#! /usr/bin/python

import sys
import os
import math
import datetime
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import ControlWindow
import SceneWindow

class MainControlWindow(QMainWindow, ControlWindow.Ui_ControlWindow):
	
	"""
	This is the main window of the program.
	"""
	
	def __init__(self, parent=None):
		QMainWindow.__init__(self, parent)
		ControlWindow.Ui_ControlWindow.__init__(self, parent)
		
		# Build the main window using the setupUi method generated by Qt Designer
		self.setupUi(self)

		# Grab the current date for the filename
		now = datetime.datetime.now()
		dateStr = '-'.join([str(now.year), str(now.month), str(now.day)])
		timeStr = ''.join(['%02d' % now.hour, '%02d' % now.minute, '%02d' % now.second])
		self.fname_prefix = '_'.join([dateStr, timeStr])

		# Start with the "invert" action unchecked
		self.action_invert.setChecked(False)

		# Create the window that will show the scene
		self.sceneWindow = MainSceneWindow(parent=self)
		self.sceneWindow.show()
		
		# Connections
		self.connect(self.action_invert, SIGNAL("toggled(bool)"), self.sceneWindow.updateProperties)
		self.connect(self.filled_checkBox, SIGNAL("stateChanged(int)"), self.sceneWindow.updateProperties)
		self.connect(self.slingSize_spinBox, SIGNAL("valueChanged(int)"), self.sceneWindow.updateProperties)
		self.connect(self.centerSize_spinBox, SIGNAL("valueChanged(int)"), self.sceneWindow.updateProperties)
		self.connect(self.radius_spinBox, SIGNAL("valueChanged(int)"), self.sceneWindow.updateProperties)
		self.connect(self.thickness_spinBox, SIGNAL("valueChanged(int)"), self.sceneWindow.updateProperties)
		self.connect(self.aVelocity_doubleSpinBox, SIGNAL("valueChanged(double)"), self.sceneWindow.updateParameters)
		self.connect(self.distance_doubleSpinBox, SIGNAL("valueChanged(double)"), self.sceneWindow.updateParameters)
		self.connect(self.diameter_doubleSpinBox, SIGNAL("valueChanged(double)"), self.sceneWindow.updateParameters)
		self.connect(self.density_doubleSpinBox, SIGNAL("valueChanged(double)"), self.sceneWindow.updateParameters)
		self.connect(self.viscosity_doubleSpinBox, SIGNAL("valueChanged(double)"), self.sceneWindow.updateParameters)
		self.connect(self.engage_pushButton, SIGNAL("clicked()"), self.sceneWindow.startRotation)
		self.connect(self.record_pushButton, SIGNAL("clicked()"), self.saveData)

	def saveData(self):
		"""
		Save parameters to disk
		"""
		
		fname = self.fname_prefix + '_SlingTest' + '.dat' 
		if os.path.isfile(fname):
			# Open in append mode
			file = open(fname, 'a')
		else:
			# Open in write mode (create the file) and write header
			file = open(fname, 'w')
			
			slingSizeHead = 'Sling Size'
			centerSizeHead = 'Center Size'
			radiusHead = 'Radius'
			thicknessHead = 'Thickness'
			angularVelocityHead = 'AngularVelocity (rps)'
			distanceHead = 'Distance (um)'
			densityHead = 'Density (g/cm3)'
			diameterHead = 'Particle diameter (um)'
			viscosityHead = 'Viscosity (mPa s)'
			linearVelocityHead = 'Linear velocity (um/s)'
			depHead = 'DEP (pN)'
			centripetalForceHead = 'Centripetal force (pN)'
			header = '\t'.join(['# ' + slingSizeHead, centerSizeHead, radiusHead, thicknessHead, angularVelocityHead, distanceHead, densityHead, diameterHead, viscosityHead, linearVelocityHead, depHead, centripetalForceHead])
			file.write('# The Wheel test\n')
			file.write(header + '\n\n')
		
		# Write the values
		slingSize = str(self.slingSize_spinBox.value())				# pixels
		centerSize = str(self.centerSize_spinBox.value())			# pixels
		radius = str(self.radius_spinBox.value())					# pixels
		thickness = str(self.thickness_spinBox.value())				# pixels
		angularVelocity = str(self.aVelocity_doubleSpinBox.value())	# rps
		distance = str(self.distance_doubleSpinBox.value())			# um
		density = str(self.density_doubleSpinBox.value())			# g/cm3
		diameter = str(self.diameter_doubleSpinBox.value())			# um
		viscosity = str(self.viscosity_doubleSpinBox.value())		# mPa s
		linearVelocity = str(self.lVelocity_LCDNumber.value())		# um/s
		dep = str(self.DEPForce_LCDNumber.value())					# pN
		centripetalForce = str(self.cForce_LCDNumber.value())		# pN
		recordLine = '\t'.join([slingSize, centerSize, radius, thickness, angularVelocity, distance, density, diameter, viscosity, linearVelocity, dep, centripetalForce])
		file.write(recordLine + '\n')
			
		file.close()
		
		self.statusbar.showMessage("Saved to file " + fname)


class MainSceneWindow(QMainWindow, SceneWindow.Ui_SceneWindow):
	"""
	This is the window that shows the scene
	"""
	
	def __init__(self, parent=None):
		QDialog.__init__(self, parent)
		SceneWindow.Ui_SceneWindow.__init__(self, parent)
		
		# Build the window using the setupUi method generated by Qt Designer
		self.setupUi(self)

		# Create the scene and visualize it
		self.scene = self.createScene()
		self.graphicsView.setScene(self.scene)

	def createScene(self):
		"""
		Create the scene
		"""
		
		# Create the scene and set some basic properties
		scene = QGraphicsScene(parent=self)
		scene.setSceneRect(-1920/2, -1080/2, 1920, 1080)
		thickness = self.parent().thickness_spinBox.value()
		slingSize = self.parent().slingSize_spinBox.value()
		centerSize = self.parent().centerSize_spinBox.value()
		radius = self.parent().radius_spinBox.value()
		filled = self.parent().filled_checkBox.isChecked()
		inverted = self.parent().action_invert.isChecked()
		
		if inverted:
			scene.setBackgroundBrush(Qt.white)
			pen = QPen(Qt.black, thickness)
			foregroundBrush = QBrush(Qt.black)
			backgroundBrush = QBrush(Qt.white)
		else:
			scene.setBackgroundBrush(Qt.black)
			pen = QPen(Qt.white, thickness)
			foregroundBrush = QBrush(Qt.white)
			backgroundBrush = QBrush(Qt.black)

		# Create the items
		slingCircle = QGraphicsEllipseItem(-radius-slingSize/2.0, -slingSize/2.0, slingSize, slingSize)
		centralCircle = QGraphicsEllipseItem(-centerSize/2.0, -centerSize/2.0, centerSize, centerSize)
		self.itemList = [slingCircle, centralCircle]
		for item in self.itemList:
			item.setPos(0, 0)
		
		# Set colours and positions
		for item in self.itemList:
			item.setPen(pen)
			if filled:
				item.setBrush(foregroundBrush)
			else:
				item.setBrush(backgroundBrush)
		
		#wheel.setFlags(QGraphicsItem.GraphicsItemFlags(1)) # Make the item movable
		
		# Add the items to the scene
		for item in self.itemList:
			scene.addItem(item)
		
		# Create a running variable that will be used to determine the rotation angle of the wheel
		self.slingAngle = 0.0
		
		# Make the calculations with the initial values
		self.updateParameters()
		
		return scene

	def updateProperties(self):
		"""
		Update the properties of the scene
		"""
		
		# Read the properties from the SpinBoxes
		thickness = self.parent().thickness_spinBox.value()
		slingSize = self.parent().slingSize_spinBox.value()
		centerSize = self.parent().centerSize_spinBox.value()
		radius = self.parent().radius_spinBox.value()
		filled = self.parent().filled_checkBox.isChecked()
		inverted = self.parent().action_invert.isChecked()
		
		# Set the background and foreground color according to the status of the "invert" menu
		if inverted:
			self.scene.setBackgroundBrush(Qt.white)
			pen = QPen(Qt.black, thickness)
			foregroundBrush = QBrush(Qt.black)
			backgroundBrush = QBrush(Qt.white)
		else:
			self.scene.setBackgroundBrush(Qt.black)
			pen = QPen(Qt.white, thickness)
			foregroundBrush = QBrush(Qt.white)
			backgroundBrush = QBrush(Qt.black)
		
		for item in self.itemList:
			item.setPen(pen)
			if filled:
				item.setBrush(foregroundBrush)
			else:
				item.setBrush(backgroundBrush)

		# Set the sizes and position
		self.itemList[0].setRect(-radius-slingSize/2.0, -slingSize/2.0, slingSize, slingSize)
		self.itemList[1].setRect(-centerSize/2.0, -centerSize/2.0, centerSize, centerSize)

	def startRotation(self):
		"""
		Start the rotation of the wheel
		"""

		unitRotation = 0.1 # seconds
		timeline = QTimeLine(unitRotation * 1000)
		timeline.setFrameRange(0, 1)
		timeline.setUpdateInterval(1)
		timeline.setCurveShape(3)
		self.rotation = QGraphicsItemAnimation()
		self.rotation.setTimeLine(timeline)
		
		self.connect(timeline, SIGNAL("finished()"), self.startRotation)
		self.connect(self.parent().stop_pushButton, SIGNAL("clicked()"), timeline.stop)
		
		angularV = self.parent().aVelocity_doubleSpinBox.value()
		initial = self.slingAngle
		if initial > 360:
			initial -= 360
		final = initial + angularV * 360 * unitRotation
		self.slingAngle = final
		
		self.rotation.setRotationAt(0, initial)
		self.rotation.setRotationAt(1, final)
		self.rotation.setItem(self.itemList[0])
		timeline.start()

	def updateParameters(self):
		"""
		Update the linear velocity, DEP and centripetal forces according to the	values of the parameters
		"""
		
		# Linear velocity
		aVelocity_SI = self.parent().aVelocity_doubleSpinBox.value() * 2 * math.pi	# rad/s
		lVelocity = aVelocity_SI * self.parent().distance_doubleSpinBox.value()		# In um/s
		self.parent().lVelocity_LCDNumber.display(lVelocity)
		
		# DEP, which, at constant velocity, will be exactly the same as the drag force (that is what we assume)
		viscosity_SI = self.parent().viscosity_doubleSpinBox.value() * 1e-3			# Pa s
		radius_SI = (self.parent().diameter_doubleSpinBox.value() / 2) * 1e-6		# m
		lVelocity_SI = lVelocity * 1e-6												# m/s
		DEP_SI = 6 * math.pi * viscosity_SI * radius_SI * lVelocity_SI				# N
		DEP = DEP_SI * 1e12															# pN
		self.parent().DEPForce_LCDNumber.display(DEP)
		
		# Centripetal force
		distance_SI = self.parent().distance_doubleSpinBox.value() * 1e-6			# m
		density_SI = self.parent().density_doubleSpinBox.value() * 1e3				# Kg/m3
		volume_SI = 4 * math.pi * radius_SI**3 / 3									# m3
		mass_SI = density_SI * volume_SI											# Kg
		cForce_SI = mass_SI * aVelocity_SI**2 * distance_SI							# In N
		cForce = cForce_SI * 1e12													# pN
		self.parent().cForce_LCDNumber.display(cForce)


def main():
	app = QApplication(sys.argv)
	#app.setStyle("plastique")
	controlWin = MainControlWindow()
	controlWin.show()
	app.exec_()

main()
