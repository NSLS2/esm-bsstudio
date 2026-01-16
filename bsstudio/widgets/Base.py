from PyQt5 import QtDesigner, QtGui, QtWidgets, QtCore
#from qtpy.QtWidgets import QLabel, QApplication, QDoubleSpinBox, QWidget, QPushButton
from PyQt5.QtWidgets import QLabel, QApplication, QDoubleSpinBox, QWidget, QPushButton, QPlainTextEdit
#from qtpy.QtDesigner import QExtensionFactory
from PyQt5.QtDesigner import QExtensionFactory
from PyQt5.QtCore import pyqtProperty as Property
from PyQt5.QtCore import pyqtSignal
from ..functions import getTopObject
import inspect
from itertools import dropwhile
import textwrap
import time
import logging

logger = logging.getLogger(__name__)
#logger.setLevel(logging.DEBUG)
logger.setLevel(logging.WARN)


class BaseWidget:
	closing = pyqtSignal()

	def __init__(self, parent=None):
		self.isTopLevel = False

	def initialize(self):
		pass

	def pauseWidget(self):
		pass

	def resumeWidget(self):
		pass


	def windowFileName(self):
		fileName = None
		if not self._paused:
			fileName = getTopObject(self).uiFilePath
		else:
			try:
				fileName = self.core.formWindowManager().activeFormWindow().fileName()
			except:
				logger.info("Error getting window filename in designer")
		return fileName


	def ui(self):
		if hasattr(self, "_ui"):
			return self._ui()
		from ..functions import makeUiFunction
		_ui = makeUiFunction(self)
		self._ui = _ui
		return _ui()

	def resumeChildren(self):
		children = self.findChildren(BaseWidget)
		for c in children:
			c.resumeWidget()

	def pauseChildren(self):
		children = self.findChildren(BaseWidget)
		for c in children:
			c.pauseWidget()



	def closeEvent(self, evt):
		self.closing.emit()
		logger.info("close Event")
		self.hide()
		for child in self.findChildren(QWidget):
			try:
				child.close()
			except:
				None


