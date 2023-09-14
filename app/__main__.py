import sys
import logging
from PyQt5.QtGui import QFontDatabase, QFont, QIcon
from PyQt5.QtCore import QFile, QTextStream, QTranslator, QLocale
from PyQt5.QtWidgets import QApplication

from controllers.MainWindow import MainWindow

import resources_rc  # noqa
import faulthandler

def main():
    logging.basicConfig(level=logging.DEBUG)
    app = QApplication(sys.argv)

    app.setWindowIcon(QIcon('ADIAT.ico'))

    fontDB = QFontDatabase()
    fontDB.addApplicationFont(':/fonts/Roboto-Regular.ttf')
    app.setFont(QFont('Roboto'))

    f = QFile(':/style.qss')
    f.open(QFile.ReadOnly | QFile.Text)
    app.setStyleSheet(QTextStream(f).readAll())
    f.close()

    mw = MainWindow()
    mw.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    faulthandler.enable()
    main()
