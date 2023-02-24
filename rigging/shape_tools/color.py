import pymel.core as pm


def add_rgb_color(shape=None, rgb_values=None):
	if shape is None:
		return
	
	if rgb_values is None:
		return
	
	if pm.nodeType(shape) != 'nurbsCurve':
		return
	
	shape.overrideEnabled.set(True)
	shape.overrideRGBColors.set(True)
	shape.overrideColorRGB.set(rgb_values)


def remove_rgb_color(shape=None):
	if shape is None:
		return

	shape.overrideEnabled.set(False)
	shape.overrideRGBColors.set(False)
