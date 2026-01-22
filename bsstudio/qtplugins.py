from PyQt5 import QtDesigner, QtGui, QtWidgets, QtCore
#from qtpy.QtWidgets import QLabel, QApplication, QDoubleSpinBox, QWidget, QPushButton
from PyQt5.QtWidgets import QLabel, QApplication, QDoubleSpinBox, QWidget, QPushButton, QPlainTextEdit, QWidget, QAction
#from qtpy.QtDesigner import QExtensionFactory
from PyQt5.QtDesigner import QExtensionFactory, QDesignerPropertyEditorInterface 
from PyQt5.QtCore import pyqtProperty as Property
from PyQt5.QtCore import QVariant, QCoreApplication
from PyQt5.QtCore import pyqtSlot, QObject
import inspect
from itertools import dropwhile
import textwrap
from .widgets import REButton, RECustomPlan, CodeButton, TextUpdate, MplWidget, Scan1DButton, EmbedFrame, LineInput
from .widgets import Base
from .widgets import CodeContainer
from .widgets import DataBrowser
from .widgets import OphydProperties
from .widgets import OpenWindowButton
from .widgets import ArrayImage
from .widgets import BooleanLED
from .widgets import BarUpdate
from .widgets import MBSTable
from PyQt5.QtDesigner import QPyDesignerTaskMenuExtension 
from PyQt5.Qt import Qt
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QTreeView, QFileSystemModel
import inspect
import bsstudio
from PyQt5.QtCore import QFile
from PyQt5.Qt import Qt
from PyQt5.QtDesigner import QDesignerFormWindowInterface
import time
#from . import git


#splash = QLabel("test")
#splash.setWindowFlags(Qt.SplashScreen)
#splash.show()
#splash.update()
#splash.repaint()
#time.sleep(60)

def clearLayout(layout):
	while layout.count():
		child = layout.takeAt(0)
		try:
			child.widget().hide()
			#if child.widget():
			#	child.widget().hide()
			#child.hide()
		except:
			None
		#if child.widget():
		#	child.widget().deleteLater()

global core

class EditTemplateMenuEntry(QPyDesignerTaskMenuExtension):

	def action(self):
		from PyQt5.QtWidgets import QMessageBox
		messageBox = QMessageBox(None)
		messageBox.setText("Coming soon...")
		self.messageBox = messageBox
		#self.messageBox.show()
		self.open_template()

	def open_template(self):
		#filename = "/home/bsobhani/bsw/bss_test83.ui"
		filename = self.widget.getAbsPath()
		#print(filename)
		file = QFile(filename)
		file.open(QFile.ReadWrite)
		#core.formWindowManager().activeFormWindow().setContents(file)
		#core.formWindowManager().addFormWindow(core.formWindowManager().createFormWindow())
		orig = core.formWindowManager().activeFormWindow()
		self.p = core.formWindowManager().activeFormWindow().parent()
		#self.p = QWidget()
		self.win = core.formWindowManager().createFormWindow(self.p,Qt.Widget)
		#print("win width", self.win.width())
		#print("win height", self.win.height())
		self.win.setContents(file)
		#print(self.win.contents())
		#print("win width", self.win.geometry().width())
		#print("win height", self.win.height())
		self.win.setHidden(False)
		#self.win.setVisible(True)
		self.win.setFileName(filename)
		self.win.show()
		
		core.formWindowManager().addFormWindow(self.win)
		core.formWindowManager().setActiveFormWindow(self.win)
		main = core.actionEditor().parent().parent().parent()
		mdiArea = main.children()[5]
		from PyQt5.QtWidgets import QMdiSubWindow
		self.subwindow = QMdiSubWindow(mdiArea)
		self.subwindow.setWidget(self.win)
		self.subwindow.show()

	def __init__(self, widget, parent):

		QPyDesignerTaskMenuExtension.__init__(self, parent)

		self.widget = widget
		self.editStateAction = QAction(self.tr("Edit template..."), self)
		self.editStateAction.triggered.connect(self.action)

	def preferredEditAction(self):
		return self.editStateAction

	def taskActions(self):
		return [self.editStateAction]

class EditCodeMenuEntry(QPyDesignerTaskMenuExtension):

  def __init__(self, widget, parent):

      QPyDesignerTaskMenuExtension.__init__(self, parent)

      self.widget = widget
      self.editStateAction = QAction(
          self.tr("Edit code..."), self)
      #self.connect(self.editStateAction,
      #    SIGNAL("triggered()"), self.updateLocation)

  def preferredEditAction(self):
      return self.editStateAction

  def taskActions(self):
      return [self.editStateAction]


class EditCodeTaskMenuFactory(QExtensionFactory):

  def __init__(self, parent = None):

      QExtensionFactory.__init__(self, parent)
      #print("factory...", self.createExtension)

  def createExtension(self, obj, iid, parent):
      #print("create extensions...")

      if iid != "org.qt-project.Qt.Designer.TaskMenu":
          return None

      if isinstance(obj, CodeButton):
          #print("wrhwrt")
          return EditCodeMenuEntry(obj, parent)

      if isinstance(obj, EmbedFrame):
          pass
          #return EditTemplateMenuEntry(obj, parent)
			

      return None

def debug_prompt(vars):
	while(True):
		cmd = input()
		if cmd == "q":
			break
		try:
			exec(cmd,vars)
		except:
			print("unable to run command")


core_initialized = False
def plugin_factory(cls, is_container=False):
	class PyBSPlugin(QtDesigner.QPyDesignerCustomWidgetPlugin):
		def __init__(self, cls):
			QtDesigner.QPyDesignerCustomWidgetPlugin.__init__(self)
			#print("init")
			self.cls = cls
			self.initialized = False
			self.is_container = is_container

		def name(self):
			return self.cls.__name__

		def group(self):
			return "BSStudio Widgets"

		def isContainer(self):
			return self.is_container

		def icon(self):
			return QtGui.QIcon()

		def toolTip(self):
			return "test"

		def includeFile(self):
			return self.cls.__module__

		def whatsThis(self):
			return "this"

		def createWidget(self, parent):
			w = self.cls(parent)
			w.core = self.core
			w.pauseWidget()
			return w

		
		def init_core(self):
			global core_initialized
			#print("core initialized", core_initialized)
			if core_initialized:
				return
			global core
			core = self.core
			children = core.formWindowManager().children()
			a = QAction("zzz",core.formWindowManager())

			#print("lllllllllgasdf")
			#print(core)
			#print(dir(core.formWindowManager()))
			app = QApplication.instance()
			app.setApplicationDisplayName("BS Studio")
			from PyQt5.QtWidgets import QLabel
			#self.asdf = QDockWidget()
			#self.asdf.show()
			#debug_prompt(locals())
			
			def try_until_successful(func):
				import threading
				thread = threading.Thread()
				def run_func():
					successful = False
					while not successful:
						try:
							func()
							successful = True
						except:
							None
				thread.run = run_func
				thread.start()
				#run_func()

			def make_git_context_menu():
				self.main = core.actionEditor().parent().parent().parent()
				self.menu = self.main.menuWidget().addMenu("aaaaaaaaa")
				git.make_menu(self.menu)
				#mainThread = QCoreApplication.instance().thread()
				#self.menu.moveToThread(mainThread)
				return self.menu

			def make_git():
				#self.asdf = QLabel("asdf")
				self.asdf = QTreeView()
				self.asdf.model = QFileSystemModel()
				self.asdf.model.setRootPath('')
				self.asdf.setModel(self.asdf.model)
				from PyQt5.QtWidgets import QTabWidget
				self.view = git.run()
				self.tabs = QTabWidget()
				self.tabs.addTab(self.view, "Files")
				self.commit_view = git.make_commit()
				self.tabs.addTab(self.commit_view, "Commit")
				### test
				#self.branches_view = git.make_branches()
				#self.tabs.addTab(self.branches_view, "Branches")
				#self.status_view = git.make_status()
				#core.actionEditor().layout().addWidget(self.view)
				def p2():
					clearLayout(core.actionEditor().layout())
					core.actionEditor().layout().addWidget(self.tabs)
					#make_git_context_menu()
				#try_until_successful(p2)
				p2()
				#core.actionEditor().layout().addWidget(self.commit_view)
				#core.actionEditor().layout().addWidget(self.status_view)
				#core.actionEditor().layout().addWidget(self.asdf)
				#self.asdf.show()
				#debug_prompt(locals())
				#self.view.show()
				#self.view.hide()
				#self.view.show()
				#self.view.repaint()


			#try_until_successful(make_git)

			def diff_between_objects(a, b):
				for k in dir(a):
					if getattr(a, k) != getattr(b, k):
						print(k, getattr(a, k), getattr(b, k))	
			


			def preview():
				import os
				#print("preview")
				core = self.core
				fileName = core.formWindowManager().activeFormWindow().fileName()
				path = os.path.dirname(inspect.getfile(bsstudio))

				#cmd = 'ipython --profile=collection --matplotlib=qt5 -c "'+path_import+'\nimport bsstudio\nbsstudio.load(\\"'+fileName+'\\", verbose=True)"'
				#cmd = 'bsui -c "'+path_import+'\nimport bsstudio\nbsstudio.load(\\"'+fileName+'\\", False, verbose=True)"'
				if os.system("type bsui")==0:
					#cmd = 'bsui -c "import bsstudio\nbsstudio.load(\\"'+fileName+'\\", False, verbose=True)"'
					cmd = 'bsui -c "from PyQt5.QtWidgets import QApplication; app = QApplication([]); import bsstudio\nbsstudio.load(\\"'+fileName+'\\", False, verbose=True)"'
				else:
					cmd = 'ipython --profile=collection --matplotlib=qt5 -c "\nimport bsstudio\nbsstudio.load(\\"'+fileName+'\\", verbose=True)"'
					
				#print(core.formWindowManager().children())
				os.system(cmd + " &")
				
				#debug_prompt(locals())
				#main.menuWidget().addMenu(git.git_menu())
				#make_git()
				
				#diff_between_objects(orig, self.win)
				#core.formWindowManager().actionVerticalLayout()
				#QDesignerFormWindowInterface(None,Qt.Dialog)
				#for c in core.children():
				#	print(c.dumpObjectInfo())

				#open_template()
				#p = core.formWindowManager().findChildren(QObject)

	
				
			p = core.formWindowManager().findChild(QAction, "__qt_default_preview_action")
			p.triggered.disconnect()
			p.triggered.connect(preview)
			#core.formWindowManager().formWindowAdded.connect(preview)
			#print("make git", p)
			#print(p.parent())
			#print(p.parent().children())
			#print(p.parent().parent().children())
			#print(p.parent().parent().parent())
			#print(p.parent().parent().parent().children())
			#debug_prompt(locals())
			
			
			core_initialized = True
			#make_git()

		def initialize(self, core):
			if self.initialized:
				return
			self.core = core
			self.init_core()

			self.manager = core.extensionManager()
			if self.manager:
				factory = EditCodeTaskMenuFactory(parent=self.manager)
				self.manager.registerExtensions(factory,'org.qt-project.Qt.Designer.TaskMenu')	
			self.initialized = True


	class Plugin(PyBSPlugin):
		def __init__(self):
			super(Plugin, self).__init__(cls)


	return Plugin

pCodeButton = plugin_factory(CodeButton)
#pREButton = plugin_factory(REButton)
pTextUpdate = plugin_factory(TextUpdate)
pMplWidget = plugin_factory(MplWidget)
pScan1DButton = plugin_factory(Scan1DButton)
pEmbedFrame = plugin_factory(EmbedFrame)
pLineInput = plugin_factory(LineInput)
pRECustomPlan = plugin_factory(RECustomPlan)
pCodeContainter = plugin_factory(CodeContainer, is_container=True)
pDataBrowser = plugin_factory(DataBrowser)
pOphydProperties = plugin_factory(OphydProperties)
pOpenWindowButton = plugin_factory(OpenWindowButton)
#pOpenWindowButton2 = plugin_factory(OpenWindowButton2)
pArrayImage = plugin_factory(ArrayImage)
pBooleanLED = plugin_factory(BooleanLED)
pBarUpdate = plugin_factory(BarUpdate)
pMBSTable = plugin_factory(MBSTable)

bluesky_widgets_installed = False
try:
	from .bluesky_widgets_conversion import ExampleAppConversion, QtSearchesConversion, QtFiguresConversion, QtTreeViewConversion
	bluesky_widgets_installed = True
except:
	None
if bluesky_widgets_installed:
	#pExampleApp = plugin_factory(ExampleAppConversion)
	pQtSearches = plugin_factory(QtSearchesConversion)
	pQtTreeView = plugin_factory(QtTreeViewConversion)
	#pQtFigures = plugin_factory(QtFiguresConversion)
