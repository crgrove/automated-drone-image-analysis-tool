import sys
import logging
import os
from PyQt5.QtGui import QFontDatabase, QFont, QIcon
from PyQt5.QtCore import QFile, QTextStream, QTranslator, QLocale
from PyQt5.QtWidgets import QApplication
from multiprocessing import freeze_support
from core.controllers.MainWindow import MainWindow

import faulthandler
import qdarktheme

version = '1.2.5'
def main():
	if sys.platform == 'win32':
		home_path = os.path.expanduser("~")
		app_path = home_path + '/AppData/Roaming/ADIAT/'
		if(not os.path.exists(app_path)):
			os.makedirs(app_path)
	else:
		app_path = 'Library/Application Support/ADIAT/'
		if(not os.path.exists(app_path)):
			os.makedirs(app_path)
	log_path = app_path +'adiat_logs.txt'
	logger = logging.getLogger(__name__)
	stdoutHandler = logging.StreamHandler(stream=sys.stdout)
	fileHandler = logging.FileHandler(log_path)
	stdoutFmt = logging.Formatter(
	"%(name)s: %(asctime)s | %(levelname)s | %(filename)s:%(lineno)s | %(process)d >>> %(message)s")
	stdoutHandler.setFormatter(stdoutFmt)
	fileHandler.setFormatter(stdoutFmt)
	logger.addHandler(stdoutHandler)
	logger.addHandler(fileHandler)
	app = QApplication(sys.argv)
	qdarktheme.setup_theme()

	app.setWindowIcon(QIcon('ADIAT.ico'))

	mw = MainWindow(qdarktheme, version)
	mw.show()

	sys.exit(app.exec_())


if __name__ == "__main__":
	#faulthandler.enable()
	freeze_support()
	main()
