import pymel.core as pm


def fix_shape_names(transform=None):
	if transform is None:
		return
	
	accepted_transform_types = ['transform', 'joint']
	
	if pm.nodeType(transform) not in accepted_transform_types:
		return
	
	shapes = transform.getShapes()
	use_index = False
	if len(shapes) > 1:
		use_index = True
	
	for index, shape in enumerate(shapes):
		name = '{}Shape'.format(transform.nodeName())
		if use_index:
			name = '{}{}Shape'.format(transform.nodeName(), index + 1)
		shape.rename(name)

	
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
