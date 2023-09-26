import sys
import logging
from PyQt5.QtGui import QFontDatabase, QFont, QIcon
from PyQt5.QtCore import QFile, QTextStream, QTranslator, QLocale
from PyQt5.QtWidgets import QApplication
from multiprocessing import freeze_support

from core.controllers.MainWindow import MainWindow

import resources_rc  # noqa
import faulthandler
import qdarktheme

def main():
    logging.basicConfig(level=logging.DEBUG)
    app = QApplication(sys.argv)
    qdarktheme.setup_theme()

    app.setWindowIcon(QIcon('ADIAT.ico'))

    mw = MainWindow(qdarktheme)
    mw.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    #faulthandler.enable()
    freeze_support()
    main()
