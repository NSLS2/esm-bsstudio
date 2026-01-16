from PyQt5 import QtDesigner, QtGui, QtWidgets, QtCore, sip
#from qtpy.QtWidgets import QLabel, QApplication, QDoubleSpinBox, QWidget, QPushButton
from PyQt5.QtWidgets import QLabel, QApplication, QDoubleSpinBox, QWidget, QPushButton, QPlainTextEdit, QFrame
#from qtpy.QtDesigner import QExtensionFactory
from PyQt5.QtDesigner import QExtensionFactory
from PyQt5.QtCore import pyqtProperty as Property
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import QThread
from PyQt5.QtCore import QReadWriteLock
from PyQt5.Qt import Qt
import inspect
from itertools import dropwhile
import textwrap
from .CodeObject import CodeObject
import logging
from ..worker import Worker
import time
import threading
from .REButton import makeProperty

logger = logging.getLogger(__name__)
#logger.setLevel(logging.DEBUG)
logger.setLevel(logging.WARN)

main_thread = threading.current_thread()

def isOphyd(obj):
	from ophyd.ophydobj import OphydObject
	return issubclass(obj, OphydObject)

class WorkerThread(QThread):
	lock = QReadWriteLock()
	cancelled = False
	def cancel(self):
		WorkerThread.cancelled = True
	def resume(self):
		WorkerThread.cancelled = False
	def setFunc(self, func):
		self.func = func
	def run(self):
		self.func()	

class TextUpdateBase(CodeObject):
	def __init__(self, parent=None,*,sig=""):
		#self.parent = parent
		#super().__init__(parent)
		#QLabel.__init__(self, parent)
		CodeObject.__init__(self, parent)
		self.updatePeriod_ = 1500
		self._updatePeriod = "1500"
		self._source = ""
		self.source = sig
		self._useThreading = False
		#self.worker = Worker(self.start_thread)
		t0 = time.time()
		self.worker = WorkerThread(self)
		self.worker.setFunc(self.start_thread)
		self.timer = QtCore.QTimer(self)
		self.timer.setInterval(self.updatePeriod_)
		self.timer.timeout.connect(self.timeout)
		logger.info(str(time.time()-t0) +" seconds to create thread")
		self.threadMode = "qtimer"
		self.start_time = time.time()


	def timeout(self):
		t0 = time.time()
		self.runCode()
		logger.info("Timeout function duration: "+str(time.time()-t0))

	def resumeWorkerThread(self):
		WorkerThread.cancelled = False

	def start_thread(self):
		self.update()
		self.repaint()
		time.sleep(10)
		logger.info("Starting thread")
		t0 = time.time()
		WorkerThread.cancelled = False
		while not WorkerThread.cancelled and not sip.isdeleted(self):
			logger.info("text update start_thread while loop")
			#if time.time()-t0>self.updatePeriod_/1000:
			if time.time()-t0>self.updatePeriod_/1000 and main_thread.isAlive():
				self.timeout()
				logger.info(self.objectName()+":runCode duration: "+str(time.time()-t0))
				logger.info("update period: "+str(self.updatePeriod_))
				time.sleep(self.updatePeriod_/10000)
				#self.worker.wait(10)
				t0 = time.time()
			if not main_thread.isAlive():
				break
		logger.info("end of thread")

	def updateText(self, val):
		if val == None:
			#self.setText("unknown")
			self.updateTextSignal.emit("unknown")
			logger.info("setting text to unknown")
		else:
			self.setText(val)
			#self.updateTextSignal.emit(val)
	

	def default_code(self):
		return """
			from bsstudio.functions import widgetValue, fieldValue
			ui = self.ui
			try:
				v = widgetValue(fieldValue(self, "source"))
			except:
				v=None
			if v is not None:
				v = str(v)
			self.updateText(v)
			"""[1:]

	@Property(str, designable=True)
	def source(self):
		return self._source

	@source.setter
	def source(self, val):
		self._source = val

	def pauseWidget(self):
		self._paused = True

	def closeEvent(self, evt):
		logger.info("close Event")
		self.timer.stop()
		self.worker.cancel()
		while not self.worker.isFinished() and self.worker.isRunning():
			logger.info("worker not finished")
			time.sleep(2)
		super().closeEvent(evt)

	def resumeWidget(self):
		CodeObject.resumeWidget(self)
		t0 = time.time()
		self.updatePeriod_ = eval(self.updatePeriod)
		if self.threadMode == "qtimer":
			self.timer.setInterval(self.updatePeriod_)
			self.timer.start()
		elif self.threadMode == "qthread":
			self.worker.start()
		logger.info(str(time.time()-t0) +" seconds to start thread")

	updatePeriod = makeProperty("updatePeriod")
	updateTextSignal = pyqtSignal(str)


class TextUpdate(QLabel, TextUpdateBase):
	@Property(bool, designable=True)
	def runInThread(self):
		return self._useThreading

	@runInThread.setter
	def runInThread(self, val):
		self._useThreading = val


	def __init__(self, parent=None,*,sig=""):
		#self.parent = parent
		#super().__init__(parent)
		QLabel.__init__(self, parent)
		TextUpdateBase.__init__(self, parent, sig=sig)
		#self.setStyleSheet("border: 1px solid black;")
		#self.setLineWidth(1)
		#self.setAlignment(Qt.AlignHCenter)
		self.setAlignment(Qt.AlignCenter)
		self.setFrameShape(QFrame.Box)
		self.setFrameShadow(QFrame.Sunken)
		self.updateTextSignal.connect(self.setText)

