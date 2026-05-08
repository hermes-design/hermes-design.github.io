import numpy as np
import matplotlib.pyplot as plt
import os

# --- CONFIGURATION ---
# Noms des fichiers générés par GNU Radio
FICHIER_PROPRE = 'attacker/signal_propre.bin'
FICHIER_BROUILLE = 'attacker/signal_brouille.bin'
FICHIER_DEFENSE = 'defender/defended_power.bin'

# Fréquence d'échantillonnage des fichiers (10 Hz après vos blocs Keep 1 in N)
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

# 1. Chargement des données
print("Chargement des fichiers binaires...")
propre = charger_donnees(FICHIER_PROPRE)
brouille = charger_donnees(FICHIER_BROUILLE)
defense = charger_donnees(FICHIER_DEFENSE)

# 2. Synchronisation et nettoyage
if propre is not None and brouille is not None and defense is not None:
    # On aligne sur la taille du fichier le plus petit
    taille_min = min(len(propre), len(brouille), len(defense))
    propre = propre[:taille_min]
    brouille = brouille[:taille_min]
    defense = defense[:taille_min]
    
    # Axe du temps
    temps = np.arange(taille_min) / FREQ_MESURE

    # 3. Calculs des KPIs
    # Gain de récupération en dB (Efficacité du nettoyage)
    gain_db = 10 * np.log10((defense + EPSILON) / (brouille + EPSILON))
    
    # Pourcentage de restauration (Signal défendu vs Signal original)
    # 100% signifie que le Defender a parfaitement récupéré le flux satellite
    taux_restauration = (defense / (propre + EPSILON)) * 100
    taux_restauration = np.clip(taux_restauration, 0, 100) # Plafonné à 100%

    # 4. Visualisation
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), sharex=True)

    # Graphique du haut : Puissances en dB
    ax1.plot(temps, 10 * np.log10(propre + EPSILON), label='Satellite (Référence)', color='green', alpha=0.8)
    ax1.plot(temps, 10 * np.log10(brouille + EPSILON), label='Signal Brouillé (Attaque)', color='red', alpha=0.5)
    ax1.plot(temps, 10 * np.log10(defense + EPSILON), label='Signal Défendu (Défense)', color='blue', linewidth=1.5)
    ax1.set_ylabel('Puissance (dB)')
    ax1.set_title('Analyse de la Fiabilité du Signal : Satellite vs Attaque vs Défense')
    ax1.legend(loc='upper right')
    ax1.grid(True, linestyle='--')

    # Graphique du bas : Pourcentage de réussite
    ax2.fill_between(temps, taux_restauration, color='skyblue', alpha=0.3)
    ax2.plot(temps, taux_restauration, color='navy', label='Taux de Restauration (%)')
    ax2.axhline(y=np.mean(taux_restauration), color='orange', linestyle='--', 
                label=f'Moyenne : {np.mean(taux_restauration):.2f}%')
    ax2.set_ylabel('Efficacité (%)')
    ax2.set_xlabel('Temps (secondes)')
    ax2.set_ylim(0, 110)
    ax2.set_title('Qualité du Signal Restauré par le Defender')
    ax2.legend(loc='lower right')
    ax2.grid(True, linestyle='--')

    plt.tight_layout()
    
    # 5. Affichage des résultats numériques pour le rapport
    print("\n--- RÉSULTATS DE LA SIMULATION ---")
    print(f"Points analysés : {taille_min}")
    print(f"Gain de récupération moyen : {np.mean(gain_db):.2f} dB")
    print(f"Taux de restauration moyen : {np.mean(taux_restauration):.2f} %")
    print(f"Performance maximale : {np.max(taux_restauration):.2f} %")
    
    plt.show()

else:
    print("\nImpossible d'exécuter l'analyse. Vérifiez que les fichiers .bin sont générés.")
