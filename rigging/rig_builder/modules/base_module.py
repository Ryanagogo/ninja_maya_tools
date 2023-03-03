import pymel.core as pm

from ... controls import control
from ... import constants_data
from ... tools import attributes
from ... tools import connections
from ... tools import name_builder


class BaseModule(object):
	def __init__(self):
		self.rig_type = None
		self.module_type = None
		self.identifier = None
		self.basename = None
		
		self.asset = None
		self.module_data = None
		self.node_keys = []
		self.fitrig_keys = []
		
		# script data
		self.pre_build_script = ''
		self.post_build_script = ''
		self.pre_module_build_script = ''
		self.post_module_build_script = ''
		self.build_data = ''
		
		self.module_data = None
		#self.controls_group = None
		self.rig_group = None
		self.fitrig_group = None
		
		self.parent_list = []

	def set_build_data(self):
		if self.module_data is None:
			pm.warning('set_build_data : module data not set')
			return
			
		if pm.attributeQuery('preBuildScript', node=self.module_data, exists=True):
			self.pre_build_script = self.module_data.preBuildScript.get()
		if pm.attributeQuery('postBuildScript', node=self.module_data, exists=True):
			self.post_build_script = self.module_data.postBuildScript.get()
		if pm.attributeQuery('preModuleBuildScript', node=self.module_data, exists=True):
			self.pre_module_build_script = self.module_data.preModuleBuildScript.get()
		if pm.attributeQuery('postModuleBuildScript', node=self.module_data, exists=True):
			self.post_module_build_script = self.module_data.postModuleBuildScript.get()
		if pm.attributeQuery('buildData', node=self.module_data, exists=True):
			self.build_data = self.module_data.buildData.get()
	
	def run_pre_build_script(self):
		self.run_script(self.pre_build_script)
	
	def run_post_build_script(self):
		self.run_script(self.post_build_script)
	
	def tag_nodes(self):
		cancel = False
		if self.rig_type is None:
			pm.warning('tag_nodes : rig_type not set')
			cancel = True
		if self.module_type is None:
			pm.warning('tag_nodes :module_type not set')
			cancel = True
		if self.identifier is None:
			pm.warning('tag_nodes : identifier not set')
			cancel = True
		if self.basename is None:
			pm.warning('tag_nodes : basename not set')
			cancel = True
		
		if cancel:
			return
		
		general_data = {
			'rig_type': self.rig_type,
			'module_type': self.module_type,
			'identifier': self.identifier,
			'basename': self.basename
		}
		
		for key in self.node_keys:
			self.tag_node(node=getattr(self, key), node_type=key, **general_data)
	
	def find_all_module_nodes(self, module_type=None, module_identifier=None):
		if module_type is None:
			return
		
		module_nodes = []
		
		for node in pm.ls(type='transform'):
			if not pm.attributeQuery('moduleType', node=node, exists=True):
				continue
			
			if node.moduleType.get() != module_type:
				continue
				
			# get all nodes of module type, identifier is not important
			if module_identifier is None:
				module_nodes.append(node)
			# get all nodes of module type that have specific identifier
			elif pm.attributeQuery('moduleIdentifier', node=node, exists=True):
				if node.moduleIdentifier.get() == module_identifier:
					module_nodes.append(node)
		
		return module_nodes
	
	def find_node_from_list(self, node_list=(), node_type=None):
		if node_type is None:
			return None
		
		for node in node_list:
			node = pm.PyNode(node)
			if not pm.attributeQuery('moduleNodeType', node=node, exists=True):
				continue
			if node_type == node.moduleNodeType.get():
				return node
		
		return None
	
	def tag_node(self, node=None, rig_type=None, module_type=None, basename=None, identifier=None, node_type=None):
		if node is None:
			return
		
		self.tag_default_attrs(node=node)
		
		if rig_type is not None:
			self.tag_rig_type(rig_type=rig_type, node=node)
		
		if module_type is not None:
			self.tag_module_type(module_type=module_type, node=node)
		
		if identifier is not None:
			self.tag_module_identifier(identifier=identifier, node=node)
		
		if basename is not None:
			self.tag_module_basename(basename=basename, node=node)
		
		if node_type is not None:
			self.tag_module_node_type(node_type=node_type, node=node)
	
	def tag_default_attrs(self, node=None):
		if node is None:
			return
		
		node = pm.PyNode(node)
		attributes.message_attr_tag(attr='faceRigModule', node=node)
	
	def tag_rig_type(self, rig_type=None, node=None):
		if rig_type is None or node is None:
			return
		
		node = pm.PyNode(node)
		attributes.string_attr_tag(attr='rig_type', node=node, data=rig_type)
	
	def tag_module_type(self, module_type=None, node=None):
		if module_type is None or node is None:
			return
		
		node = pm.PyNode(node)
		attributes.string_attr_tag(attr='moduleType', node=node, data=module_type)
	
	def tag_module_identifier(self, identifier=None, node=None):
		if identifier is None or node is None:
			return
		
		node = pm.PyNode(node)
		attributes.string_attr_tag(attr='moduleIdentifier', node=node, data=identifier)
	
	def tag_module_basename(self, basename=None, node=None):
		if basename is None or node is None:
			return
		
		node = pm.PyNode(node)
		attributes.string_attr_tag(attr='moduleBasename', node=node, data=basename)
	
	def tag_module_node_type(self, node_type=None, node=None):
		if node_type is None or node is None:
			return
		
		node = pm.PyNode(node)
		attributes.string_attr_tag(attr='moduleNodeType', node=node, data=node_type)
	
	def setup_module_node_attributes(self, node=None):
		if node is None:
			return
		
		node = pm.PyNode(node)
		attributes.script_string_attr(attr='preBuildScript', node=node)
		attributes.script_string_attr(attr='postBuildScript', node=node)
		attributes.script_string_attr(attr='preModuleBuildScript', node=node)
		attributes.script_string_attr(attr='postModuleBuildScript', node=node)
		attributes.script_string_attr(attr='buildData', node=node)
	
	def run_script(self, script=''):
		exec(script)
	
	def find(self):
		if self.module_type is None:
			pm.warning('module type is not defined')
			return
		
		self.reset_nodes()
		
		module_nodes = self.find_all_module_nodes(module_type=self.module_type)
		
		for key in self.node_keys:
			node = self.find_node_from_list(node_list=module_nodes, node_type=key)
			setattr(self, key, node)
	
	def reset_nodes(self):
		for key in self.node_keys:
			setattr(self, key, None)

	def set_default_module_nodes_hierarchy(self):
		pm.parent(self.module_data, self.asset.module_data)
		# pm.parent(self.controls_group, self.asset.controls_group)
		pm.parent(self.rig_group, self.asset.rig_group)
		pm.parent(self.fitrig_group, self.asset.fitrig_group)
	
	def set_parents_from_data(self):
		for parent_item in self.parent_list:
			parent_module = parent_item['parent_module']
			parent_node_attr = parent_item['parent_node']
			set_child_attrs = parent_item['set_child_attrs']
			child_node_attr = parent_item['child_node']
			parent_type = parent_item['parent_type']
			
			parent_node = getattr(parent_module, parent_node_attr)
			child_node = getattr(self, child_node_attr)
			
			if parent_type == 'constraint':
				pm.parent(child_node, parent_node)
			elif parent_type == 'matrix_constraint':
				pm.parent(child_node, parent_node)
			else:
				pm.parent(child_node, parent_node)
				
			for child_attr_data in set_child_attrs:
				attr = child_attr_data.get('attr', None)
				value = child_attr_data.get('value', None)
				
				if attr is None or value is None:
					continue
				
				child_node.attr(attr).set(value)
				
	def initialize_module_data(self, data=None):
		if data is None:
			return
		for key in data:
			if not hasattr(self, key):
				continue
			setattr(self, key, data[key])
	
	def add_rig_pose(self, driver_node=None, driven_node=None, poses=('default', 'anim')):
		if driver_node is None or driven_node is None:
			return
		
		if not pm.attributeQuery('rigPose', node=driver_node, exists=True):
			enum = ''
			for pose in poses:
				enum += '{}:'.format(pose)
			pm.addAttr(driver_node, ln='rigPose', at='enum', en=enum)
			driver_node.rigPose.set(k=True)
		
		basename = driven_node.nodeName()
		rig_pose_choice = pm.createNode('choice', name='{}_rigPose_choice'.format(basename))
		rig_pose_choice.output.connect(driven_node.offsetParentMatrix)
		driver_node.rigPose.connect(rig_pose_choice.selector)
		
		for index, pose in enumerate(poses):
			compose_matrix = pm.createNode('composeMatrix', name='{}_{}_rigPose_composeMatrix'.format(basename, pose))
			compose_matrix.outputMatrix.connect(rig_pose_choice.input[index])
			
			for attr in ['it', 'itx', 'ity', 'itz', 'ir', 'irx', 'iry', 'irz', 'is', 'isx', 'isy', 'isz']:
				compose_matrix.attr(attr).set(k=True)


class Nodes:
	def __init__(self):
		pass
	
	def initialize(self, node_key=None, node_type=None):
		setattr(self, node_key, None)
		setattr(self, '{}_type'.format(node_key), node_type)
	
	def get_node(self, node_key):
		if node_key is None:
			return None
		return getattr(self, node_key, None)
	
	def get_type(self, node_key):
		if node_key is None:
			return None
		return getattr(self, '{}_type'.format(node_key), None)
	
	def create_group(self, node_key=None, **kwargs):
		print('Nodes | create_group | {} | {}'.format(node_key, kwargs))
		if node_key is None:
			return
		
		name = kwargs.get('name', None)
		if name is None:
			setattr(self, node_key, None)
			return
		
		node = pm.createNode('transform', name=name)
		setattr(self, node_key, node)
		return node
	
	def create_control(self, node_key=None, **kwargs):
		print('Nodes | create_control | {} | {}'.format(node_key, kwargs))
		if node_key is None:
			return
		
		control_data = kwargs.get('control_data', None)
		if control_data is None:
			setattr(self, node_key, None)
			return

		control_object = control.Control()
		node = control_object.create(**control_data)
		setattr(self, node_key, node)
		return node

		
		