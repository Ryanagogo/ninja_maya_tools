import pymel.core as pm

import shape_data
from ..tools import shapes as shapes_tool


class Control:
	def __init__(self):
		self.transform = None
	
	def create(self, shape_type=None, **kwargs):
		self.create_transform(**kwargs)
		self.set_shape(shape_type=shape_type, **kwargs)
	
	def set_shape(self, shape_type=None, **kwargs):
		data = getattr(shape_data, shape_type)
		
		scale_values = kwargs.get('scale_values', None)
		rotate_values = kwargs.get('rotate_values', None)
		translate_values = kwargs.get('translate_values', None)
		
		for info in data.shapes:
			periodic = False
			if info['form'] == 'periodic':
				periodic = True
			
			curve_transform = pm.curve(p=info['cvs'], d=info['degree'], k=info['knots'], per=periodic)
			shape_nodes = curve_transform.getShapes()
			for shape in shape_nodes:
				pm.parent(shape, self.transform, r=True, shape=True)
				self.tag_shape(shape_node=shape, shape_type=shape_type)
				self.scale_shape(shape_node=shape, values=scale_values)
				self.rotate_shape(shape_node=shape, values=rotate_values)
				self.translate_shape(shape_node=shape, values=translate_values)
			
			pm.delete(curve_transform)
		
		self.fix_shape_names()
	
	def replace_shape(self, shape_type=None, **kwargs):
		if self.transform is None:
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
		shape_node.ninjaControlShapeType.set(shape_type)
		shape_node.ninjaControlShapeType.set(l=True)
	
	def scale_shape(self, shape_node=None, values=None):
		if shape_node is None or values is None:
			return
		shapes_tool.scale_shape(shape_node=shape_node, values=values)
	
	def rotate_shape(self, shape_node=None, values=None):
		if shape_node is None or values is None:
			return
		shapes_tool.rotate_shape(shape_node=shape_node, values=values)

	def translate_shape(self, shape_node=None, values=None):
		if shape_node is None or values is None:
			return
		shapes_tool.translate_shape(shape_node=shape_node, values=values)
		