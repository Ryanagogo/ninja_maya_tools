import pymel.core as pm

import shape_data
reload(shape_data)


def create(shape_type=None, **kwargs):
	data = getattr(shape_data, shape_type)
	
	transform_type = kwargs.get('transform_type', 'transform')
	
	if transform_type == 'joint':
		transform = pm.createNode('joint', name=shape_type)
	else:
		transform = pm.createNode('transform', name=shape_type)
		
	for info in data.shapes:
		periodic = False
		if info['form'] == 'periodic':
			periodic = True
			
		curve_transform = pm.curve(p=info['cvs'], d=info['degree'], k=info['knots'], per=periodic)
		shapes = curve_transform.getShapes()
		for shape in shapes:
			pm.parent(shape, transform, r=True, shape=True)
		pm.delete(curve_transform)
	
	fix_shape_names(transform)


def fix_shape_names(curve_transform=None):
	shapes = curve_transform.getShapes()
	use_index = False
	if len(shapes) > 1:
		use_index = True
	
	for index, shape in enumerate(shapes):
		name = '{}Shape'.format(curve_transform.nodeName())
		if use_index:
			name = '{}{}Shape'.format(curve_transform.nodeName(), index+1)
		shape.rename(name)