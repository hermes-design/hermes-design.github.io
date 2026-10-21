"""Diagnostic EN DIRECT du Defender (a lancer la ou tourne GNU Radio).
Fixe un angle, laisse converger LONGTEMPS, lit les probes brutes.
Objectif : voir si les probes XCORR reagissent a l'angle SANS l'orchestrateur."""
import time, math
import satellite_advanced, attackerv, defender_spatial_recorded

tb_a = attackerv.attackerv()
tb_s = satellite_advanced.satellite_advanced()
tb_d = defender_spatial_recorded.defender_spatial_recorded()

tb_a.set_jam_power(-8.0)          # brouillage FORT et fixe
tb_a.start(); tb_s.start(); time.sleep(2.0); tb_d.start()
time.sleep(2.0)

print("angle |  xcorr_re_brut  xcorr_im_brut  x1_pow   x2_pow  | norm_re  norm_im")
for angle in [-60, -30, 0, 30, 60]:
    tb_d.set_jam_angle(float(angle))
    time.sleep(2.0)                # convergence LONGUE (pas 50ms)
    re = tb_d.probe_xcorr_re.level()
    im = tb_d.probe_xcorr_im.level()
    p1 = tb_d.probe_x1_pow.level()
    p2 = tb_d.probe_x2_pow.level()
    den = math.sqrt(max(p1,1e-20)*max(p2,1e-20))+1e-20
    print(f"{angle:+4d}  |  {re:+.5f}     {im:+.5f}    {p1:.4f}  {p2:.4f}  | {re/den:+.4f}  {im/den:+.4f}")

print()
print("ATTENDU : im_brut doit changer de SIGNE entre angle negatif et positif.")
print("Si im_brut reste ~0 partout -> le dephasage e^{jphi} n'affecte pas la correlation.")
print("Si x1_pow et x2_pow different beaucoup -> pb dans la construction des elements.")

tb_d.stop(); tb_d.wait(); tb_s.stop(); tb_s.wait(); tb_a.stop(); tb_a.wait()