#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extraction des TAUX (rates) pour un CTMC de fiabilite de la defense IA,
mesures en boucle fermee sur le banc GNU Radio, pour PRISM.

MODELE CTMC (4 etats) avec ADVERSAIRE ADAPTATIF :

          lambda_att                 mu_react
SAFE ------------------> UNDER_ATTACK --------------> DEFENDED
  ^                       |         ^                   | |
  |           delta_fail  |         |                   | |
  |                       v         |                   | |
  |                    COMPROMISED  |                   | |
  |                       |         |                   | |
  |<------ rho_recover ---+         |                   | |
  |                                 |---sigma_adapt-----+ |
  +------------------ gamma_reset ------------------------+

  Transitions :
    - lambda_att   : SAFE -> UNDER_ATTACK        (une attaque arrive)
    - mu_react     : UNDER_ATTACK -> DEFENDED    (l'IA neutralise) [MESURE]
    - delta_fail   : UNDER_ATTACK -> COMPROMISED (l'IA echoue)     [MESURE]
    - sigma_adapt  : DEFENDED -> UNDER_ATTACK    (RAFFINEMENT : le brouilleur,
                     une fois nulle, se repositionne (change d'angle) et
                     RELANCE une attaque -> retour en UNDER_ATTACK)
    - gamma_reset  : DEFENDED -> SAFE            (attaque terminee, nominal)
    - rho_recover  : COMPROMISED -> SAFE         (recuperation apres echec)

  Le systeme reste protege tant que mu_react > sigma_adapt (l'IA re-neutralise
  plus vite que l'adversaire ne se repositionne).

  - lambda_att, gamma_reset, rho_recover, sigma_adapt : parametres de scenario (PRISM)
  - mu_react, delta_fail : MESURES ICI, par etat d'attaque (angle, puissance)
  Note : sigma_adapt n'est PAS mesure sur le banc (c'est une propriete de
  l'adversaire, pas de la defense) -> balaye en Experiment PRISM.

============================================================================
CONTRAT ENTREE / SORTIE DU MODELE IA (pour le test en boucle fermee)
============================================================================

ENTREES (19 features) -- vecteur lu depuis les sondes du Defender, dans CET
ordre exact (fonction read_features), puis normalise par scaler.pkl :

  index  nom          source (sonde GNU Radio)        description
  -----  -----------  ------------------------------  ------------------------
   0     RSSI         probe_rssi.level()              puissance recue moyenne
                                                      (|x1+x2|^2 filtre IIR)
   1..16 PSD_0..15    probe_psd.level()  (16 bins)    densite spectrale (log)
                                                      du signal somme x1+x2
   17    XCORR_RE     probe_xcorr_re / |x1||x2|       partie reelle de la
                                                      correlation croisee
                                                      NORMALISEE x1.conj(x2)
   18    XCORR_IM     probe_xcorr_im / |x1||x2|       partie imaginaire idem

  Pre-traitement applique AVANT le reseau (identique a l'entrainement) :
    a) normalisation de la correlation par sqrt(|x1|^2 * |x2|^2)  -> coherence
       (retire la dependance en puissance, ne garde que la PHASE = angle signe)
    b) ecretage cercle unite : si |XCORR| > 1, on projette sur |XCORR| = 1
    c) standardisation : X = scaler.transform(X)  (moyenne/ecart-type du train)

  Garde : si le banc PSD n'est pas complet (len != 16), l'essai est ignore.

SORTIES (2 valeurs) -- prediction directe du MLP (pas de normalisation en sortie) :

  w2_r, w2_i  : parties reelle et imaginaire du poids complexe w2 du 2e element
                d'antenne. Le 1er poids est FIXE : w1 = 1 + 0j (non predit).
                Le nulling applique est : y = w1*x1 + w2*x2.

  Actionnement sur le Defender (boucle fermee) :
    set_w1_r(1.0) ; set_w1_i(0.0)          # w1 fixe
    set_w2_r(w2_r) ; set_w2_i(w2_i)        # w2 predit par l'IA

DEROULEMENT D'UN ESSAI DE TEST (boucle fermee) :
  1. Reset defense a neutre (w2=0) + reglage de l'attaque (angle, puissance)
  2. Lecture des 19 features -> prediction (w2_r, w2_i)   [chronometre T_inference]
  3. Application des poids au Defender
  4. Attente que le SINR mesure franchisse le seuil       [chronometre T_convergence]
  5. Issue : succes (SINR > seuil avant timeout) ou echec (timeout)
============================================================================

============================================================================
ENTREES DE LA GENERATION DES TAUX (parametres de configuration)
============================================================================
Ces parametres definissent COMMENT les taux mu_react et delta_fail sont
mesures. Les modifier change les taux obtenus -> a documenter dans le papier.

  --- GRILLE D'ETATS D'ATTAQUE (discretisation pour PRISM) ---
  ANGLE_GRID = range(-80, 81, 20)   9 angles d'incidence du brouilleur (deg).
                                    Chaque angle = un etat d'attaque distinct.
                                    Pas de 20 deg ; affiner (pas=10) donne une
                                    grille plus fine mais un run plus long.
  POWER_GRID = range(-25, 1, 5)     6 puissances de brouillage (dB). De -25 dB
                                    (faible) a 0 dB (fort). En dessous de -25,
                                    l'angle est peu observable (cf. papier).
  N_REPEAT   = 10                   essais repetes par cellule (angle,puissance).
                                    Donne la STATISTIQUE : p_success et E[T_react]
                                    par etat. Plus grand = taux plus fiables mais
                                    run plus long. Total = |ANGLE|*|POWER|*N_REPEAT.

  --- CRITERE DE SUCCES (definit ce qu'est une "defense reussie") ---
  SINR_THRESHOLD = 10.0 dB          seuil de QoS. La defense REUSSIT si le SINR
                                    mesure depasse ce seuil avant le timeout.
                                    C'est le parametre le PLUS structurant :
                                    l'augmenter rend le succes plus exigeant
                                    -> mu_react baisse, delta_fail monte.
                                    Garder ctmc_rates_raw.csv permet de re-agreger
                                    avec un autre seuil sans refaire le banc.

  --- FENETRES TEMPORELLES (mesure des temps de reaction) ---
  TIMEOUT       = 2.0 s             duree max d'attente de convergence. Au-dela,
                                    l'essai est compte comme ECHEC. Borne aussi
                                    delta_fail dans les cas d'echec systematique.
  POLL          = 0.02 s            periode de scrutation du SINR pendant la
                                    convergence (resolution de T_convergence).
  SETTLE_ATTACK = 0.3 s             temps laisse a l'attaque pour s'etablir
                                    (IIR du Defender) AVANT que l'IA n'agisse.
                                    Trop court -> features non convergees.

  --- ECHELLES PHYSIQUES (pour le SINR analytique de reference) ---
  P_SAT_DB   = -15.0 dB             puissance du satellite (cf. satellite_advanced).
  P_NOISE_DB = -30.0 dB             plancher de bruit thermique. ESSENTIEL : borne
                                    le SINR (sans lui, le nulling parfait donne un
                                    SINR infini). Ne PAS mettre a une valeur trop
                                    basse (ex. -110) sous peine de SINR aberrant.

  RAPPEL DERIVATION (comment ces entrees deviennent des taux) :
    Pour chaque cellule (angle, puissance) sur N_REPEAT essais :
      p_success  = (nb essais avec SINR > SINR_THRESHOLD) / N_REPEAT
      mu_react   = 1 / moyenne(T_react)   sur les essais reussis
      delta_fail = mu_react * (1 - p_success) / p_success
    -> ecrits par cellule dans ctmc_rates_grid.csv, moyennes dans le .prism.
============================================================================

DECOMPOSITION DU TEMPS DE REACTION (argument "latence reduite" du papier) :
    T_react = T_inference + T_convergence
  - T_inference   : latence de calcul du MLP (une passe avant) -- l'avantage de l'IA
                    face aux methodes iteratives (MVDR/LMS) qui convergent en
                    centaines d'iterations.
  - T_convergence : temps physique pour que le SINR remonte au-dessus du seuil
                    apres application des poids (incompressible, commun a toutes
                    les methodes).

DERIVATION DES TAUX (risques concurrents) :
    mu_react   = 1 / E[T_react]                       (sur les essais REUSSIS)
    delta_fail = mu_react * (p_fail / p_success)      (issue concurrente)
  Ainsi mu/(mu+delta) = p_success, coherent avec le CTMC.

Sorties :
  - ctmc_rates_raw.csv   : un essai par ligne (temps, issue)
  - ctmc_rates_grid.csv  : par etat (angle,puissance) : mu_react, delta_fail, latences
  - prism_rates.csv      : format compact pour PRISM
"""

import time
import math
import cmath
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import joblib

import satellite_advanced
import attackerv
import defender_spatial_recorded


# ==========================================
# CONFIGURATION
# ==========================================
ANGLE_GRID = list(range(-80, 81, 20))       # 9 angles
POWER_GRID = list(range(-25, 1, 5))         # 6 puissances
N_REPEAT = 10                                # essais par etat

SINR_THRESHOLD = 10.0     # seuil de QoS : la defense "reussit" si SINR > ce seuil
POLL = 0.02               # pas de scrutation du SINR pendant la convergence (s)
TIMEOUT = 2.0             # au-dela, on considere que la defense a ECHOUE (s)
SETTLE_ATTACK = 0.3       # laisse l'attaque s'etablir avant de declencher l'IA

P_SAT_DB, P_NOISE_DB = -15.0, -30.0


class SpatialNullingMLP(nn.Module):
    def __init__(self, input_size=19):
        super().__init__()
        self.layers = nn.Sequential(
            nn.Linear(input_size, 64), nn.ReLU(),
            nn.Linear(64, 64), nn.ReLU(),
            nn.Linear(64, 32), nn.ReLU(),
            nn.Linear(32, 2),
        )

    def forward(self, x):
        return self.layers(x)


def sinr_from_weights(w2r, w2i, angle_deg, p_jam_db):
    P_s = 10 ** (P_SAT_DB / 10)
    P_j = 10 ** (p_jam_db / 10)
    P_n = 10 ** (P_NOISE_DB / 10)
    W = np.array([1 + 0j, complex(w2r, w2i)])
    phi = math.pi * math.sin(math.radians(angle_deg))
    V_sat = np.array([1.0, 1.0])
    V_jam = np.array([1.0, cmath.exp(1j * phi)])
    sig = P_s * abs(W @ V_sat) ** 2
    interf = P_j * abs(W @ V_jam) ** 2
    noise = P_n * (abs(W[0]) ** 2 + abs(W[1]) ** 2)
    return 10 * math.log10(max(sig / (interf + noise), 1e-12))


def optimal_w2(angle_deg):
    phi = math.pi * math.sin(math.radians(angle_deg))
    return -cmath.exp(-1j * phi)


# ==========================================
# CHARGEMENT IA
# ==========================================
print("Chargement du modele et du scaler...")
model = SpatialNullingMLP(input_size=19)
model.load_state_dict(torch.load('spatial_nulling_mlp.pth'))
model.eval()
scaler = joblib.load('scaler.pkl')


def read_features(tb_d):
    rssi = tb_d.probe_rssi.level()
    psd = list(tb_d.probe_psd.level())
    xr = tb_d.probe_xcorr_re.level()
    xi = tb_d.probe_xcorr_im.level()
    x1p = tb_d.probe_x1_pow.level()
    x2p = tb_d.probe_x2_pow.level()
    if len(psd) != 16:
        return None
    denom = math.sqrt(max(x1p, 1e-20) * max(x2p, 1e-20)) + 1e-20
    xr_n, xi_n = xr / denom, xi / denom
    mag = math.hypot(xr_n, xi_n)
    if mag > 1.0:
        xr_n, xi_n = xr_n / mag, xi_n / mag
    return [rssi] + psd + [xr_n, xi_n]


# ==========================================
# BANC
# ==========================================
print("Demarrage du banc GNU Radio...")
tb_attacker = attackerv.attackerv()
tb_satellite = satellite_advanced.satellite_advanced()
tb_defender = defender_spatial_recorded.defender_spatial_recorded()

tb_attacker.start()
tb_satellite.start()
time.sleep(1.5)
tb_defender.start()
time.sleep(1.5)

records = []
total = len(ANGLE_GRID) * len(POWER_GRID) * N_REPEAT
done = 0
print(f"Grille : {len(ANGLE_GRID)} angles x {len(POWER_GRID)} puissances "
      f"x {N_REPEAT} essais = {total} tests.\n")

try:
    for angle in ANGLE_GRID:
        for p_jam in POWER_GRID:
            for rep in range(N_REPEAT):
                # --- 1. Etat UNDER_ATTACK : on remet la defense a neutre ---
                tb_defender.set_w1_r(1.0); tb_defender.set_w1_i(0.0)
                tb_defender.set_w2_r(0.0); tb_defender.set_w2_i(0.0)   # pas de nulling
                tb_attacker.set_jam_power(float(p_jam))
                tb_defender.set_jam_angle(float(angle))
                time.sleep(SETTLE_ATTACK)   # l'attaque s'etablit

                t_start = time.perf_counter()

                # --- 2. L'IA observe et decide (T_inference) ---
                feats = read_features(tb_defender)
                if feats is None:
                    continue
                t0 = time.perf_counter()
                X = scaler.transform(np.array([feats]))
                with torch.no_grad():
                    w2r, w2i = model(torch.tensor(X, dtype=torch.float32)).numpy()[0]
                t_inference = time.perf_counter() - t0     # LATENCE DE CALCUL IA

                # --- 3. Application des poids (actionnement) ---
                tb_defender.set_w2_r(float(w2r))
                tb_defender.set_w2_i(float(w2i))

                # --- 4. Convergence physique : on attend que le SINR MESURE
                #        par le Defender passe le seuil. On lit la sonde reelle
                #        (elle evolue pendant que les IIR convergent), et non un
                #        recalcul analytique qui serait constant.
                t1 = time.perf_counter()
                success = False
                t_convergence = None
                while time.perf_counter() - t1 < TIMEOUT:
                    try:
                        sinr_now = tb_defender.get_measured_sinr_db()
                    except Exception:
                        sinr_now = -999.0
                    if sinr_now > SINR_THRESHOLD:
                        t_convergence = time.perf_counter() - t1
                        success = True
                        break
                    time.sleep(POLL)
                if not success:
                    t_convergence = TIMEOUT      # echec : timeout

                t_react = t_inference + t_convergence

                # SINR final : mesure par le banc (reference physique) + calcul analytique
                try:
                    sinr_measured = tb_defender.get_measured_sinr_db()
                except Exception:
                    sinr_measured = float('nan')
                sinr_ia = sinr_from_weights(w2r, w2i, angle, p_jam)
                w2o = optimal_w2(angle)
                sinr_opt = sinr_from_weights(w2o.real, w2o.imag, angle, p_jam)

                records.append({
                    'angle': angle, 'p_jam': p_jam, 'rep': rep,
                    'success': int(success),
                    'T_inference': t_inference,
                    'T_convergence': t_convergence,
                    'T_react': t_react,
                    'SINR_measured': sinr_measured,
                    'SINR_IA': sinr_ia, 'SINR_OPT': sinr_opt,
                    'gap': abs(sinr_opt - sinr_ia),
                })
                done += 1
            print(f"  angle={angle:+4d} p_jam={p_jam:+4d} ({done}/{total})")

except KeyboardInterrupt:
    print("\nArret manuel.")
finally:
    tb_defender.stop(); tb_defender.wait()
    tb_satellite.stop(); tb_satellite.wait()
    tb_attacker.stop(); tb_attacker.wait()
    print("Banc arrete.")


# ==========================================
# DERIVATION DES TAUX CTMC
# ==========================================
if not records:
    print("Aucun enregistrement.")
    raise SystemExit

df = pd.DataFrame(records)
df.to_csv('ctmc_rates_raw.csv', index=False)
print(f"\nctmc_rates_raw.csv ecrit ({len(df)} essais).")

rows = []
for (angle, p_jam), g in df.groupby(['angle', 'p_jam']):
    n = len(g)
    n_succ = int(g['success'].sum())
    p_succ = n_succ / n if n else 0.0
    p_fail = 1.0 - p_succ

    # mu_react = 1 / E[T_react] sur les essais REUSSIS
    if n_succ > 0:
        mean_treact = g.loc[g['success'] == 1, 'T_react'].mean()
        mu_react = 1.0 / mean_treact if mean_treact > 0 else 0.0
    else:
        mean_treact = float('nan')
        mu_react = 0.0

    # delta_fail : issue concurrente -> mu/(mu+delta) = p_succ
    if p_succ > 0 and p_fail > 0:
        delta_fail = mu_react * (p_fail / p_succ)
    elif p_succ == 0:
        # echec systematique : taux d'echec = 1/timeout (borne)
        delta_fail = 1.0 / TIMEOUT
    else:
        delta_fail = 0.0     # succes systematique

    rows.append({
        'angle': angle, 'p_jam': p_jam, 'n': n,
        'p_success': p_succ,
        'mu_react': mu_react,            # taux de neutralisation (s^-1)
        'delta_fail': delta_fail,        # taux d'echec (s^-1)
        'T_react_mean': mean_treact,
        'T_inference_mean': g['T_inference'].mean(),
        'T_convergence_mean': g['T_convergence'].mean(),
        'SINR_IA_mean': g['SINR_IA'].mean(),
        'SINR_OPT_mean': g['SINR_OPT'].mean(),
        'gap_mean': g['gap'].mean(),
    })

grid = pd.DataFrame(rows).sort_values(['angle', 'p_jam'])
grid.to_csv('ctmc_rates_grid.csv', index=False)
print(f"ctmc_rates_grid.csv ecrit ({len(grid)} etats).")

# Format PRISM compact
prism = grid[['angle', 'p_jam', 'mu_react', 'delta_fail', 'p_success']].copy()
prism.to_csv('prism_rates.csv', index=False)
print("prism_rates.csv ecrit.")

# ==========================================
# RESUME (chiffres pour le papier)
# ==========================================
succ = df[df['success'] == 1]
print("\n===== TAUX CTMC (agreges) =====")
print(f"Fiabilite globale (SINR > {SINR_THRESHOLD:g} dB) : {df['success'].mean()*100:.1f}%")
if len(succ):
    print(f"T_inference moyen   : {succ['T_inference'].mean()*1000:.2f} ms   <-- latence IA")
    print(f"T_convergence moyen : {succ['T_convergence'].mean()*1000:.2f} ms   <-- physique")
    print(f"T_react moyen       : {succ['T_react'].mean()*1000:.2f} ms")
    print(f"mu_react global     : {1.0/succ['T_react'].mean():.2f} s^-1")
p_s = df['success'].mean()
if 0 < p_s < 1 and len(succ):
    mu_g = 1.0 / succ['T_react'].mean()
    print(f"delta_fail global   : {mu_g*(1-p_s)/p_s:.2f} s^-1")
print(f"\nEcart SINR IA<->optimal : {df['gap'].mean():.2f} dB (median {df['gap'].median():.2f})")
print("\nArgument papier : T_inference (une passe MLP) vs methodes iteratives")
print("(MVDR/LMS) qui necessitent des centaines d'iterations -> latence reduite.")