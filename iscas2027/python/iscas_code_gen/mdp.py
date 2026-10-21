#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extraction de la FIABILITE de la defense IA, en boucle fermee sur le banc GNU Radio,
pour alimenter un modele PRISM (model checking de la composition satellite + defense).

Principe :
  - On balaye une GRILLE (angle x puissance) d'etats d'attaque.
  - Pour chaque cellule, l'IA lit l'environnement, predit les poids, les APPLIQUE
    au Defender (boucle fermee reelle), et on MESURE le SINR effectivement obtenu.
  - On repete N_REPEAT fois par cellule pour une statistique.
  - On enregistre le SINR brut -> on derive la fiabilite pour PLUSIEURS seuils.

Sorties :
  - reliability_raw.csv      : une ligne par essai (angle, puissance, SINR IA, SINR opt, ecart)
  - reliability_grid.csv     : par cellule, moyennes + p(succes) pour chaque seuil
  - prism_reliability.csv    : format compact pret pour PRISM (etat -> proba)

Coherent avec le modele actuel : 19 features, 2 sorties (w2), scaler.pkl.
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
# 1. CONFIGURATION
# ==========================================
# Grille d'etats d'attaque (discretisation pour PRISM)
ANGLE_GRID = list(range(-80, 81, 20))        # -80, -60, ..., 80  (9 valeurs)
POWER_GRID = list(range(-25, 1, 5))          # -25, -20, ..., 0   (6 valeurs)
N_REPEAT = 10                                 # essais par cellule (statistique)

# Seuils de succes (dB) : on derive une fiabilite par seuil
SINR_THRESHOLDS = [5.0, 10.0, 15.0]
GAP_THRESHOLD = 3.0                           # succes "proche optimal" si ecart < 3 dB

SETTLING = 0.3                                # stabilisation apres application des poids

# Echelles physiques pour le SINR calcule (memes que l'evaluation)
P_SAT_DB, P_NOISE_DB = -15.0, -30.0


# ==========================================
# 2. MODELE (identique a l'entrainement)
# ==========================================
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


def optimal_w2(angle_deg):
    phi = math.pi * math.sin(math.radians(angle_deg))
    return -cmath.exp(-1j * phi)


def sinr_from_weights(w2r, w2i, angle_deg, p_jam_db):
    """SINR post-nulling avec plancher de bruit realiste (borne le nulling profond)."""
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
    # Plancher pour eviter log10(0) : si le signal utile est annule (sig~0),
    # le SINR est tres bas (signal perdu) — cas physique reel a certains angles.
    ratio = sig / (interf + noise)
    return 10 * math.log10(max(ratio, 1e-12))


# ==========================================
# 3. CHARGEMENT IA + SCALER
# ==========================================
print("Chargement du modele et du scaler...")
model = SpatialNullingMLP(input_size=19)
model.load_state_dict(torch.load('spatial_nulling_mlp.pth'))
model.eval()
scaler = joblib.load('scaler.pkl')            # MEME normalisation qu'a l'entrainement

FEATURES = ['RSSI'] + [f'PSD_{i}' for i in range(16)] + ['XCORR_RE', 'XCORR_IM']


def read_features(tb_defender):
    """Lit les 19 features depuis les probes, avec normalisation XCORR (coherence)."""
    rssi = tb_defender.probe_rssi.level()
    psd = list(tb_defender.probe_psd.level())
    xr = tb_defender.probe_xcorr_re.level()
    xi = tb_defender.probe_xcorr_im.level()
    x1p = tb_defender.probe_x1_pow.level()
    x2p = tb_defender.probe_x2_pow.level()
    if len(psd) != 16:
        return None
    denom = math.sqrt(max(x1p, 1e-20) * max(x2p, 1e-20)) + 1e-20
    xr_n, xi_n = xr / denom, xi / denom
    # ecretage cercle unite (comme a l'entrainement)
    mag = math.hypot(xr_n, xi_n)
    if mag > 1.0:
        xr_n, xi_n = xr_n / mag, xi_n / mag
    return [rssi] + psd + [xr_n, xi_n]


# ==========================================
# 4. LANCEMENT DU BANC
# ==========================================
print("Demarrage des jumeaux numeriques GNU Radio...")
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

print(f"Balayage de la grille : {len(ANGLE_GRID)} angles x {len(POWER_GRID)} puissances "
      f"x {N_REPEAT} essais = {total} tests.\n")

try:
    for angle in ANGLE_GRID:
        for p_jam in POWER_GRID:
            # Conditions d'attaque
            tb_attacker.set_jam_power(float(p_jam))
            tb_defender.set_jam_angle(float(angle))

            for rep in range(N_REPEAT):
                time.sleep(SETTLING)

                # A. L'IA lit l'environnement
                feats = read_features(tb_defender)
                if feats is None:
                    continue

                # B. Prediction des poids
                X = scaler.transform(np.array([feats]))
                with torch.no_grad():
                    w2r, w2i = model(torch.tensor(X, dtype=torch.float32)).numpy()[0]

                # C. Application EN BOUCLE FERMEE au Defender
                tb_defender.set_w1_r(1.0)
                tb_defender.set_w1_i(0.0)
                tb_defender.set_w2_r(float(w2r))
                tb_defender.set_w2_i(float(w2i))
                time.sleep(SETTLING)   # laisse le nulling s'appliquer

                # D. Mesure : SINR obtenu par l'IA vs SINR optimal
                sinr_ia = sinr_from_weights(w2r, w2i, angle, p_jam)
                w2o = optimal_w2(angle)
                sinr_opt = sinr_from_weights(w2o.real, w2o.imag, angle, p_jam)

                records.append({
                    'angle': angle, 'p_jam': p_jam, 'rep': rep,
                    'w2_r_ia': w2r, 'w2_i_ia': w2i,
                    'SINR_IA': sinr_ia, 'SINR_OPT': sinr_opt,
                    'gap': abs(sinr_opt - sinr_ia),
                })
                done += 1
            print(f"  angle={angle:+4d} p_jam={p_jam:+4d} : {N_REPEAT} essais "
                  f"({done}/{total})")

except KeyboardInterrupt:
    print("\nArret manuel.")
finally:
    tb_defender.stop(); tb_defender.wait()
    tb_satellite.stop(); tb_satellite.wait()
    tb_attacker.stop(); tb_attacker.wait()
    print("Banc GNU Radio arrete.")


# ==========================================
# 5. ANALYSE ET EXPORT POUR PRISM
# ==========================================
if not records:
    print("Aucun enregistrement — verifiez le banc.")
    raise SystemExit

df = pd.DataFrame(records)
df.to_csv('reliability_raw.csv', index=False)
print(f"\nreliability_raw.csv ecrit ({len(df)} essais).")

# Agregation par cellule (angle, puissance) : moyennes + p(succes) par seuil
rows = []
for (angle, p_jam), g in df.groupby(['angle', 'p_jam']):
    row = {
        'angle': angle, 'p_jam': p_jam, 'n': len(g),
        'SINR_IA_mean': g['SINR_IA'].mean(),
        'SINR_OPT_mean': g['SINR_OPT'].mean(),
        'gap_mean': g['gap'].mean(),
    }
    for thr in SINR_THRESHOLDS:
        row[f'p_success_SINR>{thr:g}'] = (g['SINR_IA'] > thr).mean()
    row[f'p_near_optimal_gap<{GAP_THRESHOLD:g}'] = (g['gap'] < GAP_THRESHOLD).mean()
    rows.append(row)

grid = pd.DataFrame(rows).sort_values(['angle', 'p_jam'])
grid.to_csv('reliability_grid.csv', index=False)
print(f"reliability_grid.csv ecrit ({len(grid)} cellules).")

# Format PRISM compact : etat (angle,puissance) -> proba de succes (seuil median)
main_thr = SINR_THRESHOLDS[len(SINR_THRESHOLDS) // 2]
prism = grid[['angle', 'p_jam', f'p_success_SINR>{main_thr:g}']].copy()
prism.columns = ['angle', 'p_jam', 'p_defense_success']
prism.to_csv('prism_reliability.csv', index=False)
print(f"prism_reliability.csv ecrit (seuil {main_thr} dB).")

# Resume
print("\n===== RESUME FIABILITE =====")
print(f"SINR IA moyen global    : {df['SINR_IA'].mean():.2f} dB")
print(f"SINR optimal moyen      : {df['SINR_OPT'].mean():.2f} dB")
print(f"Ecart moyen             : {df['gap'].mean():.2f} dB (median {df['gap'].median():.2f})")
for thr in SINR_THRESHOLDS:
    print(f"Fiabilite globale (SINR>{thr:g} dB) : {(df['SINR_IA']>thr).mean()*100:.1f}%")
print(f"Fiabilite (proche optimal, gap<{GAP_THRESHOLD:g}) : {(df['gap']<GAP_THRESHOLD).mean()*100:.1f}%")