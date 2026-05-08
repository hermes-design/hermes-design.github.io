#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Defender Recorded (Repair Rate Test)
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

from PyQt5 import Qt
from gnuradio import qtgui
from gnuradio.filter import firdes
import sip
from gnuradio import analog
from gnuradio import blocks
from gnuradio import gr
from gnuradio.fft import window
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio import zeromq
from gnuradio.qtgui import Range, RangeWidget
from PyQt5 import QtCore
import math, cmath



from gnuradio import qtgui

class defender_spatial_recorded(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "Defender Recorded (Repair Rate Test)", catch_exceptions=True)
        Qt.QWidget.__init__(self)
        self.setWindowTitle("Defender Recorded (Repair Rate Test)")
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

        self.settings = Qt.QSettings("GNU Radio", "defender_spatial_recorded")

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
        self.null_angle = null_angle = 0
        self.mttr_def_min = mttr_def_min = 1.0/2.0
        self.mtid_min = mtid_min = 1.0/10.0
        self.samp_rate = samp_rate = 32000
        self.period_total_min = period_total_min = mtid_min + mttr_def_min
        self.null_weight = null_weight = cmath.exp(-1j * math.pi * math.sin(math.radians(null_angle)))
        self.control_rate = control_rate = 10

        ##################################################
        # Blocks
        ##################################################
        self.zeromq_sub_source = zeromq.sub_source(gr.sizeof_gr_complex, 2, 'tcp://127.0.0.1:5556', 100, False, -1, '')
        self.subtractor = blocks.sub_cc(1)
        self.split_antennas = blocks.vector_to_streams(gr.sizeof_gr_complex*1, 2)
        self.qtgui_freq_sink_x_0 = qtgui.freq_sink_c(
            1024, #size
            window.WIN_BLACKMAN_hARRIS, #wintype
            0, #fc
            samp_rate, #bw
            "Efficacite du Nulling", #name
            2,
            None # parent
        )
        self.qtgui_freq_sink_x_0.set_update_time(0.10)
        self.qtgui_freq_sink_x_0.set_y_axis(-140, 10)
        self.qtgui_freq_sink_x_0.set_y_label('Relative Gain', 'dB')
        self.qtgui_freq_sink_x_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, 0.0, 0, "")
        self.qtgui_freq_sink_x_0.enable_autoscale(False)
        self.qtgui_freq_sink_x_0.enable_grid(True)
        self.qtgui_freq_sink_x_0.set_fft_average(0.2)
        self.qtgui_freq_sink_x_0.enable_axis_labels(True)
        self.qtgui_freq_sink_x_0.enable_control_panel(False)
        self.qtgui_freq_sink_x_0.set_fft_window_normalized(False)



        labels = ['Signal Brut', 'Signal Nettoye', '', '', '',
            '', '', '', '', '']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ["blue", "red", "green", "black", "cyan",
            "magenta", "yellow", "dark red", "dark green", "dark blue"]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]

        for i in range(2):
            if len(labels[i]) == 0:
                self.qtgui_freq_sink_x_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_freq_sink_x_0.set_line_label(i, labels[i])
            self.qtgui_freq_sink_x_0.set_line_width(i, widths[i])
            self.qtgui_freq_sink_x_0.set_line_color(i, colors[i])
            self.qtgui_freq_sink_x_0.set_line_alpha(i, alphas[i])

        self._qtgui_freq_sink_x_0_win = sip.wrapinstance(self.qtgui_freq_sink_x_0.qwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._qtgui_freq_sink_x_0_win, 1, 0, 1, 1)
        for r in range(1, 2):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 1):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._null_angle_range = Range(-90, 90, 1, 0, 200)
        self._null_angle_win = RangeWidget(self._null_angle_range, self.set_null_angle, "Nulling Angle (Deg)", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_grid_layout.addWidget(self._null_angle_win, 0, 0, 1, 1)
        for r in range(0, 1):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 1):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.mag_sq_defended = blocks.complex_to_mag_squared(1)
        self.interpolator = blocks.repeat(gr.sizeof_float*1, int(samp_rate / control_rate))
        self.float_to_complex = blocks.float_to_complex(1)
        self.file_defended_power = blocks.file_sink(gr.sizeof_float*1, 'defended_power.bin', False)
        self.file_defended_power.set_unbuffered(True)
        self.defense_switch = blocks.threshold_ff((mtid_min / period_total_min) - 0.01, (mtid_min / period_total_min) + 0.01, 0)
        self.defense_cycle = analog.sig_source_f(control_rate, analog.GR_SAW_WAVE, 1.0 / (period_total_min * 60.0), 0.5, 0.5, 0)
        self.apply_weight = blocks.multiply_const_cc(null_weight)
        self.apply_switch = blocks.multiply_vcc(1)


        ##################################################
        # Connections
        ##################################################
        self.connect((self.apply_switch, 0), (self.subtractor, 1))
        self.connect((self.apply_weight, 0), (self.apply_switch, 0))
        self.connect((self.defense_cycle, 0), (self.defense_switch, 0))
        self.connect((self.defense_switch, 0), (self.interpolator, 0))
        self.connect((self.float_to_complex, 0), (self.apply_switch, 1))
        self.connect((self.interpolator, 0), (self.float_to_complex, 0))
        self.connect((self.mag_sq_defended, 0), (self.file_defended_power, 0))
        self.connect((self.split_antennas, 1), (self.apply_weight, 0))
        self.connect((self.split_antennas, 0), (self.qtgui_freq_sink_x_0, 0))
        self.connect((self.split_antennas, 0), (self.subtractor, 0))
        self.connect((self.subtractor, 0), (self.mag_sq_defended, 0))
        self.connect((self.subtractor, 0), (self.qtgui_freq_sink_x_0, 1))
        self.connect((self.zeromq_sub_source, 0), (self.split_antennas, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "defender_spatial_recorded")
        self.settings.setValue("geometry", self.saveGeometry())
        self.stop()
        self.wait()

        event.accept()

    def get_null_angle(self):
        return self.null_angle

    def set_null_angle(self, null_angle):
        self.null_angle = null_angle
        self.set_null_weight(cmath.exp(-1j * math.pi * math.sin(math.radians(self.null_angle))))

    def get_mttr_def_min(self):
        return self.mttr_def_min

    def set_mttr_def_min(self, mttr_def_min):
        self.mttr_def_min = mttr_def_min
        self.set_period_total_min(self.mtid_min + self.mttr_def_min)

    def get_mtid_min(self):
        return self.mtid_min

    def set_mtid_min(self, mtid_min):
        self.mtid_min = mtid_min
        self.set_period_total_min(self.mtid_min + self.mttr_def_min)
        self.defense_switch.set_hi((self.mtid_min / self.period_total_min) + 0.01)
        self.defense_switch.set_lo((self.mtid_min / self.period_total_min) - 0.01)

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.interpolator.set_interpolation(int(self.samp_rate / self.control_rate))
        self.qtgui_freq_sink_x_0.set_frequency_range(0, self.samp_rate)

    def get_period_total_min(self):
        return self.period_total_min

    def set_period_total_min(self, period_total_min):
        self.period_total_min = period_total_min
        self.defense_cycle.set_frequency(1.0 / (self.period_total_min * 60.0))
        self.defense_switch.set_hi((self.mtid_min / self.period_total_min) + 0.01)
        self.defense_switch.set_lo((self.mtid_min / self.period_total_min) - 0.01)

    def get_null_weight(self):
        return self.null_weight

    def set_null_weight(self, null_weight):
        self.null_weight = null_weight
        self.apply_weight.set_k(self.null_weight)

    def get_control_rate(self):
        return self.control_rate

    def set_control_rate(self, control_rate):
        self.control_rate = control_rate
        self.defense_cycle.set_sampling_freq(self.control_rate)
        self.interpolator.set_interpolation(int(self.samp_rate / self.control_rate))




def main(top_block_cls=defender_spatial_recorded, options=None):

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
