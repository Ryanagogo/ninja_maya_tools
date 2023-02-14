from maya import cmds
from maya import mel
import pymel.core as pm

'''
This system created a simple constraint, with one driver and one driven
if this script is in your maya/scripts folder, you can use the following line to import the module

import connections

Usage is similar to a maya constraint, driver first, driven second
connections.matrixPointConstraint('driverNodeName', 'drivenNodeName')
connections.matrixOrientConstraint('driverNodeName', 'drivenNodeName')
connections.matrixScaleConstraint('driverNodeName', 'drivenNodeName')
connections.matrixParentConstraint('driverNodeName', 'drivenNodeName')

set maintain_offset to True if you want to maintain the offset between the driver and driven
set name if you want to give the matrix nodes a specific basename
'''


def matrix_point_constraint(driver=None, driven=None, maintain_offset=False, name=None):
	matrix_constraint(driver=driver, driven=driven, maintain_offset=maintain_offset, connections='t', name=name)


def matrix_orient_constraint(driver=None, driven=None, maintain_offset=False, name=None):
	matrix_constraint(driver=driver, driven=driven, maintain_offset=maintain_offset, connections='r', name=name)


def matrix_scale_constraint(driver=None, driven=None, maintain_offset=False, name=None):
	matrix_constraint(driver=driver, driven=driven, maintain_offset=maintain_offset, connections='s', name=name)


def matrix_parent_constraint(driver=None, driven=None, maintain_offset=True, name=None):
	matrix_constraint(driver=driver, driven=driven, maintain_offset=maintain_offset, connections='trs', name=name)


def get_wt_add_matrix_node(driver=None, driven=None, driven_attr='translate'):
	if driver is not None:
		print('if driver is not None : get_wtAddMatrix_node : driven_attr', driven_attr)
		mult_matrix_output = driver.worldMatrix[0].outputs()
		if len(mult_matrix_output) == 0:
			return None
		
		wt_add_matrix_output = mult_matrix_output[0].matrixSum.outputs()
		if len(wt_add_matrix_output) == 0:
			return None
		
		return wt_add_matrix_output[0]
	
	elif driven is not None:
		print('elif driven is not None : get_wtAddMatrix_node : driven_attr', driven_attr)
		decompose_matrix_output = driven.attr(driven_attr).inputs()
		if len(decompose_matrix_output) == 0:
			return None
		
		wt_add_matrix_output = decompose_matrix_output[0].inputMatrix.inputs()
		if len(wt_add_matrix_output) == 0:
			return None
		
		return wt_add_matrix_output[0]
	
	return None


def matrix_aim_constraint(
		driver=None, driven=None, up_object=None, name=None,
		primary_mode='Aim',	primary_input_axis=(1, 0, 0), primary_target_vector=(0, 0, 0),
		secondary_mode='None', secondary_input_axis=(0, 1, 0), secondary_target_vector=(0, 0, 0)):
	if driven is None or driver is None:
		pm.warning('driver and/or driven is not defined', driver, driven)
		return
	
	driver = pm.PyNode(driver)
	driven = pm.PyNode(driven)
	
	basename = name
	if basename is None:
		basename = driven.nodeName()
	
	aim_matrix = pm.createNode('aimMatrix', name='{}_aimMatrix'.format(basename))
	
	driver.worldMatrix[0].connect(aim_matrix.primary.primaryTargetMatrix)
	aim_matrix.outputMatrix.connect(driven.offsetParentMatrix)
	
	if up_object is not None:
		up_object = pm.PyNode(up_object)
		up_object.worldMatrix[0].connect(aim_matrix.secondary.secondaryTargetMatrix)
	
	aim_matrix.primaryMode.set(primary_mode)
	aim_matrix.secondaryMode.set(secondary_mode)
	
	aim_matrix.primaryInputAxis.set(primary_input_axis)
	aim_matrix.primaryTargetVector.set(primary_target_vector)
	aim_matrix.secondaryInputAxis.set(secondary_input_axis)
	aim_matrix.secondaryTargetVector.set(secondary_target_vector)
	
	return aim_matrix


def matrix_constraint(driver=None, driven=None, maintain_offset=False, decompose=False, name=None, connections=None):
	if driven is None or driver is None:
		pm.warning('driver and/or driven is not defined', driver, driven)
		return
	
	driver = pm.PyNode(driver)
	driven = pm.PyNode(driven)
	driven_parent = driven.getParent()
	
	basename = name
	if basename is None:
		basename = driven.nodeName()
	
	mult_matrix = pm.createNode('multMatrix', name='{}_multMatrix'.format(basename))
	
	######################################################################
	# Set Maintain Offset if needed
	######################################################################
	
	if maintain_offset:
		# determine and set the offset matrix
		driven_wm = driven.worldMatrix[0].get()
		driver_wim = driver.worldInverseMatrix[0].get()
		matrix = driven_wm * driver_wim
		mult_matrix.matrixIn[0].set(matrix)
		
		# connect the offset, driver and driven parent to the mult matrix
		driver.worldMatrix[0].connect(mult_matrix.matrixIn[1])
		driven_parent.worldInverseMatrix[0].connect(mult_matrix.matrixIn[2])
	else:
		driver.worldMatrix[0].connect(mult_matrix.matrixIn[0])
		driven_parent.worldInverseMatrix[0].connect(mult_matrix.matrixIn[1])
	
	if decompose:
		######################################################################
		# Decompose Matrix if needed
		######################################################################
		decompose_matrix = pm.createNode('decomposeMatrix', name='{}_decomposeMatrix'.format(basename))
		mult_matrix.matrixSum.connect(decompose_matrix.inputMatrix)
		
		if connections is None:
			decompose_matrix.outputTranslate.connect(driven.translate, f=True)
			decompose_matrix.outputRotate.connect(driven.rotate, f=True)
			decompose_matrix.outputScale.connect(driven.scale, f=True)
		else:
			if 't' not in connections:
				decompose_matrix.outputTranslate.connect(driven.translate, f=True)
			if 'r' not in connections:
				decompose_matrix.outputRotate.connect(driven.rotate, f=True)
			if 's' not in connections:
				decompose_matrix.outputScale.connect(driven.scale, f=True)
		
		return mult_matrix, decompose_matrix
	else:
		######################################################################
		# connect to the transform using the offset parent matrix
		######################################################################
		if connections is None:
			mult_matrix.matrixSum.connect(driven.offsetParentMatrix, f=True)
			return mult_matrix
		else:
			pick_matrix = pm.createNode('pickMatrix', name='{}_pickMatrix'.format(basename))
			mult_matrix.matrixSum.connect(pick_matrix.inputMatrix, f=True)
			pick_matrix.outputMatrix.connect(driven.offsetParentMatrix, f=True)
			
			if 't' not in connections:
				pick_matrix.useTranslate.set(False)
			if 'r' not in connections:
				pick_matrix.useRotate.set(False)
			if 's' not in connections:
				pick_matrix.useScale.set(False)
			
			return mult_matrix, pick_matrix


def matrix_constraint_old(
		driver=None, driven=None, driven_parent=None,
		maintain_offset=True, connections='trs', name=None):
	if driven is None or driver is None:
		pm.warning('driver and/or driven is not defined', driver, driven)
		return
	
	driver = pm.PyNode(driver)
	driven = pm.PyNode(driven)
	
	basename = name
	if basename is None:
		basename = driven.nodeName()
	
	if driven_parent is None:
		driven_parent = driven.getParent()
	else:
		driven_parent = pm.PyNode(driven_parent)
	
	weight_add_matrix = None
	weight_add_matrix_name = '{}_{}_wtAddMatrix'.format(basename, connections)
	if pm.objExists(weight_add_matrix_name):
		weight_add_matrix = pm.PyNode(weight_add_matrix_name)
		connected = []
		for plug in weight_add_matrix.wtMatrix:
			for item in pm.listConnections(plug.matrixIn):
				connected.append(item)
		if len(connected) == 0:
			pm.delete(weight_add_matrix)
			weight_add_matrix = None
	
	if weight_add_matrix is None:
		weight_add_matrix = pm.createNode('wtAddMatrix', name=weight_add_matrix_name)
	
	next_index = weight_add_matrix.wtMatrix.numElements()
	
	mult_matrix = pm.createNode('multMatrix', name='{}_{}_{}_multMatrix'.format(basename, connections, next_index))
	decompose_matrix = pm.createNode('decomposeMatrix', name='{}_{}_decomposeMatrix'.format(basename, connections))
	
	if maintain_offset:
		# this hold matrix node will hold the offset matrix value
		
		# determine and set the offset matrix
		driven_wm = driven.worldMatrix[0].get()
		driver_wim = driver.worldInverseMatrix[0].get()
		matrix = driven_wm * driver_wim
		mult_matrix.matrixIn[0].set(matrix)
		# offset_matrix.inMatrix.set(driven_wm * driver_wim)
		
		# connect the offset, driver and driven parent to the mult matrix
		# offset_matrix.outMatrix.connect(mult_matrix.matrixIn[0])
		driver.worldMatrix[0].connect(mult_matrix.matrixIn[1])
		driven_parent.worldInverseMatrix[0].connect(mult_matrix.matrixIn[2])
	else:
		driver.worldMatrix[0].connect(mult_matrix.matrixIn[0])
		driven_parent.worldInverseMatrix[0].connect(mult_matrix.matrixIn[1])
	
	# connect the mult matrix to the decompose node
	# get the next index in wtAddMatrix
	
	# print('next_index', next_index)
	default_value = 0
	if next_index == 0:
		default_value = 1
	
	attr_name = 'weight{}'.format(next_index)
	pm.addAttr(weight_add_matrix, ln=attr_name, min=0, max=1, dv=default_value)
	weight_add_matrix.attr(attr_name).set(k=True)
	
	mult_matrix.matrixSum.connect(weight_add_matrix.wtMatrix[next_index].matrixIn)
	weight_add_matrix.attr(attr_name).connect(weight_add_matrix.wtMatrix[next_index].weightIn)
	
	if next_index == 0:
		weight_add_matrix.matrixSum.connect(decompose_matrix.inputMatrix)
		
		# connect the decompose node to the transforms of the driven
		if 't' in connections:
			decompose_matrix.outputTranslate.connect(driven.translate, f=True)
		if 'r' in connections:
			decompose_matrix.outputRotate.connect(driven.rotate, f=True)
		if 's' in connections:
			decompose_matrix.outputScale.connect(driven.scale, f=True)


def matrix_space_switch(
		drivers=(), driven=None, control=None, enum_attr='spaceSwitch', enums=None, connections='trs',
		parent_scale_module=None, parent_scale=None, loc_parent=None, name=None):
	driven = pm.PyNode(driven)
	
	if not pm.attributeQuery('SPACE', node=control, exists=True):
		pm.addAttr(control, ln='SPACE', at='enum', en='----------:')
		control.SPACE.set(k=True)
	pm.addAttr(control, ln=enum_attr, at='enum', en=enums)
	control.attr(enum_attr).set(k=True)
	
	driver_locs = []
	for driver in drivers:
		loc = pm.createNode('transform', name='{}__{}__spaceSwitch_loc'.format(control.nodeName(), driver.nodeName()))
		if loc_parent is not None:
			pm.parent(loc, loc_parent)
		t = pm.xform(driver, query=True, ws=True, t=True)
		r = pm.xform(driver, query=True, ws=True, ro=True)
		pm.xform(loc, ws=True, t=t)
		pm.xform(loc, ws=True, ro=r)
		# pm.parentConstraint(driver, loc, mo=True)
		matrix_constraint(driver, loc, maintain_offset=True, connections='tr')
		if parent_scale_module is not None and parent_scale_module.module == 'cog':
			matrix_constraint(parent_scale_module.control_03, loc, maintain_offset=True, connections='s')
		elif parent_scale is not None:
			matrix_constraint(parent_scale, loc, maintain_offset=True, connections='s')
		driver_locs.append(loc)
	
	offset_choice = pm.createNode('choice')
	driver_choice = pm.createNode('choice')
	
	control.attr(enum_attr).connect(offset_choice.selector)
	control.attr(enum_attr).connect(driver_choice.selector)
	
	mult_matrix = pm.createNode('multMatrix')
	offset_choice.output.connect(mult_matrix.matrixIn[0])
	driver_choice.output.connect(mult_matrix.matrixIn[1])
	driven.getParent().worldInverseMatrix[0].connect(mult_matrix.matrixIn[2])
	
	decompose_matrix = pm.createNode('decomposeMatrix')
	mult_matrix.matrixSum.connect(decompose_matrix.inputMatrix)
	
	# for index, driver in enumerate(drivers):
	for index, driver in enumerate(driver_locs):
		# this hold matrix node will hold the offset matrix value
		offset_matrix = pm.createNode('holdMatrix')
		
		# determine and set the offset matrix
		driven_wm = driven.worldMatrix[0].get()
		driver_wim = driver.worldInverseMatrix[0].get()
		matrix = driven_wm * driver_wim
		# offset_choice.input[index].set(matrix)
		# print(driven.nodeName(), driver.nodeName(), matrix)
		offset_matrix.inMatrix.set(matrix)
		
		# connect to the choice nodes
		offset_matrix.outMatrix.connect(offset_choice.input[index])
		driver.worldMatrix[0].connect(driver_choice.input[index])
	
	if 't' in connections:
		decompose_matrix.outputTranslate.connect(driven.translate, f=True)
	if 'r' in connections:
		decompose_matrix.outputRotate.connect(driven.rotate, f=True)
	if 's' in connections:
		if parent_scale_module is not None and parent_scale_module.module == 'cog':
			matrix_constraint(parent_scale_module.control_03, driven, maintain_offset=True, connections='s')
		else:
			decompose_matrix.outputScale.connect(driven.scale, f=True)


class FitRig:
	def __init__(self):
		pass
	
	@staticmethod
	def connect_fitrig_controls_vis(module, node):
		shapes = node.getShapes()
		for shape in shapes:
			module.group.fitrig_controls_vis.connect(shape.visibility)
	
	@staticmethod
	def connect_anim_controls_vis(module, node):
		shapes = node.getShapes()
		for shape in shapes:
			module.group.anim_controls_vis.connect(shape.visibility)
	
	@staticmethod
	def connect_anim_fk_control_vis(module, node):
		shapes = node.getShapes()
		for shape in shapes:
			module.group.anim_fk_controls_vis.connect(shape.visibility)
	
	@staticmethod
	def connect_anim_ik_control_vis(module, node):
		shapes = node.getShapes()
		for shape in shapes:
			module.group.anim_ik_controls_vis.connect(shape.visibility)
	
	@staticmethod
	def connect_control_orientations_vis(module, node):
		shapes = node.getShapes()
		for shape in shapes:
			module.group.control_orientations_vis.connect(shape.visibility)


def find_connected(attr=None, node=None):
	result = None
	
	if attr is None or node is None:
		pm.warning('** find_connected input not defined **', 'attr={}'.format(attr), 'node={}'.format(node))
		return result
	
	if pm.attributeQuery(attr, node=node, exists=True):
		connections = pm.listConnections(node.attr(attr), d=True, s=False)
		if len(connections) > 0:
			result = connections[0]
	
	if result is None:
		pm.warning('** Connection not found **', 'attr={}'.format(attr), 'node={}'.format(node))
	
	return result
