#!/usr/bin/env python3
# -*- coding: utf-8 -*-


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


p_s = df['success'].mean()
print(f"p_success global    : {p_s:.4f}")
if len(succ):
    mu_g = 1.0 / succ['T_react'].mean()      # mu global = 1 / E[T_react] (reussis)
    print(f"T_inference moyen   : {succ['T_inference'].mean()*1000:.2f} ms   <-- latence IA")
    print(f"T_convergence moyen : {succ['T_convergence'].mean()*1000:.2f} ms   <-- physique")
    print(f"T_react moyen       : {succ['T_react'].mean()*1000:.2f} ms")
    print(f"mu_react global     : {mu_g:.4f} s^-1")
    if 0 < p_s < 1:
        delta_g = mu_g * (1 - p_s) / p_s
        print(f"delta_fail global   : {delta_g:.4f} s^-1  (= mu*(1-p)/p, coherent CTMC)")
        print(f"  verif mu/(mu+delta) = {mu_g/(mu_g+delta_g):.4f}  (doit egaler p_success)")

# Rappel : pour le .prism GLOBAL, utiliser mu_react et delta_fail ci-dessus.
# Ne PAS moyenner les colonnes delta_fail de la grille (agregation differente).
print(f"\nEcart SINR IA<->optimal : {df['gap'].mean():.2f} dB (median {df['gap'].median():.2f})")
print("\nArgument papier : T_inference (une passe MLP) vs methodes iteratives")
print("(MVDR/LMS) qui necessitent des centaines d'iterations -> latence reduite.")
