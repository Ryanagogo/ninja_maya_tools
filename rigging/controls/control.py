import pymel.core as pm

import shape_data
from ..tools import shapes


class Control:
	def __init__(self):
		self.transform = None
	
	def create(self, shape_type=None, **kwargs):
		self.create_transform(**kwargs)
		self.set_shape(shape_type=shape_type, **kwargs)
	
	def set_shape(self, shape_type=None, **kwargs):
		data = getattr(shape_data, shape_type)
		
		for info in data.shapes:
			periodic = False
			if info['form'] == 'periodic':
				periodic = True
			
			curve_transform = pm.curve(p=info['cvs'], d=info['degree'], k=info['knots'], per=periodic)
			shape_nodes = curve_transform.getShapes()
			for shape in shape_nodes:
				pm.parent(shape, self.transform, r=True, shape=True)
				self.tag_shape(shape_node=shape, shape_type=shape_type)
			pm.delete(curve_transform)
		
		self.fix_shape_names()
	
	def replace_shape(self, shape_type=None, **kwargs):
		if self.transform is None:
			return
			
		shape_nodes = self.transform.getShapes()
		for shape in shape_nodes:
			pm.delete(shape)
		
		self.set_shape(shape_type=shape_type, **kwargs)
	
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
		shapes.fix_shape_names(self.transform)
		
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

		
		