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
        self.delta_phi = delta_phi = math.pi * math.sin(math.radians(jam_angle))

        ##################################################
        # Blocks
        ##################################################
        self.zeromq_sub_source_1 = zeromq.sub_source(gr.sizeof_char, 1, 'tcp://127.0.0.1:5557', 100, False, -1, '')
        self.zeromq_sub_source_1.set_block_alias("Satelitte_def")
        self.zeromq_sub_source_0 = zeromq.sub_source(gr.sizeof_gr_complex, 1, 'tcp://127.0.0.1:5556', 100, False, -1, '')
        self.zeromq_sub_source_0.set_block_alias("Attacker")
        self.zeromq_sub_source = zeromq.sub_source(gr.sizeof_gr_complex, 1, 'tcp://127.0.0.1:5555', 100, False, -1, '')
        self.zeromq_sub_source.set_block_alias("Satelitte")
        self.single_pole_iir_filter_xx_0 = filter.single_pole_iir_filter_ff(0.01, 1)
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
        self.fec_ber_bf_0 = fec.ber_bf(False, 10000, -7.0)
        self.digital_constellation_decoder_cb_0 = digital.constellation_decoder_cb(digital.qpsk_constellation())
        self.blocks_sub_xx_0 = blocks.sub_cc(1)
        self.blocks_null_sink_0 = blocks.null_sink(gr.sizeof_gr_complex*1)
        self.blocks_multiply_const_vxx_2 = blocks.multiply_const_cc(cmath.exp(1j * delta_phi))
        self.blocks_multiply_const_vxx_1 = blocks.multiply_const_cc(complex(w2_r, w2_i))
        self.blocks_multiply_const_vxx_0 = blocks.multiply_const_cc(complex(w1_r, w1_i))
        self.blocks_complex_to_mag_squared_0 = blocks.complex_to_mag_squared(1)
        self.blocks_add_xx_1 = blocks.add_vcc(1)
        self.blocks_add_xx_0 = blocks.add_vcc(1)


        ##################################################
        # Connections
        ##################################################
        self.connect((self.blocks_add_xx_0, 0), (self.blocks_multiply_const_vxx_1, 0))
        self.connect((self.blocks_add_xx_1, 0), (self.blocks_complex_to_mag_squared_0, 0))
        self.connect((self.blocks_add_xx_1, 0), (self.blocks_multiply_const_vxx_0, 0))
        self.connect((self.blocks_add_xx_1, 0), (self.logpwrfft_x_0, 0))
        self.connect((self.blocks_complex_to_mag_squared_0, 0), (self.single_pole_iir_filter_xx_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0, 0), (self.blocks_sub_xx_0, 0))
        self.connect((self.blocks_multiply_const_vxx_1, 0), (self.blocks_sub_xx_0, 1))
        self.connect((self.blocks_multiply_const_vxx_2, 0), (self.blocks_add_xx_0, 1))
        self.connect((self.blocks_sub_xx_0, 0), (self.blocks_null_sink_0, 0))
        self.connect((self.blocks_sub_xx_0, 0), (self.digital_constellation_decoder_cb_0, 0))
        self.connect((self.digital_constellation_decoder_cb_0, 0), (self.fec_ber_bf_0, 1))
        self.connect((self.fec_ber_bf_0, 0), (self.probe_ber, 0))
        self.connect((self.logpwrfft_x_0, 0), (self.probe_psd, 0))
        self.connect((self.single_pole_iir_filter_xx_0, 0), (self.probe_rssi, 0))
        self.connect((self.zeromq_sub_source, 0), (self.blocks_add_xx_0, 0))
        self.connect((self.zeromq_sub_source, 0), (self.blocks_add_xx_1, 0))
        self.connect((self.zeromq_sub_source_0, 0), (self.blocks_add_xx_1, 1))
        self.connect((self.zeromq_sub_source_0, 0), (self.blocks_multiply_const_vxx_2, 0))
        self.connect((self.zeromq_sub_source_1, 0), (self.fec_ber_bf_0, 0))


    def get_jam_angle(self):
        return self.jam_angle

    def set_jam_angle(self, jam_angle):
        self.jam_angle = jam_angle
        self.set_delta_phi(math.pi * math.sin(math.radians(self.jam_angle)))

    def get_w2_r(self):
        return self.w2_r

    def set_w2_r(self, w2_r):
        self.w2_r = w2_r
        self.blocks_multiply_const_vxx_1.set_k(complex(self.w2_r, self.w2_i))

    def get_w2_i(self):
        return self.w2_i

    def set_w2_i(self, w2_i):
        self.w2_i = w2_i
        self.blocks_multiply_const_vxx_1.set_k(complex(self.w2_r, self.w2_i))

    def get_w1_r(self):
        return self.w1_r

    def set_w1_r(self, w1_r):
        self.w1_r = w1_r
        self.blocks_multiply_const_vxx_0.set_k(complex(self.w1_r, self.w1_i))

    def get_w1_i(self):
        return self.w1_i

    def set_w1_i(self, w1_i):
        self.w1_i = w1_i
        self.blocks_multiply_const_vxx_0.set_k(complex(self.w1_r, self.w1_i))

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.logpwrfft_x_0.set_sample_rate(self.samp_rate)

    def get_delta_phi(self):
        return self.delta_phi

    def set_delta_phi(self, delta_phi):
        self.delta_phi = delta_phi
        self.blocks_multiply_const_vxx_2.set_k(cmath.exp(1j * self.delta_phi))




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
