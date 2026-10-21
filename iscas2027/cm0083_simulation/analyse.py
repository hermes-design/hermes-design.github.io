import numpy as np
import matplotlib.pyplot as plt
import os


FICHIER_PROPRE = 'attacker/signal_propre.bin'
FICHIER_BROUILLE = 'attacker/signal_brouille.bin'
FICHIER_DEFENSE = 'defender/defended_power.bin'


FREQ_MESURE = 10.0 
EPSILON = 1e-12  # Évite les divisions par zéro

def charger_donnees(nom_fichier):
    if not os.path.exists(nom_fichier):
        print(f"Erreur : '{nom_fichier}' introuvable.")
        return None
    data = np.fromfile(nom_fichier, dtype=np.float32)
    if len(data) == 0:
        print(f"Erreur : '{nom_fichier}' est vide.")
        return None
    return data


print("Chargement des fichiers binaires...")
propre = charger_donnees(FICHIER_PROPRE)
brouille = charger_donnees(FICHIER_BROUILLE)
defense = charger_donnees(FICHIER_DEFENSE)


if propre is not None and brouille is not None and defense is not None:

    taille_min = min(len(propre), len(brouille), len(defense))
    propre = propre[:taille_min]
    brouille = brouille[:taille_min]
    defense = defense[:taille_min]
    

    temps = np.arange(taille_min) / FREQ_MESURE


    gain_db = 10 * np.log10((defense + EPSILON) / (brouille + EPSILON))
    
 
    taux_restauration = (defense / (propre + EPSILON)) * 100
    taux_restauration = np.clip(taux_restauration, 0, 100) # Plafonné à 100%

    # 4. Visualisation
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), sharex=True)
    # Powers in dB
    ax1.plot(temps, 10 * np.log10(propre + EPSILON), label='Satellite (Reference)', color='green', alpha=0.8)
    ax1.plot(temps, 10 * np.log10(brouille + EPSILON), label='Jamming Signal (Attack)', color='red', alpha=0.5)
    ax1.plot(temps, 10 * np.log10(defense + EPSILON), label='Mitigated Signal (Defense)', color='blue', linewidth=1.5)
    ax1.set_ylabel('Power (dB)')
    ax1.set_title('Signal Reliability Analysis: Satellite vs Attack vs Defense')
    ax1.legend(loc='upper right')
    ax1.grid(True, linestyle='--')

    # Success rate
    ax2.fill_between(temps, taux_restauration, color='skyblue', alpha=0.3)
    ax2.plot(temps, taux_restauration, color='navy', label='Restoration Rate (%)')
    ax2.axhline(y=np.mean(taux_restauration), color='orange', linestyle='--', 
                label=f'Mean: {np.mean(taux_restauration):.2f}%')
    ax2.set_ylabel('Efficiency (%)')
    ax2.set_xlabel('Time (seconds)')
    ax2.set_ylim(0, 110)
    ax2.set_title('Quality of Signal Restored by Defender')
    ax2.legend(loc='lower right')
    ax2.grid(True, linestyle='--')

    plt.tight_layout()
    
    # 5. Display results
    print("\n--- SIMULATION RESULTS ---")
    print(f"Analyzed points: {taille_min}")
    print(f"Mean recovery gain: {np.mean(gain_db):.2f} dB")
    print(f"Mean restoration rate: {np.mean(taux_restauration):.2f} %")
    
    plt.show()

else:
    print("\nAnalysis failed. Please verify that the .bin files have been generated.")
