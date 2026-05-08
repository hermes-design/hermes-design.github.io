#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Attacker with Periodic Cycle
# GNU Radio version: 3.10.1.1

from packaging.version import Version as StrictVersion

if __name__ == '__main__':
    import ctypes
    import sys
    if sys.platform.startswith('linux'):
        try:
            x11 = ctypes.cdll.LoadLibrary('libX11.so')
            x11.XInitThreads()
        except:
            print("Warning: failed to XInitThreads()")

from gnuradio import analog
from gnuradio import blocks
from gnuradio import gr
from gnuradio.filter import firdes
from gnuradio.fft import window
import sys
import signal
from PyQt5 import Qt
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio import zeromq
from gnuradio.qtgui import Range, RangeWidget
from PyQt5 import QtCore



from gnuradio import qtgui

class attackerv(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "Attacker with Periodic Cycle", catch_exceptions=True)
        Qt.QWidget.__init__(self)
        self.setWindowTitle("Attacker with Periodic Cycle")
        qtgui.util.check_set_qss()
        try:
            self.setWindowIcon(Qt.QIcon.fromTheme('gnuradio-grc'))
        except:
            pass
        self.top_scroll_layout = Qt.QVBoxLayout()
        self.setLayout(self.top_scroll_layout)
        self.top_scroll = Qt.QScrollArea()
        self.top_scroll.setFrameStyle(Qt.QFrame.NoFrame)
        self.top_scroll_layout.addWidget(self.top_scroll)
        self.top_scroll.setWidgetResizable(True)
        self.top_widget = Qt.QWidget()
        self.top_scroll.setWidget(self.top_widget)
        self.top_layout = Qt.QVBoxLayout(self.top_widget)
        self.top_grid_layout = Qt.QGridLayout()
        self.top_layout.addLayout(self.top_grid_layout)

        self.settings = Qt.QSettings("GNU Radio", "attackerv")

        try:
            if StrictVersion(Qt.qVersion()) < StrictVersion("5.0.0"):
                self.restoreGeometry(self.settings.value("geometry").toByteArray())
            else:
                self.restoreGeometry(self.settings.value("geometry"))
        except:
            pass

        ##################################################
        # Variables
        ##################################################
        self.mttr_min = mttr_min = 2
        self.mtti_min = mtti_min = 100
        self.sps = sps = 4
        self.sample_rate = sample_rate = 32000
        self.period_total_min = period_total_min = mtti_min + mttr_min
        self.on_time_min = on_time_min = mttr_min
        self.jammer_power = jammer_power = 0.5
        self.jammer_freq_offset = jammer_freq_offset = 5000
        self.control_rate = control_rate = 10
        self.chip_rate = chip_rate = 1.023e6

        ##################################################
        # Blocks
        ##################################################
        self.zeromq_sub_source_0 = zeromq.sub_source(gr.sizeof_gr_complex, 1, 'tcp://127.0.0.1:5555', 100, False, 0, '')
        self.zeromq_sub_source_0.set_block_alias("zeromq_sub_source")
        self.zeromq_pub_sink_0 = zeromq.pub_sink(gr.sizeof_gr_complex, 2, 'tcp://*:5556', 100, False, 0, '')
        self.time_slicer = blocks.threshold_ff(1.0 - (2.0 * (on_time_min / period_total_min)) - 0.01, 1.0 - (2.0 * (on_time_min / period_total_min)) + 0.01, 0)
        self.rf_source = analog.sig_source_c(sample_rate, analog.GR_COS_WAVE, jammer_freq_offset, 1, 0, 0)
        self.power_scale = blocks.multiply_const_cc(jammer_power)
        self.on_off_switch = blocks.multiply_vcc(1)
        self._mttr_min_range = Range(0.01, 20, 0.01, 2, 200)
        self._mttr_min_win = RangeWidget(self._mttr_min_range, self.set_mttr_min, "MTTR (Minutes)", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._mttr_min_win)
        self._mtti_min_range = Range(0.01, 200, 0.01, 100, 200)
        self._mtti_min_win = RangeWidget(self._mtti_min_range, self.set_mtti_min, "MTTI (Minutes)", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._mtti_min_win)
        self.mixer = blocks.add_vcc(1)
        self.mag_sq_jammed = blocks.complex_to_mag_squared(1)
        self.mag_sq_clean = blocks.complex_to_mag_squared(1)
        self.interpolator = blocks.repeat(gr.sizeof_float*1, int(sample_rate / control_rate))
        self.float_to_complex = blocks.float_to_complex(1)
        self.file_jammed = blocks.file_sink(gr.sizeof_float*1, 'signal_brouille.bin', False)
        self.file_jammed.set_unbuffered(True)
        self.file_clean = blocks.file_sink(gr.sizeof_float*1, 'signal_propre.bin', False)
        self.file_clean.set_unbuffered(True)
        self.decimate_jammed = blocks.keep_one_in_n(gr.sizeof_float*1, int(sample_rate / 10))
        self.decimate_clean = blocks.keep_one_in_n(gr.sizeof_float*1, int(sample_rate / 10))
        self.control_sawtooth = analog.sig_source_f(control_rate, analog.GR_SAW_WAVE, 1.0 / (period_total_min * 60.0), 1, 0, 0)
        self.blocks_stream_to_vector_0 = blocks.stream_to_vector(gr.sizeof_gr_complex*1, 2)


        ##################################################
        # Connections
        ##################################################
        self.connect((self.blocks_stream_to_vector_0, 0), (self.zeromq_pub_sink_0, 0))
        self.connect((self.control_sawtooth, 0), (self.time_slicer, 0))
        self.connect((self.decimate_clean, 0), (self.file_clean, 0))
        self.connect((self.decimate_jammed, 0), (self.file_jammed, 0))
        self.connect((self.float_to_complex, 0), (self.on_off_switch, 1))
        self.connect((self.interpolator, 0), (self.float_to_complex, 0))
        self.connect((self.mag_sq_clean, 0), (self.decimate_clean, 0))
        self.connect((self.mag_sq_jammed, 0), (self.decimate_jammed, 0))
        self.connect((self.mixer, 0), (self.blocks_stream_to_vector_0, 0))
        self.connect((self.mixer, 0), (self.mag_sq_jammed, 0))
        self.connect((self.on_off_switch, 0), (self.power_scale, 0))
        self.connect((self.power_scale, 0), (self.mixer, 1))
        self.connect((self.rf_source, 0), (self.on_off_switch, 0))
        self.connect((self.time_slicer, 0), (self.interpolator, 0))
        self.connect((self.zeromq_sub_source_0, 0), (self.mag_sq_clean, 0))
        self.connect((self.zeromq_sub_source_0, 0), (self.mixer, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "attackerv")
        self.settings.setValue("geometry", self.saveGeometry())
        self.stop()
        self.wait()

        event.accept()

    def get_mttr_min(self):
        return self.mttr_min

    def set_mttr_min(self, mttr_min):
        self.mttr_min = mttr_min
        self.set_on_time_min(self.mttr_min)
        self.set_period_total_min(self.mtti_min + self.mttr_min)

    def get_mtti_min(self):
        return self.mtti_min

    def set_mtti_min(self, mtti_min):
        self.mtti_min = mtti_min
        self.set_period_total_min(self.mtti_min + self.mttr_min)

    def get_sps(self):
        return self.sps

    def set_sps(self, sps):
        self.sps = sps

    def get_sample_rate(self):
        return self.sample_rate

    def set_sample_rate(self, sample_rate):
        self.sample_rate = sample_rate
        self.decimate_clean.set_n(int(self.sample_rate / 10))
        self.decimate_jammed.set_n(int(self.sample_rate / 10))
        self.interpolator.set_interpolation(int(self.sample_rate / self.control_rate))
        self.rf_source.set_sampling_freq(self.sample_rate)

    def get_period_total_min(self):
        return self.period_total_min

    def set_period_total_min(self, period_total_min):
        self.period_total_min = period_total_min
        self.control_sawtooth.set_frequency(1.0 / (self.period_total_min * 60.0))
        self.time_slicer.set_hi(1.0 - (2.0 * (self.on_time_min / self.period_total_min)) + 0.01)
        self.time_slicer.set_lo(1.0 - (2.0 * (self.on_time_min / self.period_total_min)) - 0.01)

    def get_on_time_min(self):
        return self.on_time_min

    def set_on_time_min(self, on_time_min):
        self.on_time_min = on_time_min
        self.time_slicer.set_hi(1.0 - (2.0 * (self.on_time_min / self.period_total_min)) + 0.01)
        self.time_slicer.set_lo(1.0 - (2.0 * (self.on_time_min / self.period_total_min)) - 0.01)

    def get_jammer_power(self):
        return self.jammer_power

    def set_jammer_power(self, jammer_power):
        self.jammer_power = jammer_power
        self.power_scale.set_k(self.jammer_power)

    def get_jammer_freq_offset(self):
        return self.jammer_freq_offset

    def set_jammer_freq_offset(self, jammer_freq_offset):
        self.jammer_freq_offset = jammer_freq_offset
        self.rf_source.set_frequency(self.jammer_freq_offset)

    def get_control_rate(self):
        return self.control_rate

    def set_control_rate(self, control_rate):
        self.control_rate = control_rate
        self.control_sawtooth.set_sampling_freq(self.control_rate)
        self.interpolator.set_interpolation(int(self.sample_rate / self.control_rate))

    def get_chip_rate(self):
        return self.chip_rate

    def set_chip_rate(self, chip_rate):
        self.chip_rate = chip_rate




def main(top_block_cls=attackerv, options=None):

    if StrictVersion("4.5.0") <= StrictVersion(Qt.qVersion()) < StrictVersion("5.0.0"):
        style = gr.prefs().get_string('qtgui', 'style', 'raster')
        Qt.QApplication.setGraphicsSystem(style)
    qapp = Qt.QApplication(sys.argv)

    tb = top_block_cls()

    tb.start()

    tb.show()

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()

        Qt.QApplication.quit()

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    timer = Qt.QTimer()
    timer.start(500)
    timer.timeout.connect(lambda: None)

    qapp.exec_()

if __name__ == '__main__':
    main()
