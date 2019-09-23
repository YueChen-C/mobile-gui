#!python
# -*- coding: utf-8 -*-
import argparse
import logging
import os
import sys
from os.path import abspath, dirname

sys.path.insert(0, abspath(dirname(abspath(__file__)) + '/..'))
import qdarkstyle
from app.menus import Ui_MainWindow as ui_main

EXAMPLE_PATH = os.path.abspath(os.path.dirname(__file__))
REPO_PATH = os.path.dirname(EXAMPLE_PATH)
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import QTimer, QSettings

style_method = qdarkstyle.load_stylesheet_pyqt5


def main():
    """Execute QDarkStyle example."""
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--qt_from', default='pyqt5',
                        choices=['pyqt', 'pyqt5', 'pyside', 'pyside2', 'qtpy', 'pyqtgraph'],
                        help="Choose which wrapper/framework is to be used to run the example.", type=str)
    parser.add_argument('--no_dark', action='store_true',
                        help="Exihibts the original  window (without qdarkstyle).")
    parser.add_argument('--test', action='store_true',
                        help="Auto close window after 2s.")
    parser.add_argument('--reset', action='store_true',
                        help="Reset GUI settings (position, size).")
    parser.add_argument('--screenshots', action='store_true',
                        help="Generate screenshots.")

    # parsing arguments from command line
    args = parser.parse_args()

    # set log for debug
    logging.basicConfig(level=logging.DEBUG)

    # to avoid problems when testing without screen
    if args.test:
        os.environ['QT_QPA_PLATFORM'] = 'offscreen'

    def write_settings(window):
        """Get window settings and write it into a file."""
        settings = QSettings('QDarkStyle', 'QDarkStyle Example')
        settings.setValue('pos', window.pos())
        settings.setValue('size', window.size())
        settings.setValue('state', window.saveState())

    def read_settings(window, reset=False):
        """Read and set window settings from a file."""
        settings = QSettings('QDarkStyle', 'QDarkStyle Example')
        if args.qt_from == 'pyside' or args.qt_from == 'pyside2':
            pos = settings.value('pos', window.pos())
            size = settings.value('size', window.size())
            state = settings.value('state', window.saveState())
        else:
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
    ui = ui_main()
    ui.setupUi(window)
    window.setWindowTitle("Mobile Tool v1.0.0")

    if args.test:
        QTimer.singleShot(2000, app.exit)

    # run
    read_settings(window, args.reset)
    window.showMaximized()

    # Save screenshots for differents displays and quit

    app.exec_()
    write_settings(window)


if __name__ == "__main__":
    sys.exit(main())
