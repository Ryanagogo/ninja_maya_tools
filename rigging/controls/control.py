import pymel.core as pm

import shape_data
from ..tools import shapes as shapes_tool
from ninja_custom_data import custom_shape_data

reload(custom_shape_data)


class Control:
	def __init__(self):
		self.transform = None
	
	def create(self, shape_type=None, multi_shapes=None, **kwargs):
		#print('Control | create | shape_type={} , multi_shapes={} , kwargs={}'.format(shape_type, multi_shapes, kwargs))
		if shape_type is None and multi_shapes is None:
			return
		
		self.create_transform(**kwargs)
		
		if shape_type is not None:
			self.set_shape(shape_type=shape_type, **kwargs)
		elif multi_shapes is not None:
			self.set_multi_shapes(multi_shapes=multi_shapes, **kwargs)
			
		return self.transform
	
	def set_multi_shapes(self, multi_shapes=None, **kwargs):
		if multi_shapes is None:
			return
		
		for shape_item in multi_shapes:
			shape_type = shape_item.get('shape_type', None)
			if shape_type is None:
				continue
			shape_item.pop('shape_type')
			self.set_shape(shape_type=shape_type, **shape_item)

		self.transform_shape(**kwargs)
	
	def set_shape(self, shape_type=None, **kwargs):
		print('control -> set_shape | {}'.format(shape_type))
		if shape_type.get('builtin', None):
			#if shape_type['builtin'] not in shape_data.shape_types:
			#	return
			data = getattr(shape_data, shape_type['builtin'])
		elif shape_type.get('custom', None):
			#if shape_type['custom'] not in custom_shape_data.shape_types:
			#	return
			data = getattr(custom_shape_data, shape_type['custom'])
		else:
			return
		
		scale_values = kwargs.get('scale_values', None)
		rotate_values = kwargs.get('rotate_values', None)
		translate_values = kwargs.get('translate_values', None)
		
		for info in data.shapes:
			periodic = False
			if info['form'] == 'periodic':
				periodic = True
			
			curve_transform = pm.curve(p=info['positions'], d=info['degree'], k=info['knots'], per=periodic)
			shape_nodes = curve_transform.getShapes()
			for shape in shape_nodes:
				pm.parent(shape, self.transform, r=True, shape=True)
				self.tag_shape(shape_node=shape, shape_type=shape_type)
				self.scale_shape(shape_node=shape, values=scale_values)
				self.rotate_shape(shape_node=shape, values=rotate_values)
				self.translate_shape(shape_node=shape, values=translate_values)
				self.set_line_attributes(shape_node=shape, **kwargs)
			
			pm.delete(curve_transform)
		
		self.fix_shape_names()
	
	def set_line_attributes(self, shape_node=None, **kwargs):
		if shape_node is None:
			return
		
		line_width = kwargs.get('line_width', -1)
		index_color = kwargs.get('index_color', None)
		rgb_color = kwargs.get('rgb_color', None)
		
		shape_node.lineWidth.set(line_width)
		
		if not pm.attributeQuery('ninjaShapeLineWidth', node=shape_node, exists=True):
			pm.addAttr(shape_node, ln='ninjaShapeLineWidth', at='long')
		
		shape_node.ninjaShapeLineWidth.set(l=False)
		shape_node.ninjaShapeLineWidth.set(line_width)
		shape_node.ninjaShapeLineWidth.set(l=True)
		
		if index_color is not None:
			shape_node.overrideEnabled.set(True)
			shape_node.overrideRGBColors.set(False)
			shape_node.overrideColor.set(index_color)
			
			if not pm.attributeQuery('ninjaShapeIndexColor', node=shape_node, exists=True):
				pm.addAttr(shape_node, ln='ninjaShapeIndexColor', at='long')
			
			shape_node.ninjaShapeIndexColor.set(l=False)
			shape_node.ninjaShapeIndexColor.set(index_color)
			shape_node.ninjaShapeIndexColor.set(l=True)

		elif rgb_color is not None:
			shape_node.overrideEnabled.set(True)
			shape_node.overrideRGBColors.set(True)
			shape_node.overrideColorRGB.set(rgb_color)
			
			if not pm.attributeQuery('ninjaShapeRgbColor', node=shape_node, exists=True):
				pm.addAttr(shape_node, ln='ninjaShapeRgbColor', at='double3')
				pm.addAttr(shape_node, ln='ninjaShapeRgbColorR', at='double', p='ninjaShapeRgbColor')
				pm.addAttr(shape_node, ln='ninjaShapeRgbColorG', at='double', p='ninjaShapeRgbColor')
				pm.addAttr(shape_node, ln='ninjaShapeRgbColorB', at='double', p='ninjaShapeRgbColor')
			
			shape_node.ninjaShapeRgbColor.set(l=False)
			shape_node.ninjaShapeRgbColor.set(rgb_color)
			shape_node.ninjaShapeRgbColor.set(l=True)
	
	def replace_shape(self, shape_type=None, **kwargs):
		if self.transform is None:
			return
		
		if shape_type not in shape_data.shape_types:
			return

		shape_nodes = self.transform.getShapes()
		for shape in shape_nodes:
			pm.delete(shape)
		
		self.set_shape(shape_type=shape_type, **kwargs)
	
	def transform_shape(self, **kwargs):
		if self.transform is None:
			return
		
		scale_values = kwargs.get('scale_values', None)
		rotate_values = kwargs.get('rotate_values', None)
		translate_values = kwargs.get('translate_values', None)
		
		shape_nodes = self.transform.getShapes()
		for shape in shape_nodes:
			self.scale_shape(shape_node=shape, values=scale_values)
			self.rotate_shape(shape_node=shape, values=rotate_values)
			self.translate_shape(shape_node=shape, values=translate_values)
	
	def create_transform(self, **kwargs):
		transform_type = kwargs.get('transform_type', 'transform')
		name = kwargs.get('name', 'ninjaControl')
		
		if transform_type == 'joint':
			self.transform = pm.createNode('joint', name=name)
		else:
			self.transform = pm.createNode('transform', name=name)
		
		self.tag_transform()
	
	def set_transform(self, transform=None):
		self.transform = transform
		self.tag_transform()
	
	def fix_shape_names(self):
		shapes_tool.fix_shape_names(self.transform)
		
	def tag_transform(self):
		if self.transform is None:
			return
		
		if pm.attributeQuery('ninjaControl', node=self.transform, exists=True):
			return
		
		pm.addAttr(self.transform, ln='ninjaControl', at='message')
	
	def tag_shape(self, shape_node=None, shape_type=None):
		if shape_node is None or shape_type is None:
			return

		if not pm.attributeQuery('ninjaControlShape', node=self.transform, exists=True):
			pm.addAttr(shape_node, ln='ninjaControlShape', at='message')
		
		if not pm.attributeQuery('ninjaControlShapeType', node=self.transform, exists=True):
			pm.addAttr(shape_node, ln='ninjaControlShapeType', dt='string')
		
		shape_node.ninjaControlShapeType.set(l=False)
		if shape_type.get('builtin', None) is not None:
			shape_node.ninjaControlShapeType.set('builtin:{}'.format(shape_type['builtin']))
		elif shape_type.get('custom', None) is not None:
			shape_node.ninjaControlShapeType.set('custom:{}'.format(shape_type['custom']))
		shape_node.ninjaControlShapeType.set(l=True)
	
	def scale_shape(self, shape_node=None, values=None):
		if shape_node is None or values is None:
			return
		shapes_tool.scale_shape(shape_node=shape_node, values=values)
		if not pm.attributeQuery('ninjaShapeScale', node=shape_node, exists=True):
			pm.addAttr(shape_node, ln='ninjaShapeScale', at='double3')
			pm.addAttr(shape_node, ln='ninjaShapeScaleX', at='double', p='ninjaShapeScale')
			pm.addAttr(shape_node, ln='ninjaShapeScaleY', at='double', p='ninjaShapeScale')
			pm.addAttr(shape_node, ln='ninjaShapeScaleZ', at='double', p='ninjaShapeScale')
		
		shape_node.ninjaShapeScale.set(l=False)
		shape_node.ninjaShapeScale.set(values)
		shape_node.ninjaShapeScale.set(l=True)
	
	def rotate_shape(self, shape_node=None, values=None):
		if shape_node is None or values is None:
			return
		shapes_tool.rotate_shape(shape_node=shape_node, values=values)
		if not pm.attributeQuery('ninjaShapeRotate', node=shape_node, exists=True):
			pm.addAttr(shape_node, ln='ninjaShapeRotate', at='double3')
			pm.addAttr(shape_node, ln='ninjaShapeRotateX', at='double', p='ninjaShapeRotate')
			pm.addAttr(shape_node, ln='ninjaShapeRotateY', at='double', p='ninjaShapeRotate')
			pm.addAttr(shape_node, ln='ninjaShapeRotateZ', at='double', p='ninjaShapeRotate')
		
		shape_node.ninjaShapeRotate.set(l=False)
		shape_node.ninjaShapeRotate.set(values)
		shape_node.ninjaShapeRotate.set(l=True)
	
	def translate_shape(self, shape_node=None, values=None):
		if shape_node is None or values is None:
			return
		shapes_tool.translate_shape(shape_node=shape_node, values=values)
		if not pm.attributeQuery('ninjaShapeTranslate', node=shape_node, exists=True):
			pm.addAttr(shape_node, ln='ninjaShapeTranslate', at='double3')
			pm.addAttr(shape_node, ln='ninjaShapeTranslateX', at='double', p='ninjaShapeTranslate')
			pm.addAttr(shape_node, ln='ninjaShapeTranslateY', at='double', p='ninjaShapeTranslate')
			pm.addAttr(shape_node, ln='ninjaShapeTranslateZ', at='double', p='ninjaShapeTranslate')
		
		shape_node.ninjaShapeTranslate.set(l=False)
		shape_node.ninjaShapeTranslate.set(values)
		shape_node.ninjaShapeTranslate.set(l=True)


def list_shape_types():
	print('\nShape Types : ')
	for shape_type in shape_data.shape_types:
		print('    {}'.format(shape_type))
	print('\n')
		