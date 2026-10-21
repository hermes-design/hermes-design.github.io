#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Entrainement du MLP de spatial nulling.

Corrections cles par rapport a la version initiale :
  1. Le scaler est SAUVEGARDE (joblib) -> reutilise a l'identique en eval / temps reel.
  2. Le scaler est fit UNIQUEMENT sur le split train (pas de fuite de donnees).
  3. Sortie = w2 seul, projete sur le CERCLE UNITE (|w2|=1 garanti). w1 est constant (1+0j).
  4. Perte = MSE(w2) + lambda * puissance residuelle du brouilleur (loss physique).
  5. Reproductible (seed), early stopping, sauvegarde du meilleur modele.
"""

import math
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import joblib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


# ==========================================
# 0. Reproductibilite
# ==========================================
SEED = 42
np.random.seed(SEED)
torch.manual_seed(SEED)


# ==========================================
# 1. Dataset PyTorch
# ==========================================
class SpatialNullingDataset(Dataset):
    """Retourne (features, target_w2, phi).
    target_w2 = (w2_r, w2_i) ; phi sert a la perte physique de nulling."""
    def __init__(self, X, w2, phi):
        self.X = torch.tensor(X, dtype=torch.float32)
        self.w2 = torch.tensor(w2, dtype=torch.float32)
        self.phi = torch.tensor(phi, dtype=torch.float32).unsqueeze(1)

    def __len__(self):
        return len(self.X)

    def __getitem__(self, idx):
        return self.X[idx], self.w2[idx], self.phi[idx]


# ==========================================
# 2. Architecture du MLP
#    Sortie brute (cos, sin) -> normalisee sur le cercle unite dans forward().
#    Ainsi |w2| = 1 par construction : toute prediction est physiquement valide.
# ==========================================
class SpatialNullingMLP(nn.Module):
    def __init__(self, input_size=19):
        super().__init__()
        self.layers = nn.Sequential(
            nn.Linear(input_size, 64), nn.ReLU(),
            nn.Linear(64, 64), nn.ReLU(),
            nn.Linear(64, 32), nn.ReLU(),
            nn.Linear(32, 2),          # (cos, sin) bruts
        )

    def forward(self, x):
        return self.layers(x)          # predit (w2_r, w2_i) directement, sans normalisation dure


# ==========================================
# 3. Perte hybride : MSE(w2) + lambda * residu de brouilleur
#    Residu = |w1 + w2 * e^{j phi}|^2 avec w1 = 1+0j.
#    Le reseau optimise donc le NULLING reel, pas seulement la proximite des poids.
# ==========================================
class HybridLoss(nn.Module):
    """MSE simple sur w2 + penalite DOUCE vers |w2|=1 (ponderation faible).
    On a retire la normalisation dure en sortie et le terme physique dominant :
    ils rendaient la surface d'optimisation trop difficile (le MLP se faisait
    battre par une regression lineaire). Ici la MSE mene, la contrainte |w2|=1
    est un simple rappel doux."""
    def __init__(self, lambda_unit=0.05):
        super().__init__()
        self.mse = nn.MSELoss()
        self.lam = lambda_unit

    def forward(self, w2_pred, w2_true, phi):
        unit = ((w2_pred[:,0]**2 + w2_pred[:,1]**2) - 1.0)**2  # (|w2|^2 - 1)^2
        return self.mse(w2_pred, w2_true) + self.lam * unit.mean()


# ==========================================
# 4. Preparation des donnees (scaler fit sur TRAIN uniquement)
# ==========================================
def prepare_data(csv_file, scaler_out='scaler.pkl'):
    print(f"Chargement des donnees depuis {csv_file}...")
    df = pd.read_csv(csv_file)

    # Ecretage des correlations aberrantes : la coherence normalisee est bornee
    # a 1 en theorie ; quelques echantillons depassent legerement (IIR de
    # puissance pas tout a fait converges au settling court). On borne le module
    # a 1 pour ne pas perturber le scaler et l'entrainement.
    import numpy as _np
    mag = _np.sqrt(df['XCORR_RE']**2 + df['XCORR_IM']**2)
    over = mag > 1.0
    if over.any():
        df.loc[over, 'XCORR_RE'] = df.loc[over, 'XCORR_RE'] / mag[over]
        df.loc[over, 'XCORR_IM'] = df.loc[over, 'XCORR_IM'] / mag[over]
        print(f"  {int(over.sum())} echantillons XCORR ecretes a |1|.")

    feature_cols = (['RSSI']
                    + [f'PSD_{i}' for i in range(16)]
                    + ['XCORR_RE', 'XCORR_IM'])  # 19 features ; XCORR_* portent le signe de l'angle
    X = df[feature_cols].values
    w2 = df[['w2_r', 'w2_i']].values          # on ne predit que w2

    # phi reconstruit depuis l'angle vrai (pour la perte physique)
    phi = np.pi * np.sin(np.radians(df['Jam_Angle_True'].values))

    # Split AVANT normalisation, pour fit le scaler sur le train seul
    Xtr, Xte, w2tr, w2te, phitr, phite = train_test_split(
        X, w2, phi, test_size=0.2, random_state=SEED)

    scaler = StandardScaler().fit(Xtr)         # fit sur TRAIN uniquement
    Xtr = scaler.transform(Xtr)
    Xte = scaler.transform(Xte)

    joblib.dump(scaler, scaler_out)            # <-- sauvegarde pour eval / temps reel
    print(f"Scaler sauvegarde sous '{scaler_out}'")

    return Xtr, Xte, w2tr, w2te, phitr, phite


# ==========================================
# 5. Boucle d'entrainement (early stopping + meilleur modele)
# ==========================================
def train_model(csv_filename='iscas_dataset_spatial_nulling.csv',
                epochs=200, batch_size=64, lr=1e-3,
                patience=20,
                model_out='spatial_nulling_mlp.pth'):
    try:
        Xtr, Xte, w2tr, w2te, phitr, phite = prepare_data(csv_filename)
    except FileNotFoundError:
        print(f"Erreur : fichier '{csv_filename}' introuvable.")
        return

    train_loader = DataLoader(SpatialNullingDataset(Xtr, w2tr, phitr),
                              batch_size=batch_size, shuffle=True)
    test_loader = DataLoader(SpatialNullingDataset(Xte, w2te, phite),
                             batch_size=batch_size, shuffle=False)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = SpatialNullingMLP(input_size=19).to(device)
    print(f"Entrainement sur : {device}")

    criterion = HybridLoss(lambda_unit=0.05)
    optimizer = optim.Adam(model.parameters(), lr=lr, weight_decay=1e-4)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, 'min', factor=0.5, patience=8)

    train_losses, val_losses = [], []
    best_val, best_state, epochs_no_improve = float('inf'), None, 0

    print("Debut de l'entrainement...")
    for epoch in range(epochs):
        model.train()
        running = 0.0
        for X, w2, phi in train_loader:
            X, w2, phi = X.to(device), w2.to(device), phi.to(device)
            optimizer.zero_grad()
            loss = criterion(model(X), w2, phi)
            loss.backward()
            optimizer.step()
            running += loss.item()
        avg_train = running / len(train_loader)
        train_losses.append(avg_train)

        model.eval()
        vloss = 0.0
        with torch.no_grad():
            for X, w2, phi in test_loader:
                X, w2, phi = X.to(device), w2.to(device), phi.to(device)
                vloss += criterion(model(X), w2, phi).item()
        avg_val = vloss / len(test_loader)
        val_losses.append(avg_val)
        scheduler.step(avg_val)

        # Early stopping sur la meilleure val loss
        if avg_val < best_val - 1e-6:
            best_val = avg_val
            best_state = {k: v.cpu().clone() for k, v in model.state_dict().items()}
            epochs_no_improve = 0
        else:
            epochs_no_improve += 1

        if (epoch + 1) % 10 == 0:
            print(f"Epoch [{epoch+1}/{epochs}] | Train {avg_train:.6f} | Val {avg_val:.6f} "
                  f"| best {best_val:.6f}")

        if epochs_no_improve >= patience:
            print(f"Early stopping a l'epoch {epoch+1} (pas d'amelioration depuis {patience}).")
            break

    # Restaurer et sauvegarder le meilleur modele
    if best_state is not None:
        model.load_state_dict(best_state)
    torch.save(model.state_dict(), model_out)
    print(f"Meilleur modele (val={best_val:.6f}) sauvegarde sous '{model_out}'")

    # Courbe d'apprentissage
    plt.figure(figsize=(10, 5))
    plt.plot(train_losses, label="Train Loss")
    plt.plot(val_losses, label="Val Loss")
    plt.xlabel("Epoques"); plt.ylabel("Loss (MSE + physique)")
    plt.title("Courbe d'apprentissage du MLP (Spatial Nulling)")
    plt.legend(); plt.grid(True)
    plt.savefig("training_curve.png", dpi=120)
    print("Courbe d'apprentissage sauvegardee sous 'training_curve.png'")


if __name__ == '__main__':
    train_model()