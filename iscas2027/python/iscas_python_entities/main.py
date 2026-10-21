import time
import math
import cmath
import numpy as np
import pandas as pd
import signal
import sys

# Importation des trois flowgraphs
import satellite_advanced
import attackerv
import defender_spatial_recorded

# ==========================================
# 1. CONFIGURATION DES DEUX PHASES
# ==========================================
# Chaque phase produit son propre CSV, dans une seule session GNU Radio.
PHASES = [
    {
        'name': 'train',
        'num': 5000,
        'csv': 'iscas_dataset_spatial_nulling.csv',
        'p_jam_range': (-25, -5),
        'angle_range': (-90, 90),
    },
    {
        'name': 'test',
        'num': 1000,
        'csv': 'test_set.csv',
        'p_jam_range': (-25, 0),
        'angle_range': (-85, 85),
    },
]

SETTLING_TIME = 0.15   # garde-fou (IIR acceleres alpha=0.4)
WARMUP_TIME = 1.0      # etablissement du reseau ZMQ / remplissage des probes
# Attente ADAPTATIVE : on lit la correlation jusqu'a stabilisation, plutot que
# de parier sur un delai fixe (le debit reel des probes varie selon la machine).
STABILIZE_MAX_WAIT = 0.5   # temps max d'attente de convergence (s)
STABILIZE_TOL = 1e-3       # variation relative consideree comme "stabilise"
STABILIZE_POLL = 0.05      # intervalle entre deux lectures (s)
CHECKPOINT_EVERY = 1000


def save_checkpoint(data, filename):
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False)
    print(f"[save] {len(data)} echantillons -> {filename}")


def calculate_optimal_weights(theta_deg):
    """Verite terrain : poids de nulling analytiques pour un angle donne.
    Convention alignee avec le combineur en SOMME du Defender (w1*x1 + w2*x2)
    et le satellite au boresight (V_sat = [1, 1])."""
    delta_phi = math.pi * math.sin(math.radians(theta_deg))
    w1 = complex(1.0, 0.0)
    w2 = -cmath.exp(-1j * delta_phi)   # place un zero dans la direction du brouilleur
    return w1, w2


def wait_until_stable(tb_defender):
    """Attend que la correlation croisee se stabilise (convergence des IIR),
    au lieu d'un delai fixe. Retourne quand la variation relative de |xcorr|
    passe sous STABILIZE_TOL, ou quand STABILIZE_MAX_WAIT est atteint."""
    t0 = time.time()
    prev = None
    while time.time() - t0 < STABILIZE_MAX_WAIT:
        time.sleep(STABILIZE_POLL)
        try:
            re = tb_defender.probe_xcorr_re.level()
            im = tb_defender.probe_xcorr_im.level()
        except Exception:
            continue
        cur = math.hypot(re, im)
        if prev is not None:
            denom = max(abs(prev), 1e-6)
            if abs(cur - prev) / denom < STABILIZE_TOL:
                return          # stabilise
        prev = cur
    return                      # timeout : on prend l'etat courant


def run_phase(phase, tb_attacker, tb_defender):
    """Collecte un dataset pour une phase (train ou test) sur l'ecosysteme deja demarre."""
    name = phase['name']
    num = phase['num']
    csv = phase['csv']
    p_lo, p_hi = phase['p_jam_range']
    a_lo, a_hi = phase['angle_range']

    print(f"\n========== PHASE {name.upper()} : {num} echantillons -> {csv} ==========")
    dataset = []
    skipped = 0

    for i in range(num):
        p_jam = np.random.uniform(p_lo, p_hi)
        angle = np.random.uniform(a_lo, a_hi)

        # 1) Conditions d'attaque
        tb_attacker.set_jam_power(float(p_jam))
        tb_defender.set_jam_angle(float(angle))

        # 2) Poids optimaux (verite terrain) appliques au Defender pour la mesure SINR
        w1_opt, w2_opt = calculate_optimal_weights(angle)
        tb_defender.set_w1_r(float(w1_opt.real))
        tb_defender.set_w1_i(float(w1_opt.imag))
        tb_defender.set_w2_r(float(w2_opt.real))
        tb_defender.set_w2_i(float(w2_opt.imag))

        # 3) Stabilisation (garde-fou fixe + attente adaptative de convergence)
        time.sleep(SETTLING_TIME)
        wait_until_stable(tb_defender)

        # 4) Lecture des capteurs avec gardes
        try:
            rssi = tb_defender.probe_rssi.level()
            psd_vector = list(tb_defender.probe_psd.level())
            xcorr_re = tb_defender.probe_xcorr_re.level()
            xcorr_im = tb_defender.probe_xcorr_im.level()
            x1_pow = tb_defender.probe_x1_pow.level()
            x2_pow = tb_defender.probe_x2_pow.level()
            ber = tb_defender.probe_ber.level()
            sinr = tb_defender.get_measured_sinr_db()   # SINR MESURE
        except Exception:
            skipped += 1
            continue

        # Garde : le banc PSD (somme) doit etre complet
        if len(psd_vector) != 16:
            skipped += 1
            continue

        record = {
            'Iteration': i, 'Jam_Angle_True': angle, 'Jam_Power': p_jam,
            'RSSI': rssi, 'BER': ber, 'SINR_dB': sinr,
            'w1_r': w1_opt.real, 'w1_i': w1_opt.imag,
            'w2_r': w2_opt.real, 'w2_i': w2_opt.imag,
        }
        for idx, val in enumerate(psd_vector):
            record[f'PSD_{idx}'] = val
        # Normalisation (coherence) : retire la dependance en puissance,
        # ne garde que la PHASE = angle signe du brouilleur.
        denom = math.sqrt(max(x1_pow, 1e-20) * max(x2_pow, 1e-20)) + 1e-20
        record['XCORR_RE'] = xcorr_re / denom
        record['XCORR_IM'] = xcorr_im / denom
        dataset.append(record)

        if (i + 1) % CHECKPOINT_EVERY == 0:
            save_checkpoint(dataset, csv)
            print(f"[progress:{name}] {i+1}/{num} | ignores: {skipped}")

    save_checkpoint(dataset, csv)
    print(f"[done:{name}] {len(dataset)} echantillons, {skipped} ignores.")
    return dataset


# ==========================================
# 2. INITIALISATION DE L'ECOSYSTEME (une seule fois)
# ==========================================
print("[init] lancement de l'ecosysteme GNU Radio...")
tb_attacker = attackerv.attackerv()
tb_satellite = satellite_advanced.satellite_advanced()
tb_defender = defender_spatial_recorded.defender_spatial_recorded()

try:
    tb_attacker.start()
    tb_satellite.start()
    time.sleep(WARMUP_TIME)
    tb_defender.start()
    time.sleep(WARMUP_TIME)   # laisse les probes se remplir

    # 3) Enchainement des deux phases sur la meme session
    for phase in PHASES:
        run_phase(phase, tb_attacker, tb_defender)

except KeyboardInterrupt:
    print("\n[stop] arret manuel demande.")
finally:
    print("[cleanup] arret des processus...")
    tb_defender.stop(); tb_defender.wait()
    tb_satellite.stop(); tb_satellite.wait()
    tb_attacker.stop(); tb_attacker.wait()
    print("[end] termine.")