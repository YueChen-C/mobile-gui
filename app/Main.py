#!python
# -*- coding: utf-8 -*-
import argparse
import logging
import os
import sys
from os.path import abspath, dirname

from app import check_environ

sys.path.insert(0, abspath(dirname(abspath(__file__)) + '/..'))
import qdarkstyle
from app.Menus import MainWindow

EXAMPLE_PATH = os.path.abspath(os.path.dirname(__file__))
REPO_PATH = os.path.dirname(EXAMPLE_PATH)
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import QSettings

style_method = qdarkstyle.load_stylesheet_pyqt5


def main():
    """Execute QDarkStyle example."""
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--reset', action='store_true',
                        help="Reset GUI settings (position, size).")
    args = parser.parse_args()
    logging.basicConfig(level=logging.DEBUG)

    def write_settings(window):
        """Get window settings and write it into a file."""
        settings = QSettings('QDarkStyle', 'QDarkStyle Example')
        settings.setValue('pos', window.pos())
        settings.setValue('size', window.size())
        settings.setValue('state', window.saveState())

    def read_settings(window, reset=False):
        """Read and set window settings from a file."""
        settings = QSettings('QDarkStyle', 'QDarkStyle Example')
        pos = settings.value('pos', window.pos(), type='QPoint')
        size = settings.value('size', window.size(), type='QSize')
        state = settings.value('state', window.saveState(), type='QByteArray')

        if not reset:
            window.restoreState(state)
            window.resize(size)
            window.move(pos)

    # create the application
    app = QApplication(sys.argv)
    app.setOrganizationName('QDarkStyle')
    app.setApplicationName('QDarkStyle Example')

    # setup stylesheet
    style = style_method()
    app.setStyleSheet(style)

    # create main window
    window = QMainWindow()
    window.setObjectName('mainwindow')
    ui = MainWindow()
    try:
        ui.setupUi(window)
        ui.comboBoxAdd()
        window.setWindowTitle("Mobile Tool v1.0.0")
        read_settings(window, args.reset)
        window.showMaximized()
        check_environ()
    except Exception as E:
        ui.msg(E)

    app.exec_()
    write_settings(window)


if __name__ == "__main__":
    sys.exit(main())
