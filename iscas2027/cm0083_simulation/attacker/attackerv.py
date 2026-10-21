#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Attacker with Periodic Cycle
# GNU Radio version: 3.10.1.1

from gnuradio import analog
from gnuradio import blocks
from gnuradio import gr
from gnuradio.filter import firdes
from gnuradio.fft import window
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio import zeromq




class attackerv(gr.top_block):

    def __init__(self):
        gr.top_block.__init__(self, "Attacker with Periodic Cycle", catch_exceptions=True)

        ##################################################
        # Variables
        ##################################################
        self.samp_rate = samp_rate = 1000000
        self.jam_type = jam_type = 0
        self.jam_power = jam_power = -20
        self.jam_freq_offset = jam_freq_offset = 0
        self.jam_angle = jam_angle = 0

        ##################################################
        # Blocks
        ##################################################
        self.zeromq_pub_sink_1 = zeromq.pub_sink(gr.sizeof_gr_complex, 1, 'tcp://127.0.0.1:5556', 100, False, -1, '')
        self.blocks_selector_0 = blocks.selector(gr.sizeof_gr_complex*1,int(jam_type),0)
        self.blocks_selector_0.set_enabled(True)
        self.analog_sig_source_x_0 = analog.sig_source_c(samp_rate, analog.GR_COS_WAVE, jam_freq_offset, 10**(jam_power/20.0), 0, 0)
        self.analog_noise_source_x_0 = analog.noise_source_c(analog.GR_GAUSSIAN, 10**(jam_power/20.0), 0)


        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_noise_source_x_0, 0), (self.blocks_selector_0, 0))
        self.connect((self.analog_sig_source_x_0, 0), (self.blocks_selector_0, 1))
        self.connect((self.blocks_selector_0, 0), (self.zeromq_pub_sink_1, 0))


    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.analog_sig_source_x_0.set_sampling_freq(self.samp_rate)

    def get_jam_type(self):
        return self.jam_type

    def set_jam_type(self, jam_type):
        self.jam_type = jam_type
        self.blocks_selector_0.set_input_index(int(self.jam_type))

    def get_jam_power(self):
        return self.jam_power

    def set_jam_power(self, jam_power):
        self.jam_power = jam_power
        self.analog_noise_source_x_0.set_amplitude(10**(self.jam_power/20.0))
        self.analog_sig_source_x_0.set_amplitude(10**(self.jam_power/20.0))

    def get_jam_freq_offset(self):
        return self.jam_freq_offset

    def set_jam_freq_offset(self, jam_freq_offset):
        self.jam_freq_offset = jam_freq_offset
        self.analog_sig_source_x_0.set_frequency(self.jam_freq_offset)

    def get_jam_angle(self):
        return self.jam_angle

    def set_jam_angle(self, jam_angle):
        self.jam_angle = jam_angle




def main(top_block_cls=attackerv, options=None):
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
