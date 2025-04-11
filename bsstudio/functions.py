from PyQt5.QtWidgets import QWidget, QComboBox, QSpinBox, QDoubleSpinBox, QCheckBox, QLineEdit, QMessageBox
#from bluesky.callbacks import LivePlot, LiveGrid
import bsstudio.window
import matplotlib.pyplot as plt
from collections.abc import Iterable
import time
import re
from IPython import get_ipython
from .lib.pydollarmacro import pydollarmacro
from functools import partial
from io import StringIO

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def deleteWidgetAndChildren(w):
	#w.setParent(None)
	for c in w.children():
		#c.setParent(None)
		c.deleteLater()
	w.deleteLater()

class dotdict(dict):
	__getattr__ = dict.get
	__setattr__ = dict.__setitem__
	__delattr__ = dict.__delitem__

def alert(message):
	mb = QMessageBox(bsstudio.window.getMainWindow())
	mb.setText(message)
	mb.show()

gto_hash = {}

def getTopObject(w):
	#import importlib
	#importlib.reload(bsstudio.window)
	from .window import isMainWindow
	if w in gto_hash.keys():
		return gto_hash[w]
	obj = w.parentWidget()
	count = 0
	while True:
		if hasattr(obj, "isTopLevel"):
			if obj.isTopLevel==True:
				break
		if isMainWindow(obj):
			while not obj.isLoaded:
				time.sleep(1)
				logger.info("sleeping for 1 second")
			break
		#logger.info("getTopObject while loop iteration "+str(count))
		if obj.parentWidget() is None:
			logger.error("Object has None parent: " + str(obj) + obj.objectName())
		obj = obj.parentWidget()
	gto_hash[w] = obj
	return obj


def makeUiFunction(self):
	def ui():
		if 1==1 and ui.ui_hash != None:
			return ui.ui_hash
		obj = getTopObject(self)
		children = obj.findChildren(QWidget)
		children = [c for c in children if obj == getTopObject(c)] #commented out for performance
		#for c in children:
		#	print(getTopObject(c), obj, getTopObject(c).objectName(), obj.objectName(), getTopObject(c)==obj)
		d = {c.objectName(): c for c in children}
		d["parent"] = obj.parent
		def parentUi():
			return obj.parent().ui()
		d["parentUi"] = parentUi
		

		d = dotdict(d)
		ui.ui_hash = d
		return d
	ui.ui_hash = None
	return ui

def defaultValueField(w):
	if isinstance(w, QComboBox):
		return "currentText"
	if isinstance(w, QCheckBox):
		return "isChecked"
	if isinstance(w, QSpinBox):
		return "value"
	if isinstance(w, QDoubleSpinBox):
		return "value"
	if issubclass(w.__class__, QLineEdit):
		return "text"

	return None

def fieldValueAsString_(w, field):
	prop = w.property(field)
	if prop == None:
		return str(getattr(w, field)())
	return str(w.property(field))

def fieldValueAsString(w, field):
	#try:
	#	return fieldValueAsString_(w,field)
	#except:
	#	logger.warn("unable to get value for field "+field+" as string")
	#	return None
	return fieldValueAsString_(w,field)

def evalInNs(w, cmd):
	try:
		ip = get_ipython()
		ns = ip.user_ns.copy()
		ns['self'] = w
		ui = makeUiFunction(w)
		ns["ui"] = ui
		logger.info("evaluating command in namespace: "+cmd)
		return eval(cmd, ns)

	except:
		#logger.warn("unable to evaluate command "+str(cmd)+" in namespace")
		return None

	"""
	ip = get_ipython()
	ns = ip.user_ns.copy()
	ns['self'] = w
	#if hasattr(w, "mui_hash"):
	#	#print("caught")
	#	ui = w.mui_hash
	#else:
	#	#print("not caught")
	#	ui = makeUiFunction(w)
	#	w.mui_hash = ui
	try:
		ui = w.ui
	except:
		return None
	ns["ui"] = ui
	logger.info("evaluating command in namespace: "+cmd)
	"""
	return eval(cmd, ns)





def fieldValue(w, field):
	return evalInNs(w, fieldValueAsString(w, field))

def comboBoxValue(w):
	key = w.currentText()
	prop = w.property(key)
	if prop == None:
		key = "currentText"
	return fieldValue(w, key)
	
	
def widgetValueString(self, w_string, continuous=False):
	#ui = makeUiFunction(w)
	w = evalInNs(self, w_string)
	logger.debug("w in widgetValueString", w)
	if type(w) is list:
		return [widgetValueString(x, continuous) for x in w]
	if not isWidget(w):
		return w_string
	return widgetValue(w, continuous, asString=True)


def widgetValue(w, continuous=False,*,asString=False):
	if type(w) is list:
		return [widgetValue(x, continuous) for x in w]
	if type(w) is dict:
		return {k : widgetValue(w[k], continuous) for k in w.keys()}
	if not isWidget(w):
		return w
	prop = w.property("valueField")
	if prop == None:
		prop = defaultValueField(w)
	if isinstance(w, QComboBox):
		wv = comboBoxValue(w)
	else:
		wv = fieldValue(w, prop)
	wv_string = fieldValueAsString(w, prop)

	if not isWidget(wv) and asString:
		return wv_string
	if continuous:
		return widgetValue(wv, True, asString=asString)
	return wv



def isWidget(obj):
	return issubclass(obj.__class__, QWidget)
	
def makeLivePlots(plots, plotFields, plotKwargsList):
	from bluesky.callbacks import LivePlot, LiveGrid
	logger.info("plotFields"+str(plotFields))
	if plotFields is None or plotFields == [[]]:
		return []
	plotKwargsList = plotKwargsList + [{}]*(len(plots)-len(plotKwargsList))
	livePlots = []
	for i in range(len(plots)):
		plot_tuple = plots[i]
		if not isinstance(plot_tuple, Iterable):
			plot_tuple = (plot_tuple, "LivePlot")
		plotWidget,cls = plot_tuple
		if cls == "LiveGrid":
			plotWidget.canvas.wipe()
		p = plotFields[i]
		plotKwargs = plotKwargsList[i]
		plotKwargs["ax"] = plotWidget.canvas.ax
		lp = eval(cls)(*p, **plotKwargs)
		livePlots.append(lp)
	return livePlots

def plotHeader(livePlot, header):
	livePlot.start(header.start)
	for e in header.events():
		livePlot.event(e)
	return livePlot.ax

def plotLPList(y_list, header, samePlot=False):
	from bluesky.callbacks import LivePlot
	ax = None
	for y in y_list:
		ax_p = plotHeader(LivePlot(y, ax=ax), header)
		if samePlot:
			ax = ax_p

def openFileAsString(filename, macros=[]):
	try:
		file_obj = open(filename)
		fileContents = file_obj.read()
		file_obj.close()
	except:
		logger.debug("Read error")
		return

	macro_dict = {}
	for m in macros:
		left, right = m.split(":", 1)
		macro_dict[left] = right
		#fileContents = fileContents.replace("$("+left+")", right)
		#fileContents = fileContents.replace("$("+left+")", right)
	fileContents = pydollarmacro.subst_str_all(fileContents, macro_dict)
	return fileContents


def getFunctionStdOut(*args, **kwargs):
	f = partial(*args, **kwargs)
	import sys
	old_stdout = sys.stdout
	result = StringIO()
	sys.stdout = result
	f()
	result_string = result.getvalue()
	sys.stdout = old_stdout

	return result_string

def pop(ophydObject):
	import epics
	value = ophydObject.get()
	epics.pv._PVcache_[ophydObject._read_pv._cache_key].clear_callbacks()
	return value
	
