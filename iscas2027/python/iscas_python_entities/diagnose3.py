import pandas as pd, numpy as np, math

df = pd.read_csv('iscas_dataset_spatial_nulling.csv')

print("=== A. Correlation XCORR <-> ANGLE VRAI (pas les labels) ===")
# Si meme ca ne correle pas, la feature ne voit pas l'angle -> pb de collecte
ang = df['Jam_Angle_True'].values
phi = np.pi*np.sin(np.radians(ang))
for c in ['XCORR_RE','XCORR_IM','RSSI']:
    print(f"  {c:9s} vs angle : {abs(np.corrcoef(df[c],ang)[0,1]):.3f}"
          f"  | vs phi : {abs(np.corrcoef(df[c],phi)[0,1]):.3f}"
          f"  | vs sin(phi) : {abs(np.corrcoef(df[c],np.sin(phi))[0,1]):.3f}"
          f"  | vs cos(phi) : {abs(np.corrcoef(df[c],np.cos(phi))[0,1]):.3f}")

print("\n=== B. Ce que DEVRAIT etre XCORR normalise si tout marchait ===")
# theorie : xcorr_norm ~ (Ps + Pj*e^{-j phi})/(Ps+Pj) -- dominee par le terme e^{-j phi}
# donc XCORR_RE ~ cos(phi), XCORR_IM ~ -sin(phi)
print("  Attendu : XCORR_RE ~ cos(phi) (corr forte), XCORR_IM ~ sin(phi) (corr forte)")

print("\n=== C. Distribution des XCORR : normalisation OK ? ===")
mag = np.sqrt(df['XCORR_RE']**2 + df['XCORR_IM']**2)
print(f"  |XCORR| : min={mag.min():.3f} mean={mag.mean():.3f} max={mag.max():.3f}")
print("  (si normalise en coherence, |XCORR| devrait etre <= ~1)")
print(f"  Nb lignes |XCORR|>1.05 : {(mag>1.05).sum()} (anormal si >0)")

print("\n=== D. XCORR change-t-il de signe avec l'angle ? ===")
pos = df[df['Jam_Angle_True']>20]
neg = df[df['Jam_Angle_True']<-20]
print(f"  angle>+20 : XCORR_IM moyen = {pos['XCORR_IM'].mean():+.4f}")
print(f"  angle<-20 : XCORR_IM moyen = {neg['XCORR_IM'].mean():+.4f}")
print("  (doivent etre de SIGNES OPPOSES si la feature encode le signe)")

print("\n=== E. Correlation XCORR <-> w2, RESTREINT aux forts brouillages ===")
strong = df[df['Jam_Power']>-15]
print(f"  (sur {len(strong)} lignes avec Jam_Power > -15 dB)")
for f in ['XCORR_RE','XCORR_IM']:
    for l in ['w2_r','w2_i']:
        print(f"    {f} <-> {l} : {abs(np.corrcoef(strong[f],strong[l])[0,1]):.3f}")