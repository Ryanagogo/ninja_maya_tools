import maya.OpenMayaUI as omui

from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2.QtUiTools import *
import shiboken2 as sb
from shiboken2 import wrapInstance

import os

mayaMainWindowPtr = omui.MQtUtil.mainWindow()
mayaMainWindow = wrapInstance(long(mayaMainWindowPtr), QWidget)


class NinjaRigBuilder(QWidget):

	def __init__(self, *args, **kwargs):
		super(NinjaRigBuilder, self).__init__(*args, **kwargs)

		# Parent widget under Maya main window
		self.setParent(mayaMainWindow)
		self.setWindowFlags(Qt.Window)

		self.setAttribute(Qt.WA_DeleteOnClose)
		self.ui = None

		# Set the object name
		self.setObjectName('ninjaRigBuilder_id')
		self.setWindowTitle('Ninja Rig Builder 2023')
		self.resize(900, 500)
		# self.setGeometry(50, 50, 250, 150)

		self.addMayaCallbacks()

		self.initialize_ui()

	########################################################
	#  UI Functions
	########################################################

	def initialize_ui(self):
		self.init_ui()
		self.setup_events()

	def init_ui(self):
		loader = QUiLoader()
		current_dir = os.path.dirname(__file__)
		ui_file = QFile(current_dir + "/rig_builder.ui")
		ui_file.open(QFile.ReadOnly)
		self.ui = loader.load(ui_file, parentWidget=self)
		ui_file.close()

		main_layout = QVBoxLayout()
		main_layout.setSpacing(0)
		main_layout.setContentsMargins(0, 0, 0, 0)
		main_layout.addWidget(self.ui)
		self.setLayout(main_layout)
		
		self.ui.rig_modules_splitter.setSizes([300, 300, 300])

	########################################################
	# Event Functions
	########################################################

	def setup_events(self):
		'''
		self.ui.create_fitrig_button.clicked.connect(self.create_fitrig)
		self.ui.mirror_fitrig_l_to_r_button.clicked.connect(self.mirror_fitrig_l_to_r)
		self.ui.rebuild_fitrig_button.clicked.connect(self.rebuild_fitrig)
		self.ui.save_fitrig_data_button.clicked.connect(self.save_fitrig_data)
		self.ui.load_fitrig_data_button.clicked.connect(self.load_fitrig_data)
		self.ui.build_animrig_button.clicked.connect(self.create_animrig)
		self.ui.add_fx_fk_skeleton_button.clicked.connect(self.add_fx_fk_skeleton)
		#self.ui.skeleton_editMode_on_button.clicked.connect(self.skeleton_edit_mode_on)
		#self.ui.skeleton_editMode_off_button.clicked.connect(self.skeleton_edit_mode_off)
		#self.ui.asset_listWidget.itemClicked.connect(self.asset_list_item_clicked)
		#self.ui.jointName_lineEdit.returnPressed.connect(self.joint_name_updated)
		'''
		pass

	def addMayaCallbacks(self):
		print('Add Maya Callbacks')
		#self.callbackId = om.MEventMessage.addEventCallback('SelectionChanged', self.selection_changed, None)
		#self.nameChangeCallbackId = om.MNodeMessage.addNameChangedCallback(om.MObject(), self.name_changed, None)
		#self.sceneCallbackId = om.MSceneMessage.addCallback(om.MSceneMessage.kAfterNew, self.new_scene_event, None)

	def closeEvent(self, event):
		self.removeMayaCallbacks()

		# super(NinjaRigBuilderUI, self).closeEvent(event)
		print('Biped UI Closed')

	def removeMayaCallbacks(self):
		print('Remove Maya Callbacks')
		#om.MMessage.removeCallback(self.callbackId)
		#om.MMessage.removeCallback(self.nameChangeCallbackId)
		#om.MMessage.removeCallback(self.sceneCallbackId)

#############################################################################
#
#  Start the UI
#
#############################################################################


def start_ui():
	create_new_ui = True
	if 'NinjaRigBuilderWindow' in globals():
		global NinjaRigBuilderWindow
		if sb.isValid(NinjaRigBuilderWindow):
			create_new_ui = False
			# print('Showing Ninja Rig Builder Window')
			NinjaRigBuilderWindow.show()
			NinjaRigBuilderWindow.showNormal()
			NinjaRigBuilderWindow.activateWindow()

	if create_new_ui:
		# print('Creating a New Ninja Rig Builder Window')
		NinjaRigBuilderWindow = NinjaRigBuilder()
		NinjaRigBuilderWindow.show()

		return NinjaRigBuilderWindow