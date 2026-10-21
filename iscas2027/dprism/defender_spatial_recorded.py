#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Defender Recorded (Repair Rate Test)
# GNU Radio version: 3.10.1.1

from gnuradio import blocks
from gnuradio import digital
from gnuradio import fec
from gnuradio import filter
from gnuradio import gr
from gnuradio.filter import firdes
from gnuradio.fft import window
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio import zeromq
from gnuradio.fft import logpwrfft
import math, cmath




class defender_spatial_recorded(gr.top_block):

    def __init__(self):
        gr.top_block.__init__(self, "Defender Recorded (Repair Rate Test)", catch_exceptions=True)

        ##################################################
        # Variables
        ##################################################
        self.jam_angle = jam_angle = 0
        self.w2_r = w2_r = 1
        self.w2_i = w2_i = 0
        self.w1_r = w1_r = 1.0
        self.w1_i = w1_i = 0
        self.samp_rate = samp_rate = 1023000
        # Dephasage du BROUILLEUR entre les deux elements d'antenne.
        # Le satellite est au boresight (0 deg) -> dephasage satellite nul,
        # donc seul le brouilleur est dephase entre element 1 et element 2.
        self.delta_phi = delta_phi = math.pi * math.sin(math.radians(jam_angle))
        # Constante de temps du filtre RSSI (0.1 : converge en ~10 echantillons
        # de sortie, compatible avec le settling time de 50 ms de l'orchestrateur).
        self.rssi_alpha = rssi_alpha = 0.4

        ##################################################
        # Blocks
        ##################################################
        self.zeromq_sub_source_1 = zeromq.sub_source(gr.sizeof_char, 1, 'tcp://127.0.0.1:5557', 100, False, -1, '')
        self.zeromq_sub_source_1.set_block_alias("Satelitte_def")
        self.zeromq_sub_source_0 = zeromq.sub_source(gr.sizeof_gr_complex, 1, 'tcp://127.0.0.1:5556', 100, False, -1, '')
        self.zeromq_sub_source_0.set_block_alias("Attacker")
        self.zeromq_sub_source = zeromq.sub_source(gr.sizeof_gr_complex, 1, 'tcp://127.0.0.1:5555', 100, False, -1, '')
        self.zeromq_sub_source.set_block_alias("Satelitte")

        # --- Capteurs (features MLP) ---
        self.single_pole_iir_filter_xx_0 = filter.single_pole_iir_filter_ff(rssi_alpha, 1)
        self.probe_rssi = blocks.probe_signal_f()
        self.probe_psd = blocks.probe_signal_vf(16)
        self.probe_ber = blocks.probe_signal_f()
        self.logpwrfft_x_0 = logpwrfft.logpwrfft_c(
            sample_rate=samp_rate,
            fft_size=16,
            ref_scale=2,
            frame_rate=30,
            avg_alpha=1.0,
            average=False,
            shift=False)
        # --- Correlation croisee NORMALISEE (coherence) ---
        # brute = moyenne(x1 * conj(x2)) ; on la divise par sqrt(<|x1|^2><|x2|^2>).
        # La normalisation retire la dependance en PUISSANCE et ne garde que la
        # PHASE = -phi, c.-a-d. l'angle SIGNE du brouilleur (stable sur toutes
        # les puissances). Amplitude ~1 => angle fiable ; ~0 => brouilleur faible.
        # Les probes exposent xcorr_re/im BRUTS + |x1|^2 et |x2|^2 ;
        # l'orchestrateur fait la division (evite un bloc divide complexe ici).
        self.blocks_multiply_conj = blocks.multiply_conjugate_cc(1)
        self.blocks_complex_to_float = blocks.complex_to_float(1)
        self.xcorr_iir_re = filter.single_pole_iir_filter_ff(rssi_alpha, 1)
        self.xcorr_iir_im = filter.single_pole_iir_filter_ff(rssi_alpha, 1)
        self.probe_xcorr_re = blocks.probe_signal_f()
        self.probe_xcorr_im = blocks.probe_signal_f()
        # puissances par element (pour la normalisation)
        self.x1_mag2 = blocks.complex_to_mag_squared(1)
        self.x2_mag2 = blocks.complex_to_mag_squared(1)
        self.x1_pow_iir = filter.single_pole_iir_filter_ff(rssi_alpha, 1)
        self.x2_pow_iir = filter.single_pole_iir_filter_ff(rssi_alpha, 1)
        self.probe_x1_pow = blocks.probe_signal_f()
        self.probe_x2_pow = blocks.probe_signal_f()

        # --- Chaine BER (inchangee, laissee en l'etat) ---
        self.fec_ber_bf_0 = fec.ber_bf(False, 10000, -7.0)
        self.digital_constellation_decoder_cb_0 = digital.constellation_decoder_cb(digital.qpsk_constellation())

        # --- Element d'antenne 2 : dephasage spatial du brouilleur ---
        # jam * exp(j * delta_phi) modelise l'arrivee du brouilleur sur le 2e element.
        self.blocks_multiply_const_vxx_2 = blocks.multiply_const_cc(cmath.exp(1j * delta_phi))

        # --- Poids de nulling appliques par le MLP ---
        self.blocks_multiply_const_vxx_0 = blocks.multiply_const_cc(complex(w1_r, w1_i))  # w1 sur x1
        self.blocks_multiply_const_vxx_1 = blocks.multiply_const_cc(complex(w2_r, w2_i))  # w2 sur x2

        # --- Construction des deux elements d'antenne ---
        # x1 = sat + jam            (element 1, reference)
        # x2 = sat + jam*e^(jphi)   (element 2, brouilleur dephase)
        self.blocks_add_x1 = blocks.add_vcc(1)   # element 1
        self.blocks_add_x2 = blocks.add_vcc(1)   # element 2

        # --- Combineur de nulling : sortie = w1*x1 + w2*x2 (somme, coherent labels) ---
        self.blocks_add_out = blocks.add_vcc(1)

        # --- Capteurs sur la somme des elements : somme = x1 + x2 ---
        # C'est cette somme (facteur de reseau) qui rend l'angle observable.
        self.blocks_add_sum = blocks.add_vcc(1)

        self.blocks_complex_to_mag_squared_0 = blocks.complex_to_mag_squared(1)

        ##################################################
        # --- MESURE DU SINR POST-NULLING ---
        # On applique separement les MEMES poids w1, w2 au signal utile seul
        # et a l'interference seule, pour mesurer les puissances residuelles
        # apres nulling, sans les melanger.
        #
        #   Signal utile post-nulling : y_s = w1*s + w2*s = (w1+w2)*s
        #     (le satellite arrive en phase sur les 2 elements -> boresight)
        #   Interference post-nulling : y_j = w1*j + w2*(j*e^(jphi))
        #
        #   SINR_mesure = 10*log10( P(y_s) / P(y_j) )
        ##################################################

        # -- Branche SIGNAL utile seul (satellite) --
        self.sinr_sig_w1 = blocks.multiply_const_cc(complex(w1_r, w1_i))  # w1 * s (element 1)
        self.sinr_sig_w2 = blocks.multiply_const_cc(complex(w2_r, w2_i))  # w2 * s (element 2, sat en phase)
        self.sinr_sig_add = blocks.add_vcc(1)                             # (w1+w2)*s
        self.sinr_sig_mag2 = blocks.complex_to_mag_squared(1)
        self.sinr_sig_iir = filter.single_pole_iir_filter_ff(rssi_alpha, 1)
        self.probe_sinr_sig = blocks.probe_signal_f()

        # -- Branche INTERFERENCE seule (brouilleur) --
        self.sinr_jam_phase = blocks.multiply_const_cc(cmath.exp(1j * delta_phi))  # j * e^(jphi) (element 2)
        self.sinr_jam_w1 = blocks.multiply_const_cc(complex(w1_r, w1_i))           # w1 * j (element 1)
        self.sinr_jam_w2 = blocks.multiply_const_cc(complex(w2_r, w2_i))           # w2 * (j*e^(jphi))
        self.sinr_jam_add = blocks.add_vcc(1)                                      # interference residuelle
        self.sinr_jam_mag2 = blocks.complex_to_mag_squared(1)
        self.sinr_jam_iir = filter.single_pole_iir_filter_ff(rssi_alpha, 1)
        self.probe_sinr_jam = blocks.probe_signal_f()


        ##################################################
        # Connections
        ##################################################
        # Element 1 : x1 = sat + jam (brut)
        self.connect((self.zeromq_sub_source, 0),   (self.blocks_add_x1, 0))
        self.connect((self.zeromq_sub_source_0, 0), (self.blocks_add_x1, 1))

        # Element 2 : x2 = sat + jam*e^(jphi)
        self.connect((self.zeromq_sub_source_0, 0), (self.blocks_multiply_const_vxx_2, 0))
        self.connect((self.zeromq_sub_source, 0),   (self.blocks_add_x2, 0))
        self.connect((self.blocks_multiply_const_vxx_2, 0), (self.blocks_add_x2, 1))

        # Combineur de nulling : sortie = w1*x1 + w2*x2
        self.connect((self.blocks_add_x1, 0), (self.blocks_multiply_const_vxx_0, 0))
        self.connect((self.blocks_add_x2, 0), (self.blocks_multiply_const_vxx_1, 0))
        self.connect((self.blocks_multiply_const_vxx_0, 0), (self.blocks_add_out, 0))
        self.connect((self.blocks_multiply_const_vxx_1, 0), (self.blocks_add_out, 1))

        # Sortie nullee -> decodeur (chaine BER inchangee)
        self.connect((self.blocks_add_out, 0), (self.digital_constellation_decoder_cb_0, 0))
        self.connect((self.digital_constellation_decoder_cb_0, 0), (self.fec_ber_bf_0, 1))
        self.connect((self.zeromq_sub_source_1, 0), (self.fec_ber_bf_0, 0))
        self.connect((self.fec_ber_bf_0, 0), (self.probe_ber, 0))

        # Somme des elements pour les capteurs : somme = x1 + x2
        self.connect((self.blocks_add_x1, 0), (self.blocks_add_sum, 0))
        self.connect((self.blocks_add_x2, 0), (self.blocks_add_sum, 1))

        # RSSI depuis la somme
        self.connect((self.blocks_add_sum, 0), (self.blocks_complex_to_mag_squared_0, 0))
        self.connect((self.blocks_complex_to_mag_squared_0, 0), (self.single_pole_iir_filter_xx_0, 0))
        self.connect((self.single_pole_iir_filter_xx_0, 0), (self.probe_rssi, 0))

        # PSD depuis la somme
        self.connect((self.blocks_add_sum, 0), (self.logpwrfft_x_0, 0))
        self.connect((self.logpwrfft_x_0, 0), (self.probe_psd, 0))

        # Correlation croisee x1 * conj(x2) -> (Re, Im) moyennes (BRUTES)
        self.connect((self.blocks_add_x1, 0), (self.blocks_multiply_conj, 0))
        self.connect((self.blocks_add_x2, 0), (self.blocks_multiply_conj, 1))
        self.connect((self.blocks_multiply_conj, 0), (self.blocks_complex_to_float, 0))
        self.connect((self.blocks_complex_to_float, 0), (self.xcorr_iir_re, 0))
        self.connect((self.blocks_complex_to_float, 1), (self.xcorr_iir_im, 0))
        self.connect((self.xcorr_iir_re, 0), (self.probe_xcorr_re, 0))
        self.connect((self.xcorr_iir_im, 0), (self.probe_xcorr_im, 0))
        # Puissances par element pour la normalisation
        self.connect((self.blocks_add_x1, 0), (self.x1_mag2, 0))
        self.connect((self.x1_mag2, 0), (self.x1_pow_iir, 0))
        self.connect((self.x1_pow_iir, 0), (self.probe_x1_pow, 0))
        self.connect((self.blocks_add_x2, 0), (self.x2_mag2, 0))
        self.connect((self.x2_mag2, 0), (self.x2_pow_iir, 0))
        self.connect((self.x2_pow_iir, 0), (self.probe_x2_pow, 0))

        # --- SINR : branche signal utile (satellite seul) ---
        self.connect((self.zeromq_sub_source, 0), (self.sinr_sig_w1, 0))
        self.connect((self.zeromq_sub_source, 0), (self.sinr_sig_w2, 0))
        self.connect((self.sinr_sig_w1, 0), (self.sinr_sig_add, 0))
        self.connect((self.sinr_sig_w2, 0), (self.sinr_sig_add, 1))
        self.connect((self.sinr_sig_add, 0), (self.sinr_sig_mag2, 0))
        self.connect((self.sinr_sig_mag2, 0), (self.sinr_sig_iir, 0))
        self.connect((self.sinr_sig_iir, 0), (self.probe_sinr_sig, 0))

        # --- SINR : branche interference (brouilleur seul) ---
        self.connect((self.zeromq_sub_source_0, 0), (self.sinr_jam_w1, 0))
        self.connect((self.zeromq_sub_source_0, 0), (self.sinr_jam_phase, 0))
        self.connect((self.sinr_jam_phase, 0), (self.sinr_jam_w2, 0))
        self.connect((self.sinr_jam_w1, 0), (self.sinr_jam_add, 0))
        self.connect((self.sinr_jam_w2, 0), (self.sinr_jam_add, 1))
        self.connect((self.sinr_jam_add, 0), (self.sinr_jam_mag2, 0))
        self.connect((self.sinr_jam_mag2, 0), (self.sinr_jam_iir, 0))
        self.connect((self.sinr_jam_iir, 0), (self.probe_sinr_jam, 0))


    def get_jam_angle(self):
        return self.jam_angle

    def set_jam_angle(self, jam_angle):
        self.jam_angle = jam_angle
        self.set_delta_phi(math.pi * math.sin(math.radians(self.jam_angle)))

    def get_w2_r(self):
        return self.w2_r

    def set_w2_r(self, w2_r):
        self.w2_r = w2_r
        k = complex(self.w2_r, self.w2_i)
        self.blocks_multiply_const_vxx_1.set_k(k)
        self.sinr_sig_w2.set_k(k)
        self.sinr_jam_w2.set_k(k)

    def get_w2_i(self):
        return self.w2_i

    def set_w2_i(self, w2_i):
        self.w2_i = w2_i
        k = complex(self.w2_r, self.w2_i)
        self.blocks_multiply_const_vxx_1.set_k(k)
        self.sinr_sig_w2.set_k(k)
        self.sinr_jam_w2.set_k(k)

    def get_w1_r(self):
        return self.w1_r

    def set_w1_r(self, w1_r):
        self.w1_r = w1_r
        k = complex(self.w1_r, self.w1_i)
        self.blocks_multiply_const_vxx_0.set_k(k)
        self.sinr_sig_w1.set_k(k)
        self.sinr_jam_w1.set_k(k)

    def get_w1_i(self):
        return self.w1_i

    def set_w1_i(self, w1_i):
        self.w1_i = w1_i
        k = complex(self.w1_r, self.w1_i)
        self.blocks_multiply_const_vxx_0.set_k(k)
        self.sinr_sig_w1.set_k(k)
        self.sinr_jam_w1.set_k(k)

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.logpwrfft_x_0.set_sample_rate(self.samp_rate)

    def get_delta_phi(self):
        return self.delta_phi

    def set_delta_phi(self, delta_phi):
        self.delta_phi = delta_phi
        k = cmath.exp(1j * self.delta_phi)
        self.blocks_multiply_const_vxx_2.set_k(k)
        self.sinr_jam_phase.set_k(k)

    def get_rssi_alpha(self):
        return self.rssi_alpha

    def set_rssi_alpha(self, rssi_alpha):
        self.rssi_alpha = rssi_alpha
        self.single_pole_iir_filter_xx_0.set_taps(self.rssi_alpha)
        self.sinr_sig_iir.set_taps(self.rssi_alpha)
        self.sinr_jam_iir.set_taps(self.rssi_alpha)
        self.xcorr_iir_re.set_taps(self.rssi_alpha)
        self.xcorr_iir_im.set_taps(self.rssi_alpha)
        self.x1_pow_iir.set_taps(self.rssi_alpha)
        self.x2_pow_iir.set_taps(self.rssi_alpha)

    # --- Helper : SINR mesure en dB, lu par l'orchestrateur ---
    def get_measured_sinr_db(self):
        p_sig = self.probe_sinr_sig.level()
        p_jam = self.probe_sinr_jam.level()
        eps = 1e-20
        return 10.0 * math.log10((p_sig + eps) / (p_jam + eps))




def main(top_block_cls=defender_spatial_recorded, options=None):
    tb = top_block_cls()

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()

        sys.exit(0)

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    tb.start()

    try:
        input('Press Enter to quit: ')
    except EOFError:
        pass
    tb.stop()
    tb.wait()


if __name__ == '__main__':
    main()