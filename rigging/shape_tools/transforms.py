import pymel.core as pm


def scale_shape(shape_node=None, values=(1, 1, 1)):
	if shape_node is None:
		return
	
	if pm.nodeType(shape_node) == 'nurbsCurve':
		components = pm.ls(shape_node.cv)
		pm.scale(components, values, r=True, os=True, xyz=True)
	elif pm.nodeType(shape_node) == 'mesh':
		components = pm.ls(shape_node.vtx)
		pm.scale(components, values, r=True, os=True, xyz=True)


def rotate_shape(shape_node=None, values=(0, 0, 0)):
	if shape_node is None:
		return
	
	if pm.nodeType(shape_node) == 'nurbsCurve':
		components = pm.ls(shape_node.cv)
		pm.rotate(components, values, r=True, os=True, xyz=True)
	elif pm.nodeType(shape_node) == 'mesh':
		components = pm.ls(shape_node.vtx)
		pm.rotate(components, values, r=True, os=True, xyz=True)


def translate_shape(shape_node=None, values=(0, 0, 0)):
	if shape_node is None:
		return
	
	if pm.nodeType(shape_node) == 'nurbsCurve':
		components = pm.ls(shape_node.cv)
		pm.move(values[0], values[1], values[2], components, r=True, os=True, xyz=True)
	elif pm.nodeType(shape_node) == 'mesh':
		components = pm.ls(shape_node.vtx)
		pm.move(values[0], values[1], values[2], components, r=True, os=True, xyz=True)
