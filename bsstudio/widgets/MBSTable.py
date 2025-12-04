import os
import numpy as np
import csv
from .Base import BaseWidget
from . import CodeContainer
from .REButton import makeProperty
from .channelsbox import ChannelsBox
from .channelsbox import ScrollMessageBox
from PyQt5.QtCore import QDateTime
from PyQt5.Qt import Qt
from PyQt5.QtWidgets import QDateTimeEdit
from PyQt5 import QtCore
from PyQt5.QtCore import QThread
from PyQt5.QtCore import QTimer
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QSizePolicy
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QMenu, QAction
from PyQt5.QtWidgets import QAbstractItemView
from PyQt5.QtWidgets import QScrollArea
from PyQt5.QtWidgets import QCheckBox
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QWidget, QDialog
from PyQt5.QtWidgets import QListWidget, QTableWidget, QTableWidgetItem, QFrame, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QComboBox, QCheckBox
from PyQt5.QtGui import QColor, QBrush
from bsstudio.functions import widgetValue, plotHeader, plotLPList, evalInNs, getFunctionStdOut
from collections.abc import Iterable
from functools import partial
import time
import logging

#from ~/.ipython/profile_collection/startup/30-detectors import mbs



logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)



class MBSTable(CodeContainer):
	def __init__(self, parent):
		super().__init__(parent)
		self._tableColumns = ''
		layout = QVBoxLayout()
		layout_space = QVBoxLayout()
		layout_h = QHBoxLayout()
		self.sequence_TW = QTableWidget()

		self.sequence_TW.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		self.sequence_TW.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

		self.sequence_TW.setRowCount(6)
		self.sequence_TW.setColumnCount(17)
		self.sequence_TW.setColumnWidth(0,30)	# RE checkbox
		self.sequence_TW.setColumnWidth(1,60)	# Name
		self.sequence_TW.setColumnWidth(2,70)	# Start_KE
		self.sequence_TW.setColumnWidth(3,70)	# End_KE
		self.sequence_TW.setColumnWidth(4,70)	# Width
		self.sequence_TW.setColumnWidth(5,70)	# Cntr
		self.sequence_TW.setColumnWidth(6,80)	# PE
		self.sequence_TW.setColumnWidth(7,110)	# Lens
		self.sequence_TW.setColumnWidth(8,70)	# Acq
		self.sequence_TW.setColumnWidth(9,60)	# En_step
		self.sequence_TW.setColumnWidth(10,55)	# t_step
		self.sequence_TW.setColumnWidth(11,40)  # n_scans
		self.sequence_TW.setColumnWidth(12,100)	# t-tot
		self.sequence_TW.setColumnWidth(13,30)  # 3D checkbox
		self.sequence_TW.setColumnWidth(14,55)	# Start_A
		self.sequence_TW.setColumnWidth(15,55)	# End_A
		self.sequence_TW.setColumnWidth(16,75)	# A-step

		self.sequence_TW.setHorizontalHeaderLabels(['RE','Name','LKE','HKE','Width','Ctr', 'Pass En',\
								 'Lens', 'Acq', 'dE (mV) ', 'dt (s)', 'Scn', 'tot-t',\
								'3D', 'Ai', 'Af', 'dA'])

		for r in range(self.sequence_TW.rowCount()):
			for c in range(self.sequence_TW.columnCount()):
				#if c == 0:
				#	C_B = QCheckBox()
				#	self.sequence_TW.setCellWidget(r,c, C_B)
				if c == 6:
					C_B = QComboBox()
					C_B.addItems(['PE001', 'PE002', 'PE005', 'PE010', 'PE020', 'PE030', 'PE050', 'PE100', 'PE200'])
					C_B.setCurrentIndex(4)
					self.sequence_TW.setCellWidget(r,c, C_B)
				elif c == 7:
					C_B = QComboBox()
					C_B.addItems(['L4Ang0d8','L4Ang1d6', 'L4Ang3d9', 'L4MAng0d7', 'L4MSpat5'])
					C_B.setCurrentIndex(0)
					self.sequence_TW.setCellWidget(r,c, C_B)
				elif c == 8:
					C_B = QComboBox()
					C_B.addItems(['Fixed','FixedTrigd','Swept', 'Dither'])
					C_B.setCurrentIndex(2)
					self.sequence_TW.setCellWidget(r,c, C_B)
				#elif c == 13:
				#	CB_3D = QCheckBox()
				#	self.sequence_TW.setCellWidget(r,c, CB_3D)
				else:
					TW = QTableWidgetItem()
					self.sequence_TW.setItem(r,c, TW)
					if c==0 or c==13:
						try:
							self.sequence_TW.item(r,c).setFlags(self.sequence_TW.item(r,c).flags() | QtCore.Qt.ItemIsUserCheckable)
							self.sequence_TW.item(r,c).setCheckState(QtCore.Qt.CheckState.Unchecked)
						except Exception as e:
							print(e)
					if c == 9:
						self.sequence_TW.item(r,c).setText('5')
					if c == 10:
						self.sequence_TW.item(r,c).setText('0.1')
					if c == 11:
						self.sequence_TW.item(r,c).setText('1')
					if c in [14, 15, 16]:
						self.sequence_TW.item(r,c).setFlags(Qt.ItemIsEnabled)

		#now = QDateTime.currentDateTime()
		#self.startDateTime = QDateTimeEdit(now.addMonths(-6))
		#self.endDateTime = QDateTimeEdit(now)
		#buttonText = "Load Scans"
		#self.loadScansButton = QPushButton(buttonText)
		#layout.addWidget(self.startDateTime)
		#layout.addWidget(self.endDateTime)
		#layout.addWidget(self.loadScansButton)
		layout.addWidget(self.sequence_TW)
		layout.addSpacing(20) 

		try:
			with open('current_file.csv', 'r', newline='') as file:
				csv_reader = csv.reader(file)
				for row in csv_reader:
#					print(row)
					self.dir_le = QLineEdit(row[0])
					self.file_le = QLineEdit(row[1])
					self.num_le = QLineEdit(row[2])
					self.usr_le = QLineEdit(row[3])
		except:
			self.dir_le = QLineEdit('/nsls2/data/esm/legacy/image_files/spectrum_analyzer')
			self.file_le = QLineEdit('name')
			self.num_le = QLineEdit('0001')
			self.usr_le = QLineEdit('')

		self.dir_le.setStyleSheet("QLineEdit {background-color: orange; color:blue;}")
		self.file_le.setStyleSheet("QLineEdit {background-color: orange; color:blue;}")
		self.num_le.setStyleSheet("QLineEdit {background-color: yellow; color:blue;}")
		self.usr_le.setStyleSheet("QLineEdit {background-color: orange; color:blue;}")

		self.usr_lbl = QLabel('usr:')
		self.dir_lbl = QLabel('dir:')
		self.file_lbl = QLabel('name:')
		self.num_lbl = QLabel('#:')
		self.nxs_lbl = QLabel('.nxs')

		layout_h.addWidget(self.usr_lbl)
		layout_h.addWidget(self.usr_le)
		layout_h.addWidget(self.dir_lbl)
		layout_h.addWidget(self.dir_le)
		layout_h.addWidget(self.file_lbl)
		layout_h.addWidget(self.file_le)
		layout_h.addWidget(self.num_lbl)
		layout_h.addWidget(self.num_le)
		layout_h.addWidget(self.nxs_lbl)
		layout.addLayout(layout_h)
		layout.addSpacing(20) 

		self.setLayout(layout)

		self.sequence_TW.itemChanged.connect(self.cell_changed)
		[self.sequence_TW.cellWidget(i,7).currentTextChanged.connect(self.CB_lens_changed) for i in range(6)] # ComboBox Lens mode changed  
		[self.sequence_TW.cellWidget(i,8).currentTextChanged.connect(self.CB_changed) for i in range(6)] # ComboBox Acquisition mode changed  
		self.dir_le.returnPressed.connect(self.dirname_changed)
		self.file_le.returnPressed.connect(self.filename_changed)


	def showScrollBox(self, text):
		messageBox = ScrollMessageBox(self)
		messageBox.content.setText(text)
		messageBox.show()

	def default_code(self):
		return """
				ui = self.ui
				from functools import partial
				from bsstudio.functions import widgetValue
				from bsstudio.functions import makeLivePlots 
			"""[1:]

	def cell_changed(self, itm):
#		print('--> cell_changed')
		r,c = itm.row(), itm.column() 
#		print('row,column=({},{})={}'.format(r,c,type(itm) ))
		if c == 2 or c == 3:
			try: 
				LE, HE = float(self.sequence_TW.item(r,2).text()), float(self.sequence_TW.item(r,3).text())
			except:
				return
			if LE < HE :
				self.sequence_TW.blockSignals(True)
				self.sequence_TW.item(r,4).setText('{:.4f}'.format(HE-LE) )
				self.sequence_TW.item(r,5).setText('{:.4f}'.format((HE+LE)/2) )
				self.sequence_TW.blockSignals(False)
		if c == 4 or c == 5:
			try: 
				WE, CE = float(self.sequence_TW.item(r,4).text()), float(self.sequence_TW.item(r,5).text())
			except:
				return
			if WE > 0 and CE > WE/2:
				self.sequence_TW.blockSignals(True)
				self.sequence_TW.item(r,3).setText('{:.4f}'.format( CE+WE/2 ) )
				self.sequence_TW.item(r,2).setText('{:.4f}'.format( CE-WE/2 ) )
				self.sequence_TW.blockSignals(False)

		if c == 9:
			de = 0.001*float(self.sequence_TW.item(r,9).text())
			ctr = float(self.sequence_TW.item(r,5).text())
			w = float(self.sequence_TW.item(r,4).text())
			if int(w/de)%2 == 0:
				np = int(w/de)
			else:
				np = int(w/de)+1 
			self.sequence_TW.item(r,2).setText('{:.4f}'.format( ctr-(np/2)*de ) )
			self.sequence_TW.item(r,3).setText('{:.4f}'.format( ctr+(np/2)*de ) ) 
			self.sequence_TW.item(r,4).setText('{:.2f}'.format( np*de ) )
			self.sequence_TW.blockSignals(False)

		if c == 10:
			ms_value = 1000*float(self.sequence_TW.item(r,10).text())
			if 1< ms_value <= 100 or (ms_value > 100 and int(ms_value)%100 == 0):
				frames = int(ms_value)/1000.0
			else:
				frames = (( (int(ms_value)//100) +1) *100)/1000.0
			self.sequence_TW.blockSignals(True)
			self.sequence_TW.item(r,10).setText('{:.4f}'.format(frames)) 
			self.sequence_TW.blockSignals(False)

		if c == 13:
			if itm.checkState() == QtCore.Qt.CheckState.Checked:
				self.sequence_TW.item(r,14).setFlags(Qt.ItemIsEnabled|Qt.ItemIsSelectable|Qt.ItemIsEditable)
				self.sequence_TW.item(r,14).setForeground(QBrush(QColor("black")))
				self.sequence_TW.item(r,15).setFlags(Qt.ItemIsEnabled|Qt.ItemIsSelectable|Qt.ItemIsEditable)
				self.sequence_TW.item(r,15).setForeground(QBrush(QColor("black")))
				self.sequence_TW.item(r,16).setFlags(Qt.ItemIsEnabled|Qt.ItemIsSelectable|Qt.ItemIsEditable)
				self.sequence_TW.item(r,16).setForeground(QBrush(QColor("black")))
				self.sequence_TW.setCurrentCell(r,14)
			else:
				self.sequence_TW.item(r,14).setFlags(Qt.ItemIsEnabled)
				self.sequence_TW.item(r,14).setForeground(QBrush(QColor("grey")))
				self.sequence_TW.item(r,15).setFlags(Qt.ItemIsEnabled)
				self.sequence_TW.item(r,15).setForeground(QBrush(QColor("grey")))
				self.sequence_TW.item(r,16).setFlags(Qt.ItemIsEnabled)
				self.sequence_TW.item(r,16).setForeground(QBrush(QColor("grey")))
				self.sequence_TW.setCurrentCell(r,5)
#		print('<-- cell_changed')


	def CB_changed(self, txt):
#		print('--> CB_changed')
		r,c = self.sequence_TW.currentRow(), self.sequence_TW.currentColumn() 
#		print('row,column=({},{})={}'.format(r,c, txt ))
		self.sequence_TW.blockSignals(True)


		if txt in ['Fixed', 'FixedTrigd','Dither']:
			self.sequence_TW.item(r,2).setFlags(Qt.ItemIsEnabled)
			self.sequence_TW.item(r,2).setForeground(QBrush(QColor("grey")))
			self.sequence_TW.item(r,3).setFlags(Qt.ItemIsEnabled)
			self.sequence_TW.item(r,3).setForeground(QBrush(QColor("grey")))
			self.sequence_TW.item(r,4).setFlags(Qt.ItemIsEnabled)
			self.sequence_TW.item(r,4).setForeground(QBrush(QColor("grey")))
			self.sequence_TW.item(r,9).setFlags(Qt.ItemIsEnabled)
			self.sequence_TW.item(r,9).setForeground(QBrush(QColor("grey")))
			self.sequence_TW.setCurrentCell(r,5)

		elif txt == 'Swept':
			self.sequence_TW.item(r,2).setFlags(Qt.ItemIsEnabled|Qt.ItemIsSelectable|Qt.ItemIsEditable)
			self.sequence_TW.item(r,2).setForeground(QBrush(QColor("black")))
			self.sequence_TW.item(r,3).setFlags(Qt.ItemIsEnabled|Qt.ItemIsSelectable|Qt.ItemIsEditable)
			self.sequence_TW.item(r,3).setForeground(QBrush(QColor("black")))
			self.sequence_TW.item(r,4).setFlags(Qt.ItemIsEnabled|Qt.ItemIsSelectable|Qt.ItemIsEditable)
			self.sequence_TW.item(r,4).setForeground(QBrush(QColor("black")))
			self.sequence_TW.item(r,9).setFlags(Qt.ItemIsEnabled|Qt.ItemIsSelectable|Qt.ItemIsEditable)
			self.sequence_TW.item(r,9).setForeground(QBrush(QColor("black")))
			self.sequence_TW.setCurrentCell(r,2)

		self.sequence_TW.blockSignals(False)
#		print('<-- CB_changed')


	def CB_lens_changed(self, txt):
#		print('--> CB_lens_changed')
		r,c = self.sequence_TW.currentRow(), self.sequence_TW.currentColumn() 
#		print('row,column=({},{})={}'.format(r,c, txt ))
		if txt == 'L4MSpat5':
			self.sequence_TW.item(r,13).setCheckState(QtCore.Qt.CheckState.Checked)
			self.sequence_TW.blockSignals(True)
			if self.sequence_TW.item(r,14).text() =='': 
				self.sequence_TW.item(r,14).setText('{:.4f}'.format(-2.63)) 
			if self.sequence_TW.item(r,15).text() =='': 
				self.sequence_TW.item(r,15).setText('{:.4f}'.format(2.63)) 
			if self.sequence_TW.item(r,16).text() =='': 
				self.sequence_TW.item(r,16).setText('{:.4f}'.format(2*2.63/101)) 
			self.sequence_TW.blockSignals(False)

			self.sequence_TW.cellWidget(r,8).setCurrentIndex(1)  #change to FixedTrig mode

#			self.sequence_TW.setCurrentCell(r,14)
#		print('<-- CB_lens_changed')



	def filename_changed(self):
#		print('--> filename_changed')
#		dir ='/nsls2/data3/esm/legacy/image_files/spectrum_analyzer/' + self.dir_le.text() 
		dir ='/nsls2/data3/esm/legacy/csv_files/XPS/2025/' + self.dir_le.text() 
		nm = self.file_le.text()

		l = os.listdir(dir)

		files = []
		for entry in l:
			full_path = os.path.join(dir, entry)
			if os.path.isfile(full_path):
				files.append(entry)

		l_nm  = []
		for el in files:
			if nm in el:
				l_nm .append(int(el.split('_')[1][:-4])) 
		if len(l_nm) == 0:
			self.num_le.setText('001')
		else:
			i = max(l_nm)
			if 0<i<=9:
				self.num_le.setText('00'+'{}'.format(i))
			elif 10<=i<=99:
				self.num_le.setText('0'+'{}'.format(i))
			elif 100<=i<=999:
				self.num_le.setText('{}'.format(i))


		with open('current_file.csv', 'w', newline='') as file:
    			csv_writer = csv.writer(file)
    			csv_writer.writerows([[self.dir_le.text(), nm, self.num_le.text(), self.usr_le.text()]])
#		print('<-- filename_changed')

	def dirname_changed(self):
		print('--> direname_changed')
#		dir =self.dir_le.text() 
#		dir ='/nsls2/data3/esm/legacy/image_files/spectrum_analyzer/' + self.dir_le.text() 
		dir ='/nsls2/data3/esm/legacy/csv_files/XPS/2025/' + self.dir_le.text() 
		nm = self.file_le.text()
		try:
			os.makedirs(dir, exist_ok=True)
			print(f"Directory '{dir}' created or already exists.")
		except OSError as e:
			print(f"Error creating directory '{dir}': {e}")
			return
		self.filename_changed()

#		print('<-- dirname_changed')


	def num_increase(self):
#		print('--> num_increase')
#		dir ='/nsls2/data3/esm/legacy/image_files/spectrum_analyzer/' + self.dir_le.text() 
		dir ='/nsls2/data3/esm/legacy/csv_files/XPS/2025/' + self.dir_le.text() 
		nm = self.file_le.text()

		l = os.listdir(dir)
		files = []
		for entry in l:
			full_path = os.path.join(dir, entry)
			if os.path.isfile(full_path) and entry[0:3] !='XY_':
				files.append(entry)

		l_nm  = []
		for el in files:
			if nm in el:
				l_nm .append(int(el.split('_')[1][:-4])) 
		if len(l_nm) == 0:
			self.num_le.setText('001')
		else:
			i = max(l_nm)+1
			if 0<i<=9:
				self.num_le.setText('00'+'{}'.format(i))
			elif 10<=i<=99:
				self.num_le.setText('0'+'{}'.format(i))
			elif 100<=i<=999:
				self.num_le.setText('{}'.format(i))


		with open('current_file.csv', 'w', newline='') as file:
    			csv_writer = csv.writer(file)
    			csv_writer.writerows([[self.dir_le.text(), nm, self.num_le.text(), self.usr_le.text()]])
#		print('<-- num_increase')
