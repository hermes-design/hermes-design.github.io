#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Satellite Reliability Model
# GNU Radio version: 3.10.1.1

from gnuradio import blocks
import numpy
from gnuradio import digital
from gnuradio import gr
from gnuradio.filter import firdes
from gnuradio.fft import window
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio import zeromq




class satellite_advanced(gr.top_block):

    def __init__(self):
        gr.top_block.__init__(self, "Satellite Reliability Model", catch_exceptions=True)

        ##################################################
        # Variables
        ##################################################
        self.samp_rate = samp_rate = 1023000
        # Debit binaire : QPSK (2 bits/symbole) a 4 echantillons/symbole
        # -> bits/s = samp_rate * bits_par_symbole / sps = samp_rate * 2 / 4
        self.bit_rate = bit_rate = int(samp_rate * 2 / 4)

        ##################################################
        # Blocks
        ##################################################
        self.zeromq_pub_sink_1 = zeromq.pub_sink(gr.sizeof_char, 1, 'tcp://127.0.0.1:5557', 100, False, -1, '')
        self.zeromq_pub_sink_0 = zeromq.pub_sink(gr.sizeof_gr_complex, 1, 'tcp://127.0.0.1:5555', 100, False, -1, '')
        self.digital_constellation_modulator_0 = digital.generic_mod(
            constellation=digital.qpsk_constellation(),
            differential=True,
            samples_per_symbol=4,
            pre_diff_code=True,
            excess_bw=0.35,
            verbose=False,
            log=False,
            truncate=False)
        self.blocks_throttle_0 = blocks.throttle(gr.sizeof_gr_complex*1, samp_rate,True)
        # Throttle octet sur la branche des bits de reference, cadence au debit binaire
        # pour rester coherent en temps avec la branche RF cadencee par blocks_throttle_0.
        self.blocks_throttle_bits = blocks.throttle(gr.sizeof_char*1, bit_rate, True)
        self.blocks_multiply_const_vxx_0 = blocks.multiply_const_cc(10**(-15/20.0))
        self.analog_random_source_x_0 = blocks.vector_source_b(list(map(int, numpy.random.randint(0, 2, 1000))), True)


        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_random_source_x_0, 0), (self.digital_constellation_modulator_0, 0))
        self.connect((self.analog_random_source_x_0, 0), (self.blocks_throttle_bits, 0))
        self.connect((self.blocks_throttle_bits, 0), (self.zeromq_pub_sink_1, 0))
        self.connect((self.blocks_multiply_const_vxx_0, 0), (self.zeromq_pub_sink_0, 0))
        self.connect((self.blocks_throttle_0, 0), (self.blocks_multiply_const_vxx_0, 0))
        self.connect((self.digital_constellation_modulator_0, 0), (self.blocks_throttle_0, 0))


    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.blocks_throttle_0.set_sample_rate(self.samp_rate)
        self.set_bit_rate(int(self.samp_rate * 2 / 4))

    def get_bit_rate(self):
        return self.bit_rate

    def set_bit_rate(self, bit_rate):
        self.bit_rate = bit_rate
        self.blocks_throttle_bits.set_sample_rate(self.bit_rate)




def main(top_block_cls=satellite_advanced, options=None):
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