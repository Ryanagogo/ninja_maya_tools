import math
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
	
	nod = int(math.log10(len(shapes))) + 1  # nod = number of digits
	
	for index, shape in enumerate(shapes):
		name = '{}Shape'.format(transform.nodeName())
		if use_index:
			padded_number = str(index + 1).zfill(nod + 1)
			name = '{}_{}Shape'.format(transform.nodeName(), padded_number)
		shape.rename(name)
		