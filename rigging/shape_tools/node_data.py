import pymel.core as pm


def get_shape_data(node=None):
	if node is None:
		return
	
	shapes = []
	approved_types = ['transform', 'joint']
	if pm.nodeType(node) in approved_types:
		shapes = node.getShapes()
	elif pm.nodeType(node) == 'nurbsCurve':
		shapes = [node]

	shape_data = []
	for shape in shapes:
		positions = []
		for cv in shape.getCVs():
			positions.append([cv[0], cv[1], cv[2]])
		
		shape_data.append(
			dict(
				knots=shape.getKnots(),
				positions=positions,
				degree=shape.degree(),
				form=shape.form().key,
				overrideEnabled=shape.overrideEnabled.get(),
				overrideColor=shape.overrideColor.get(),
				overrideRGBColors=shape.overrideRGBColors.get(),
				overrideColorRGB=shape.overrideColorRGB.get(),
				lineWidth=shape.lineWidth.get()
			)
		)
		
	return shape_data
