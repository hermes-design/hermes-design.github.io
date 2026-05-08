import pandas as pd


df = pd.read_csv('data.csv', skiprows=3, header=None, decimal=',', sep=None, engine='python')


attaque = pd.to_numeric(df[1], errors='coerce')
apres_defense = pd.to_numeric(df[4], errors='coerce')


df[5] = ((attaque - apres_defense) / attaque) * 100


df.columns = ['MTTI', 'Attaque_Initiale', 'alpha_1', 'alpha_5', 'alpha_10', 'Pourcentage_Defense']


moyenne_defense = df['Pourcentage_Defense'].mean()
mediane_defense = df['Pourcentage_Defense'].median()

print(f"The average defense is: {moyenne_defense:.6f}%")
print(f"The median defense is: {mediane_defense:.6f}%")


df.to_csv('resultat_final.csv', index=False)
