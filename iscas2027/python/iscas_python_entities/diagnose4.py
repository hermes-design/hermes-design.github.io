import pandas as pd, numpy as np
df = pd.read_csv('iscas_dataset_spatial_nulling.csv')

mag = np.sqrt(df['XCORR_RE']**2+df['XCORR_IM']**2)
over = mag>1
df.loc[over,'XCORR_RE']/=mag[over]; df.loc[over,'XCORR_IM']/=mag[over]

print("=== SUSPECT 1 : la couche de sortie normalisee sur cercle unite ===")
# Le MLP predit (cos,sin) puis divise par la norme -> |w2|=1.
# Verifions que les LABELS sont bien sur le cercle unite.
lab_mag = np.sqrt(df['w2_r']**2 + df['w2_i']**2)
print(f"  |w2| des labels : min={lab_mag.min():.4f} mean={lab_mag.mean():.4f} max={lab_mag.max():.4f}")
print("  (doit etre ~1.0 partout ; sinon la couche cercle-unite est incoherente)")

print("\n=== SUSPECT 2 : echelle des features (le scaler doit gerer, mais verifions) ===")
feats = ['RSSI']+[f'PSD_{i}' for i in range(16)]+['XCORR_RE','XCORR_IM']
print(f"  {'feature':10s} {'mean':>10s} {'std':>10s} {'min':>8s} {'max':>8s}")
for f in ['RSSI','PSD_0','PSD_8','XCORR_RE','XCORR_IM']:
    print(f"  {f:10s} {df[f].mean():10.3f} {df[f].std():10.3f} {df[f].min():8.2f} {df[f].max():8.2f}")

print("\n=== SUSPECT 3 : un modele lineaire simple fait-il mieux que 1.03 ? ===")
# Regression lineaire directe w2 ~ features. Si elle bat le MLP, le MLP est mal regle.
from numpy.linalg import lstsq
X = df[feats].values
X = (X - X.mean(0)) / (X.std(0)+1e-9)   # standardise
X = np.hstack([X, np.ones((len(X),1))])  # biais
for lab in ['w2_r','w2_i']:
    y = df[lab].values
    coef,_,_,_ = lstsq(X, y, rcond=None)
    pred = X@coef
    mse = ((pred-y)**2).mean()
    var = y.var()
    print(f"  {lab}: MSE lineaire={mse:.3f}  (variance={var:.3f}, R2={1-mse/var:.3f})")
tot_lin = 0
for lab in ['w2_r','w2_i']:
    y=df[lab].values; coef,_,_,_=lstsq(X,y,rcond=None); tot_lin+=((X@coef-y)**2).mean()
print(f"\n  MSE lineaire totale (w2_r+w2_i) = {tot_lin:.3f}")
print(f"  Votre MLP val (MSE+physique) = 1.03")
print("  Si la reg lineaire bat deja le MLP, le MLP est mal configure (pas les donnees).")