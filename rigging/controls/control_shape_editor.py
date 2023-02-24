import maya.cmds as cmds
import maya.mel as mel
import pymel.core as pm

import maya.OpenMayaUI as omui

from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2.QtUiTools import *
import shiboken2 as sb
from shiboken2 import wrapInstance

import glob
import os
import json

import shape_data
import control
from .. import shape_tools
from ... general.file import custom_data

mayaMainWindowPtr = omui.MQtUtil.mainWindow()
mayaMainWindow = wrapInstance(long(mayaMainWindowPtr), QWidget)


class NinjaControlShapeEditor(QWidget):
	
	def __init__(self, *args, **kwargs):
		super(NinjaControlShapeEditor, self).__init__(*args, **kwargs)
		
		# Parent widget under Maya main window
		self.setParent(mayaMainWindow)
		self.setWindowFlags(Qt.Window)
		
		self.setAttribute(Qt.WA_DeleteOnClose)
		self.ui = None
		
		# Set the object name
		self.setObjectName('ninjaControlShapeEditor_id')
		self.setWindowTitle('Ninja Control Shape Editor 2023')
		self.resize(500, 500)
		# self.setGeometry(50, 50, 250, 150)
		
		self.addMayaCallbacks()
		
		self.current_dir = os.path.dirname(__file__)
		
		self.initialize_ui()
		
		self.copy_data = None
	
	########################################################
	#  UI Functions
	########################################################
	
	def initialize_ui(self):
		self.init_ui()
		self.setup_events()
	
	def init_ui(self):
		loader = QUiLoader()
		# current_dir = os.path.dirname(__file__)
		ui_file = QFile(self.current_dir + "/control_shape_editor.ui")
		ui_file.open(QFile.ReadOnly)
		self.ui = loader.load(ui_file, parentWidget=self)
		ui_file.close()
		
		main_layout = QVBoxLayout()
		self.create_menu_bar(main_layout)
		main_layout.setSpacing(0)
		main_layout.setContentsMargins(0, 0, 0, 0)
		main_layout.addWidget(self.ui)
		self.setLayout(main_layout)
		
		self.check_custom_shape_data_package()
		
		#self.ui.rig_modules_splitter.setSizes([300, 300, 300])
		
		self.ui.available_shapes_treeWidget.setSelectionMode(QAbstractItemView.ExtendedSelection)
		self.ui.available_shapes_treeWidget.setColumnCount(1)
		self.ui.available_shapes_treeWidget.setHeaderHidden(True)
		self.ui.available_shapes_treeWidget.clear()
		self.update_shapes_tree_view()
	
	########################################################
	# Event Functions
	########################################################
	
	def setup_events(self):
		self.ui.new_control_button.clicked.connect(self.new_control)
		self.ui.add_shapes_to_transforms_button.clicked.connect(self.add_shapes_to_transforms)
		self.ui.replace_shapes_on_transforms_button.clicked.connect(self.replace_shapes_on_transforms)
		# self.ui.delete_selected_shapes_button.clicked.connect(self.delete_selected_shapes)
		
		self.ui.translate_shape_nx_button.clicked.connect(self.translate_shape_nx)
		self.ui.translate_shape_x_button.clicked.connect(self.translate_shape_x)
		self.ui.translate_shape_ny_button.clicked.connect(self.translate_shape_ny)
		self.ui.translate_shape_y_button.clicked.connect(self.translate_shape_y)
		self.ui.translate_shape_nz_button.clicked.connect(self.translate_shape_nz)
		self.ui.translate_shape_z_button.clicked.connect(self.translate_shape_z)
		
		self.ui.rotate_shape_nx_button.clicked.connect(self.rotate_shape_nx)
		self.ui.rotate_shape_x_button.clicked.connect(self.rotate_shape_x)
		self.ui.rotate_shape_ny_button.clicked.connect(self.rotate_shape_ny)
		self.ui.rotate_shape_y_button.clicked.connect(self.rotate_shape_y)
		self.ui.rotate_shape_nz_button.clicked.connect(self.rotate_shape_nz)
		self.ui.rotate_shape_z_button.clicked.connect(self.rotate_shape_z)
		
		self.ui.scale_shape_xyz_button.clicked.connect(self.scale_shape_xyz)
		self.ui.scale_shape_nx_button.clicked.connect(self.scale_shape_nx)
		self.ui.scale_shape_x_button.clicked.connect(self.scale_shape_x)
		self.ui.scale_shape_ny_button.clicked.connect(self.scale_shape_ny)
		self.ui.scale_shape_y_button.clicked.connect(self.scale_shape_y)
		self.ui.scale_shape_nz_button.clicked.connect(self.scale_shape_nz)
		self.ui.scale_shape_z_button.clicked.connect(self.scale_shape_z)
		
		self.ui.add_shape_color_button.clicked.connect(self.add_shape_color)
		self.ui.remove_shape_color_button.clicked.connect(self.remove_shape_color)
		
		self.ui.line_thickness_1_button.clicked.connect(self.line_thickness_1)
		self.ui.line_thickness_2_button.clicked.connect(self.line_thickness_2)
		self.ui.line_thickness_3_button.clicked.connect(self.line_thickness_3)
		self.ui.line_thickness_4_button.clicked.connect(self.line_thickness_4)
		
		self.ui.copy_shape_button.clicked.connect(self.copy_shape)
		self.ui.paste_shape_button.clicked.connect(self.paste_shape)
		
		self.ui.mirror_shape_x_button.clicked.connect(self.mirror_shape_x)
		self.ui.mirror_shape_y_button.clicked.connect(self.mirror_shape_y)
		self.ui.mirror_shape_z_button.clicked.connect(self.mirror_shape_z)
		
		# tools
		self.ui.fix_shape_names_button.clicked.connect(self.fix_shape_names)
		
		# settings
		# self.ui.get_custom_shapes_folder_path_button.clicked.connect(self.get_custom_shapes_folder_path)
		self.ui.save_custom_shapes_button.clicked.connect(self.save_custom_shapes)
		
		self.ui.available_shapes_treeWidget.setContextMenuPolicy(Qt.CustomContextMenu)
		self.ui.available_shapes_treeWidget.customContextMenuRequested.connect(self.open_shape_type_popup_menu)
	
	def create_menu_bar(self, layout):
		menu_bar = QMenuBar()
		layout.addWidget(menu_bar)
		menu1 = menu_bar.addMenu('Shapes')
		fix_names_action = menu1.addAction('Fix Shape Names on Selected')
		menu1.addSeparator()
		save_action = menu1.addAction('Save Selected Shapes as Custom Shape Types')
		menu1.addSeparator()
		delete_action = menu1.addAction('Delete Selected Custom Shape Types')
		
		fix_names_action.triggered.connect(self.fix_shape_names)
		save_action.triggered.connect(self.save_custom_shapes)
		delete_action.triggered.connect(self.delete_selected_custom_shape_types)
		
	def open_shape_type_popup_menu(self, position):
		delete_custom_shape_type_action = QAction('Delete Selected Custom Shape Types')
		delete_custom_shape_type_action.triggered.connect(self.delete_selected_custom_shape_types)
		
		menu = QMenu(self.ui.available_shapes_treeWidget)
		menu.addAction(delete_custom_shape_type_action)
		
		menu.exec_(self.ui.available_shapes_treeWidget.mapToGlobal(position))
	
	def delete_selected_custom_shape_types(self):
		shape_types = self.get_selected_shape_types()
		custom_types = []
		for shape_type in shape_types:
			if shape_type.get('custom', None):
				custom_types.append(shape_type['custom'])
				
		if len(custom_types) == 0:
			print('no custom shape types selected, nothing to delete')
			return
		
		text = ''
		for index, custom_type in enumerate(custom_types):
			if index == 0:
				text += '{}'.format(custom_type)
			else:
				text += ', {}'.format(custom_type)
		
		data = dict(
			title='Delete Custom Shape Types',
			message='Delete these custom shapes?\n* Not Undoable *\n{}'.format(text),
			messageAlign='center',
			button=['Yes', 'No'],
			defaultButton='Yes', cancelButton='No', dismissString='No'
		)
		result = pm.confirmDialog(**data)
		
		if result == 'No':
			print('Delete Custom Shape Type : Canceled')
			return
		
		shape_data_path = self.check_custom_shape_data_package()
		for custom_type in custom_types:
			shape_data_file = '{}.py'.format(custom_type)
			file_path = os.path.join(shape_data_path, shape_data_file)
	
			if os.path.exists(file_path):
				os.remove(file_path)
				
		self.updated_custom_shape_data_init()
		self.update_shapes_tree_view()

	def set_custom_shapes_file_path_from_data(self):
		temp_folder = self.get_temp_folder()
		settings_file = 'ninja_custom_shapes_settings.json'
		settings_path = os.path.join(temp_folder, settings_file)
		
		data = {}
		
		if os.path.exists(settings_path):
			with open(settings_path) as json_file:
				data = json.load(json_file)
		
		custom_shapes_folder_path = data.get('custom_shapes_folder', '')
		self.ui.custom_shapes_folder_path_lineEdit.setText(custom_shapes_folder_path)
		
		if custom_shapes_folder_path != '':
			self.add_package_init_file(folder=custom_shapes_folder_path)
	
	def fix_shape_names(self):
		nodes = self.get_selected_nodes()
		for node in nodes:
			shape_tools.names.fix_shape_names(transform=node)

	def check_custom_shape_data_package(self):
		data_path = custom_data.check_ninja_custom_data_package()
		shape_data_dir = 'custom_shape_data'
		shape_data_path = os.path.join(data_path, shape_data_dir)
		if not os.path.exists(shape_data_path):
			os.makedirs(shape_data_path)
			custom_data.add_package_init_file(folder=shape_data_path)
		
		return shape_data_path
	
	def save_custom_shapes(self):
		selected = pm.ls(sl=True)
		if len(selected) == 0:
			return
		
		data = dict(
			title='Save Custom Shape Types',
			message='Save Selected Custom Shapes?',
			messageAlign='center',
			button=['Yes', 'No'],
			defaultButton='Yes', cancelButton='No', dismissString='No'
		)
		result = pm.confirmDialog(**data)
		
		if result == 'No':
			print('Saving Custom Shape Types : Canceled')
			return
		
		shape_data_path = self.check_custom_shape_data_package()
		
		accepted_types = ['transform', 'joint']
		nodes = []
		for node in selected:
			if pm.nodeType(node) not in accepted_types:
				continue
			nodes.append(node)
		
		for node in nodes:
			data = shape_tools.node_data.get_shape_data(node=node)
			module_name = node.nodeName()
			shape_data_file = '{}.py'.format(module_name)
			
			#shapes = transform.getShapes()
			text = "# shape data for : {}\n\n".format(module_name)
			text += 'shapes = [\n'
			
			for data_item in data:
				text += '    {\n'
				
				# form
				text += "        'form': '{}',\n".format(data_item.get('form'))
				
				# degree
				text += "        'degree': {},\n".format(data_item.get('degree'))
				
				# cvs
				text += "        'positions': [\n"
				positions = data_item.get('positions')
				for index, cv in enumerate(positions):
					if index < len(positions) - 1:
						text += "            [{}, {}, {}],\n".format(cv[0], cv[1], cv[2])
					else:
						text += "            [{}, {}, {}]\n".format(cv[0], cv[1], cv[2])
				text += "        ],\n"
				
				# knots
				knots = data_item.get('knots')
				text += "        'knots': ["
				for index, knot in enumerate(knots):
					if index < len(knots) - 1:
						text += "{}, ".format(knot)
					else:
						text += "{}".format(knot)
				text += "]\n"
				
				text += '    },\n'
			
			text += ']\n'
			
			file_path = os.path.join(shape_data_path, shape_data_file)
			print('writing shape data\n')
			print('{}\n'.format(file_path))
			print(text)
			with open(file_path, 'w') as f:
				f.write(text)
	
		self.updated_custom_shape_data_init()
		self.update_shapes_tree_view()
	
	def updated_custom_shape_data_init(self):
		shape_data_path = self.check_custom_shape_data_package()
		init_file_path = os.path.join(shape_data_path, '__init__.py')
		
		all_files = glob.glob('{}/*.py'.format(shape_data_path))
		module_names = []
		for file in all_files:
			file_name = os.path.basename(file)
			if '.py' not in file_name:
				continue
				
			if '__init__' in file_name:
				continue
			
			module_name, ext = os.path.splitext(file_name)
			module_names.append(module_name)
			
		text = ''
		
		for module_name in module_names:
			text += 'import {}\n'.format(module_name)
		
		text += '\n'
		text += 'shape_types = [\n'
		for module_name in module_names:
			text += "     '{}',\n".format(module_name)
		text += ']\n'
		
		with open(init_file_path, 'w') as f:
			f.write(text)
	
	def new_control(self):
		result = cmds.promptDialog(
			title='Create New Control?',
			message='Enter Name:',
			button=['OK', 'Cancel'],
			defaultButton='OK',
			cancelButton='Cancel',
			dismissString='Cancel')
		
		if result != 'OK':
			return
			
		name = cmds.promptDialog(query=True, text=True)
		
		with pm.UndoChunk():
			transform = pm.createNode('transform', name=name)
			pm.select(transform)
			self.replace_shapes_on_transforms()
	
	def copy_shape(self):
		self.copy_data = shape_tools.copy_paste.CopyPaste()
		self.copy_data.copy_selected()
	
	def paste_shape(self):
		if self.copy_data is None:
			return
		
		self.copy_data.paste_selected()
	
	def mirror_shape_x(self):
		self.mirror_shape([-1, 1, 1])
	
	def mirror_shape_y(self):
		self.mirror_shape([1, -1, 1])
	
	def mirror_shape_z(self):
		self.mirror_shape([1, 1, -1])
	
	def mirror_shape(self, values=None):
		if values is None:
			return
		
		selected = self.get_selected_nodes()
		if len(selected) != 2:
			pm.warning('Please select only two nodes for Mirror Shape X')
			return
		
		node1 = selected[0]
		node2 = selected[1]
		
		self.copy_data = shape_tools.copy_paste.CopyPaste()
		self.copy_data.copy(node=node1)
		
		self.copy_data.paste(transform=node2)
		
		for shape in node2.getShapes():
			shape_tools.transforms.scale_shape(shape_node=shape, values=values)
	
	def get_selected_shapes(self):
		shapes = []
		approved_transform_types = ['transform', 'joint']
		for node in pm.ls(sl=True):
			node_type = pm.nodeType(node)
			if node_type in approved_transform_types:
				for shape in node.getShapes():
					if pm.nodeType(shape) == 'nurbsCurve':
						shapes.append(shape)
			elif node_type == 'nurbsCurve':
				shapes.append(node)
		
		return shapes
	
	def remove_shape_color(self):
		shapes = self.get_selected_shapes()
		
		with pm.UndoChunk():
			for shape in shapes:
				shape_tools.color.remove_rgb_color(shape=shape)
	
	def add_shape_color(self):
		cmds.colorEditor()
		if cmds.colorEditor(query=True, result=True):
			rgb_values = cmds.colorEditor(query=True, rgb=True)
		else:
			return
		
		shapes = self.get_selected_shapes()
		
		with pm.UndoChunk():
			for shape in shapes:
				shape_tools.color.add_rgb_color(shape=shape, rgb_values=rgb_values)
				
	def line_thickness_1(self):
		self.set_line_width(value=-1)
	
	def line_thickness_2(self):
		self.set_line_width(value=2)
	
	def line_thickness_3(self):
		self.set_line_width(value=3)
	
	def line_thickness_4(self):
		self.set_line_width(value=4)
	
	def set_line_width(self, value=-1):
		shapes = self.get_selected_shapes()
		
		with pm.UndoChunk():
			for shape in shapes:
				shape.lineWidth.set(value)
	
	def translate_shape_nx(self):
		value = self.ui.translate_shape_doubleSpinBox.value()
		self.translate_shapes(values=[value*-1, 0, 0])
	
	def translate_shape_x(self):
		value = self.ui.translate_shape_doubleSpinBox.value()
		self.translate_shapes(values=[value, 0, 0])

	def translate_shape_ny(self):
		value = self.ui.translate_shape_doubleSpinBox.value()
		self.translate_shapes(values=[0, value*-1, 0])

	def translate_shape_y(self):
		value = self.ui.translate_shape_doubleSpinBox.value()
		self.translate_shapes(values=[0, value, 0])

	def translate_shape_nz(self):
		value = self.ui.translate_shape_doubleSpinBox.value()
		self.translate_shapes(values=[0, 0, value*-1])

	def translate_shape_z(self):
		value = self.ui.translate_shape_doubleSpinBox.value()
		self.translate_shapes(values=[0, 0, value])

	def rotate_shape_nx(self):
		value = self.ui.rotate_shape_doubleSpinBox.value()
		self.rotate_shapes(values=[value*-1, 0, 0])
	
	def rotate_shape_x(self):
		value = self.ui.rotate_shape_doubleSpinBox.value()
		self.rotate_shapes(values=[value, 0, 0])

	def rotate_shape_ny(self):
		value = self.ui.rotate_shape_doubleSpinBox.value()
		self.rotate_shapes(values=[0, value*-1, 0])

	def rotate_shape_y(self):
		value = self.ui.rotate_shape_doubleSpinBox.value()
		self.rotate_shapes(values=[0, value, 0])

	def rotate_shape_nz(self):
		value = self.ui.rotate_shape_doubleSpinBox.value()
		self.rotate_shapes(values=[0, 0, value*-1])

	def rotate_shape_z(self):
		value = self.ui.rotate_shape_doubleSpinBox.value()
		self.rotate_shapes(values=[0, 0, value])

	def scale_shape_xyz(self):
		value = self.ui.scale_shape_doubleSpinBox.value()
		self.scale_shapes(values=[value, value, value])

	def scale_shape_nx(self):
		value = self.ui.scale_shape_doubleSpinBox.value()
		value = value * -1
		#value = 1.0 / value
		mods = cmds.getModifiers()
		if (mods & 4) > 0:
			self.scale_shapes(values=[1, value, value])
		else:
			self.scale_shapes(values=[value, 1, 1])

	def scale_shape_x(self):
		value = self.ui.scale_shape_doubleSpinBox.value()
		mods = cmds.getModifiers()
		if (mods & 4) > 0:
			self.scale_shapes(values=[1, value, value])
		else:
			self.scale_shapes(values=[value, 1, 1])

	def scale_shape_ny(self):
		value = self.ui.scale_shape_doubleSpinBox.value()
		value = value * -1
		#value = 1.0 / value
		mods = cmds.getModifiers()
		if (mods & 4) > 0:
			self.scale_shapes(values=[value, 1, value])
		else:
			self.scale_shapes(values=[1, value, 1])

	def scale_shape_y(self):
		value = self.ui.scale_shape_doubleSpinBox.value()
		mods = cmds.getModifiers()
		if (mods & 4) > 0:
			self.scale_shapes(values=[value, 1, value])
		else:
			self.scale_shapes(values=[1, value, 1])

	def scale_shape_nz(self):
		value = self.ui.scale_shape_doubleSpinBox.value()
		value = value * -1
		#value = 1.0 / value
		mods = cmds.getModifiers()
		if (mods & 4) > 0:
			self.scale_shapes(values=[value, value, 1])
		else:
			self.scale_shapes(values=[1, 1, value])

	def scale_shape_z(self):
		value = self.ui.scale_shape_doubleSpinBox.value()
		mods = cmds.getModifiers()
		if (mods & 4) > 0:
			self.scale_shapes(values=[value, value, 1])
		else:
			self.scale_shapes(values=[1, 1, value])

	def translate_shapes(self, values=None):
		if values is None:
			return
		shapes = self.get_selected_shapes()
		with pm.UndoChunk():
			for shape in shapes:
				shape_tools.transforms.translate_shape(shape_node=shape, values=values)

	def rotate_shapes(self, values=None):
		if values is None:
			return
		shapes = self.get_selected_shapes()
		with pm.UndoChunk():
			for shape in shapes:
				shape_tools.transforms.rotate_shape(shape_node=shape, values=values)

	def scale_shapes(self, values=None):
		if values is None:
			return
		shapes = self.get_selected_shapes()

		with pm.UndoChunk():
			for shape in shapes:
				shape_tools.transforms.scale_shape(shape_node=shape, values=values)

	def add_shapes_to_transforms(self):
		selected = pm.ls(sl=True)
		
		shape_types = self.get_selected_shape_types()
		if len(shape_types) == 0:
			return
		selected_nodes = self.get_selected_nodes()
		
		with pm.UndoChunk():
			# add shapes to nodes
			for node in selected_nodes:
				common_data = self.get_common_shape_attributes(node=node)
				
				#print(node, common_data)
				for shape_type in shape_types:
					control_object = self.create_new_shape(shape_type=shape_type, node=node)
					
					if common_data is None:
						continue
					
					for shape in control_object.transform.getShapes():
						if common_data.get('use_overrideEnabled'):
							shape.overrideEnabled.set(common_data['overrideEnabled'])
							
						if common_data.get('use_overrideColor'):
							shape.overrideColor.set(common_data['overrideColor'])
							
						if common_data.get('use_overrideRGBColors'):
							shape.overrideRGBColors.set(common_data['overrideRGBColors'])
							
						if common_data.get('use_overrideColorRGB'):
							shape.overrideColorRGB.set(common_data['overrideColorRGB'])
							
						if common_data.get('use_lineWidth'):
							shape.lineWidth.set(common_data['lineWidth'])

			pm.select(selected)
	
	def get_common_shape_attributes(self, node=None):
		if node is None:
			return
		
		data = shape_tools.node_data.get_shape_data(node)
		if len(data) == 0:
			return None
		
		common_data = dict(
			use_overrideEnabled=True,
			use_overrideColor=True,
			use_overrideRGBColors=True,
			use_overrideColorRGB=True,
			use_lineWidth=True,
			overrideEnabled=None,
			overrideColor=None,
			overrideRGBColors=None,
			overrideColorRGB=None,
			lineWidth=None
		)
		
		for index, item in enumerate(data):
			if index == 0:
				common_data['overrideEnabled'] = item['overrideEnabled']
				common_data['overrideColor'] = item['overrideColor']
				common_data['overrideRGBColors'] = item['overrideRGBColors']
				common_data['overrideColorRGB'] = item['overrideColorRGB']
				common_data['lineWidth'] = item['lineWidth']
			else:
				if item['overrideEnabled'] != common_data['overrideEnabled']:
					common_data['use_overrideEnabled'] = False
				if item['overrideColor'] != common_data['overrideColor']:
					common_data['use_overrideColor'] = False
				if item['overrideRGBColors'] != common_data['overrideRGBColors']:
					common_data['use_overrideRGBColors'] = False
				if item['overrideColorRGB'] != common_data['overrideColorRGB']:
					common_data['use_overrideColorRGB'] = False
				if item['lineWidth'] != common_data['lineWidth']:
					common_data['use_lineWidth'] = False
		
		return common_data
	
	def replace_shapes_on_transforms(self):
		selected = pm.ls(sl=True)
		
		shape_types = self.get_selected_shape_types()
		if len(shape_types) == 0:
			return
		
		selected_nodes = self.get_selected_nodes()
		
		# delete existing nurbsCurve shapes
		common_datas = []
		for node in selected_nodes:
			common_data = self.get_common_shape_attributes(node=node)
			common_datas.append(common_data)
			shapes = node.getShapes()
			for shape in shapes:
				if pm.nodeType(shape) != 'nurbsCurve':
					continue
				pm.delete(shape)
		
		with pm.UndoChunk():
			# add shapes to nodes
			for node, common_data in zip(selected_nodes, common_datas):
				print(node, common_data)
				for shape_type in shape_types:
					control_object = self.create_new_shape(shape_type=shape_type, node=node)
					if common_data is None:
						continue
						
					for shape in control_object.transform.getShapes():
						if common_data.get('use_overrideEnabled'):
							shape.overrideEnabled.set(common_data['overrideEnabled'])
						
						if common_data.get('use_overrideColor'):
							shape.overrideColor.set(common_data['overrideColor'])
						
						if common_data.get('use_overrideRGBColors'):
							shape.overrideRGBColors.set(common_data['overrideRGBColors'])
						
						if common_data.get('use_overrideColorRGB'):
							shape.overrideColorRGB.set(common_data['overrideColorRGB'])
						
						if common_data.get('use_lineWidth'):
							shape.lineWidth.set(common_data['lineWidth'])
			
			pm.select(selected)
		
	def get_selected_nodes(self):
		nodes = []
		approved_types = ['transform', 'joint']
		for node in pm.ls(sl=True):
			node_type = pm.nodeType(node)
			if node_type in approved_types:
				nodes.append(node)
		
		return nodes
	
	def get_selected_shape_types(self):
		selected_items = self.ui.available_shapes_treeWidget.selectedItems()
		shape_types = []
		for item in selected_items:
			parent_item = item.parent()
			if parent_item is None:
				continue
			parent_item_text = parent_item.text(0)
			
			if parent_item_text == 'Custom Shape Types':
				shape_types.append(dict(custom=item.text(0)))
			else:
				shape_types.append(dict(builtin=item.text(0)))
		
		print('get_selected_shape_types | {}'.format(shape_types))
		return shape_types
	
	def create_new_shape(self, shape_type=None, node=None):
		control_object = control.Control()
		control_object.set_transform(transform=node)
		control_object.set_shape(shape_type=shape_type)
		return control_object
	
	# def delete_selected_shapes(self):
	# 	pass
	
	def addMayaCallbacks(self):
		print('Add Maya Callbacks')
		# self.callbackId = om.MEventMessage.addEventCallback('SelectionChanged', self.selection_changed, None)
		# self.nameChangeCallbackId = om.MNodeMessage.addNameChangedCallback(om.MObject(), self.name_changed, None)
		# self.sceneCallbackId = om.MSceneMessage.addCallback(om.MSceneMessage.kAfterNew, self.new_scene_event, None)
	
	def closeEvent(self, event):
		self.removeMayaCallbacks()
		
		# super(NinjaRigBuilderUI, self).closeEvent(event)
		print('Ninja Control Shape Editor Closed')
	
	def removeMayaCallbacks(self):
		print('Remove Maya Callbacks')
		# om.MMessage.removeCallback(self.callbackId)
		# om.MMessage.removeCallback(self.nameChangeCallbackId)
		# om.MMessage.removeCallback(self.sceneCallbackId)
	
	def update_shapes_tree_view(self):
		self.ui.available_shapes_treeWidget.clear()
		
		parent_item = QTreeWidgetItem(self.ui.available_shapes_treeWidget)
		parent_item.setText(0, 'Built-in Shape Types')
		parent_item.setExpanded(True)
		
		for shape_type in shape_data.shape_types:
			child_item = QTreeWidgetItem(parent_item)
			child_item.setText(0, shape_type)
		
		from ninja_custom_data import custom_shape_data
		reload(custom_shape_data)
		
		parent_item2 = QTreeWidgetItem(self.ui.available_shapes_treeWidget)
		parent_item2.setText(0, 'Custom Shape Types')
		parent_item2.setExpanded(True)
		
		for shape_type in custom_shape_data.shape_types:
			child_item = QTreeWidgetItem(parent_item2)
			child_item.setText(0, shape_type)


#############################################################################
#
#  Start the UI
#
#############################################################################


def start_ui():
	create_new_ui = True
	if 'NinjaControlShapeEditorWindow' in globals():
		global NinjaControlShapeEditorWindow
		if sb.isValid(NinjaControlShapeEditorWindow):
			create_new_ui = False
			# print('Showing Ninja Control Shape Editor Window')
			NinjaControlShapeEditorWindow.show()
			NinjaControlShapeEditorWindow.showNormal()
			NinjaControlShapeEditorWindow.activateWindow()
	
	if create_new_ui:
		# print('Creating a New Ninja Control Shape Editor Window')
		NinjaControlShapeEditorWindow = NinjaControlShapeEditor()
		NinjaControlShapeEditorWindow.show()
		
		return NinjaControlShapeEditorWindow
	