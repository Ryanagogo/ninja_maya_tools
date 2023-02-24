import pymel.core as pm

import node_data
import names


class CopyPaste:
	def __init__(self):
		self.shape_data = []
	
	def copy(self, node=None):
		self.shape_data = node_data.get_shape_data(node=node)
	
	def copy_selected(self):
		selected = pm.ls(sl=True)
		if len(selected) != 1:
			pm.warning('Please select only one item')
			return
		
		self.copy(node=selected[0])
		
	def paste(self, transform=None):
		if transform is None:
			return
		
		shape_nodes = transform.getShapes()
		for shape in shape_nodes:
			pm.delete(shape)
		
		for info in self.shape_data:
			periodic = False
			if info['form'] == 'periodic':
				periodic = True
			
			curve_transform = pm.curve(p=info['positions'], d=info['degree'], k=info['knots'], per=periodic)
			
			shape_nodes = curve_transform.getShapes()
			for shape in shape_nodes:
				pm.parent(shape, transform, r=True, shape=True)
				shape.overrideEnabled.set(info['overrideEnabled'])
				shape.overrideColor.set(info['overrideColor'])
				shape.overrideRGBColors.set(info['overrideRGBColors'])
				shape.overrideColorRGB.set(info['overrideColorRGB'])
				shape.lineWidth.set(info['lineWidth'])
			
			pm.delete(curve_transform)
		
		names.fix_shape_names(transform=transform)
	
	def paste_selected(self):
		currently_selected = pm.ls(sl=True)
		
		selected_transforms = []
		approved_types = ['transform', 'joint']
		for node in currently_selected:
			if pm.nodeType(node) in approved_types:
				selected_transforms.append(node)
				
		# selected_transforms = pm.ls(sl=True, type='transform')
		
		if len(selected_transforms) == 0:
			pm.warning('No transforms selected, please select one or more transforms')
			return
		
		with pm.UndoChunk():
			for transform in selected_transforms:
				self.paste(transform=transform)
			
			pm.select(currently_selected)

	def mirrored_paste(self, transform=None):
		pass
	
	def mirrored_paste_selected(self):
		currently_selected = pm.ls(sl=True)
		
		selected_transforms = []
		approved_types = ['transform', 'joint']
		for node in currently_selected:
			if pm.nodeType(node) in approved_types:
				selected_transforms.append(node)
		
		# selected_transforms = pm.ls(sl=True, type='transform')
		
		if len(selected_transforms) == 0:
			pm.warning('No transforms selected, please select one or more transforms')
			return
		
		with pm.UndoChunk():
			for transform in selected_transforms:
				self.mirrored_paste(transform=transform)
			
			pm.select(currently_selected)
	