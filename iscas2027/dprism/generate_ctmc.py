#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import pandas as pd
import numpy as np
import sys

CSV = 'ctmc_rates_grid.csv'

try:
    grid = pd.read_csv(CSV)
except FileNotFoundError:
    print(f"ERREUR : {CSV} introuvable. Lancez d'abord extract_ctmc_rates.py.")
    sys.exit(1)

# Nettoyage : remplacer les NaN/inf eventuels par des bornes raisonnables
grid = grid.replace([np.inf, -np.inf], np.nan)
grid['mu_react'] = grid['mu_react'].fillna(0.01)      # quasi jamais de succes
grid['delta_fail'] = grid['delta_fail'].fillna(10.0)  # echec rapide

# =========================================================
# 1. TAUX GLOBAUX (moyennes ponderees par le nb d'essais)
# =========================================================
w = grid['n'] if 'n' in grid else np.ones(len(grid))
mu_global = np.average(grid['mu_react'], weights=w)
delta_global = np.average(grid['delta_fail'], weights=w)
psucc_global = np.average(grid['p_success'], weights=w)

print("===== TAUX GLOBAUX (moyennes ponderees) =====")
print(f"  mu_react   = {mu_global:.4f} s^-1")
print(f"  delta_fail = {delta_global:.4f} s^-1")
print(f"  p_success  = {psucc_global:.4f}")
if 'T_inference_mean' in grid:
    print(f"  T_inference moyen   = {np.average(grid['T_inference_mean'], weights=w)*1000:.2f} ms")
    print(f"  T_convergence moyen = {np.average(grid['T_convergence_mean'], weights=w)*1000:.2f} ms")


# =========================================================
# 2. MODELE GLOBAL
# =========================================================
global_model = f"""// ============================================================
//  
//
//  mu_react   = {mu_global:.4f} s^-1   (moyenne ponderee, 1/T_react)
//  delta_fail = {delta_global:.4f} s^-1   (moyenne ponderee)
//  p_success  = {psucc_global:.4f}
// ============================================================

ctmc

// ---- Taux MESURES sur le banc ----
const double mu_react   = {mu_global:.4f};
const double delta_fail = {delta_global:.4f};

// ---- Parametres de scenario (a balayer en Experiment) ----
const double lambda_att  = 0.1;
const double gamma_reset = 2.0;
const double rho_recover = 0.5;
const double sigma_adapt = 3.0;    // adversaire adaptatif

// ---- ENTITE 2 : SATELLITE (plateforme) ----
// Derivation rigoureuse : lambda depuis la FIABILITE R(12ans)=88%,
// mu depuis la DISPONIBILITE A=99.5%. Reproduit les DEUX chiffres.
const double lambda_sat = 3.378e-10;  // panne satellite (MTBF ~94 ans)
const double mu_sat     = 6.722e-8;   // restauration (MTTR ~172 j : redondance/rechange)

// ---- ENTITE 3 : SIGNAL (sante du signal emis) ----
// depuis dispo signal 99.22% + recuperation 15 h.
const double lambda_sig = 1.456e-7;   // indispo signal (MTBF ~1908 h)
const double mu_sig     = 1.852e-5;   // recuperation signal (15 h)

module defense
    d : [0..3] init 0;   // 0=SAFE 1=UNDER_ATTACK 2=DEFENDED 3=COMPROMISED
    [] d=0 -> lambda_att  : (d'=1);
    [] d=1 -> mu_react    : (d'=2);
    [] d=1 -> delta_fail  : (d'=3);
    [] d=2 -> gamma_reset : (d'=0);
    [] d=2 -> sigma_adapt : (d'=1);
    [] d=3 -> rho_recover : (d'=0);
endmodule

module satellite
    sat : [0..1] init 0;   // 0=OPERATIONNEL 1=EN_PANNE
    [] sat=0 -> lambda_sat : (sat'=1);
    [] sat=1 -> mu_sat     : (sat'=0);
endmodule

module signal
    sig : [0..1] init 0;   // 0=SAIN 1=DEGRADE
    [] sig=0 -> lambda_sig : (sig'=1);
    [] sig=1 -> mu_sig     : (sig'=0);
endmodule

// Composition ET : defense protege ET satellite op ET signal sain
label "service_ok"  = (d=0 | d=2) & sat=0 & sig=0;
label "compromised" = d=3;
label "sat_down"    = sat=1;
label "signal_lost" = sig=1;
label "system_down" = (d=3) | (sat=1) | (sig=1);

rewards "time_compromised" d=3 : 1; endrewards
rewards "time_defended"    d=2 : 1; endrewards
rewards "time_service_ok"  (d=0 | d=2) & sat=0 & sig=0 : 1; endrewards
"""

open('defense_global.prism', 'w').write(global_model)
print("\n[1] defense_global.prism ecrit.")


# =========================================================
# 3. MODELE PARAMETRIQUE (taux indexes par zone via formules PRISM)
#    On encode la grille sous forme de formules : selon (idx_angle, idx_pow),
#    mu_react et delta_fail prennent la valeur mesuree de la cellule.
# =========================================================
angles = sorted(grid['angle'].unique())
powers = sorted(grid['p_jam'].unique())

# Construire des tables PRISM : mu_react[i][j] via une cascade de formules.
# PRISM ne gere pas les tableaux 2D directement -> on lineraise en un index
# k = i * len(powers) + j, et on ecrit mu_react comme une grande formule.
def build_rate_formula(name, valuecol):
    terms = []
    for i, a in enumerate(angles):
        for j, p in enumerate(powers):
            row = grid[(grid['angle'] == a) & (grid['p_jam'] == p)]
            val = float(row[valuecol].iloc[0]) if len(row) else 0.01
            k = i * len(powers) + j
            terms.append(f"    (zone={k} ? {val:.4f} : 0)")
    body = " +\n".join(terms)
    return f"{name} =\n{body};"

# Index de zone : (angle, puissance) -> k
zone_map = []
for i, a in enumerate(angles):
    for j, p in enumerate(powers):
        k = i * len(powers) + j
        zone_map.append((k, a, p))

mu_formula = build_rate_formula("mu_react", "mu_react")
delta_formula = build_rate_formula("delta_fail", "delta_fail")

n_zones = len(angles) * len(powers)

param_model = f"""// ============================================================
//  CTMC PARAMETRIQUE de la defense IA -- taux PAR ZONE (angle,puissance)
//  (genere depuis {CSV})
//
//  La constante 'zone' selectionne l'etat d'attaque (0..{n_zones-1}).
//  En Experiment PRISM : balayer zone de 0 a {n_zones-1} pour obtenir
//  la fiabilite par zone d'attaque.
//
//  Correspondance zone -> (angle, puissance) : voir rates_table.txt
// ============================================================

ctmc

// Selecteur de zone d'attaque (a balayer en Experiment : 0..{n_zones-1})
const int zone;

// Taux mesures, selectionnes par zone via formules :
formula {mu_formula}

formula {delta_formula}

// Parametres de scenario
const double lambda_att  = 0.1;
const double gamma_reset = 2.0;
const double rho_recover = 0.5;
const double sigma_adapt = 3.0;

// ENTITE 2 : SATELLITE (fiab 88%/12ans + dispo 99.5%)
const double lambda_sat = 3.378e-10;
const double mu_sat     = 6.722e-8;
// ENTITE 3 : SIGNAL (dispo 99.22% + recuperation 15 h)
const double lambda_sig = 1.456e-7;
const double mu_sig     = 1.852e-5;

module defense
    d : [0..3] init 0;
    [] d=0 -> lambda_att  : (d'=1);
    [] d=1 -> mu_react    : (d'=2);
    [] d=1 -> delta_fail  : (d'=3);
    [] d=2 -> gamma_reset : (d'=0);
    [] d=2 -> sigma_adapt : (d'=1);
    [] d=3 -> rho_recover : (d'=0);
endmodule

module satellite
    sat : [0..1] init 0;
    [] sat=0 -> lambda_sat : (sat'=1);
    [] sat=1 -> mu_sat     : (sat'=0);
endmodule

module signal
    sig : [0..1] init 0;
    [] sig=0 -> lambda_sig : (sig'=1);
    [] sig=1 -> mu_sig     : (sig'=0);
endmodule

label "service_ok"  = (d=0 | d=2) & sat=0 & sig=0;
label "compromised" = d=3;

rewards "time_compromised" d=3 : 1; endrewards
"""

open('defense_parametrique.prism', 'w').write(param_model)
print("[2] defense_parametrique.prism ecrit.")


# =========================================================
# 4. TABLE zone -> (angle, puissance) + taux (pour l'annexe)
# =========================================================
with open('rates_table.txt', 'w') as f:
    f.write("Correspondance zone -> (angle, puissance) et taux mesures\n")
    f.write("=" * 70 + "\n")
    f.write(f"{'zone':>5} {'angle':>7} {'p_jam':>7} {'mu_react':>10} "
            f"{'delta_fail':>11} {'p_success':>10}\n")
    for k, a, p in zone_map:
        row = grid[(grid['angle'] == a) & (grid['p_jam'] == p)]
        if len(row):
            mu = row['mu_react'].iloc[0]
            de = row['delta_fail'].iloc[0]
            ps = row['p_success'].iloc[0]
            f.write(f"{k:>5} {a:>7} {p:>7} {mu:>10.4f} {de:>11.4f} {ps:>10.4f}\n")
print("[3] rates_table.txt ecrit.")



print(f"\nTermine. {n_zones} zones encodees ({len(angles)} angles x {len(powers)} puissances).")
