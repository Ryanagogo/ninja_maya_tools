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
		