import pymel.core as pm

from . import base_module
from ... import constants_data
from ... tools import name_builder


class Module(base_module.BaseModule):
	def __init__(self, identifier='rig_asset', version='2023.02.06', constants_key='default'):
		super(Module, self).__init__()
		
		if not hasattr(constants_data, constants_key):
			pm.warning('constants {} not found. switching to use the default constants'.format(constants_key))
			constants_key = 'default'
		
		self.constants_key = constants_key
		self.constants_data = getattr(constants_data, constants_key)
		
		# script data
		self.pre_build_script = ''
		self.post_build_script = ''
		self.pre_module_build_script = ''
		self.post_module_build_script = ''
		self.build_data = ''
		
		# module data
		self.rig_type = 'rig'
		self.module_type = 'asset'
		self.identifier = identifier
		self.version = version
		
		# nodes
		self.nodes = base_module.Nodes()
		for node_key, node_data in self.constants_data.asset_nodes_data.items():
			#node_type = self.constants_data.asset_group_types.get(node_key, node_key)
			self.nodes.initialize(node_key=node_key, node_type=node_data['node_type'])
			
		self.nodes.initialize(node_key='module_data', node_type='module_data')

	def create(self):
		self.find()
		
		if self.all_nodes_exists():
			self.create_hierarchy()
			return
		
		self.set_build_data()
		
		self.run_pre_build_script()
		
		self.build_nodes()
		self.tag_nodes()
		self.create_hierarchy()
		
		self.add_rig_version()
		self.add_rig_vis_attributes()
		
		self.run_post_build_script()

	def build_nodes(self):
		CON = self.constants_data
		nb = name_builder.NameConvention(constants_key=self.constants_key)
		for node_key, node_data in self.constants_data.asset_nodes_data.items():
			#name = nb.create_name(**CON.asset_group_names[node_key])
			name = nb.create_name(**node_data['name'])
			setattr(self.nodes, node_key, self.create_group_node(name))
		
		name = nb.create_name(main_description=CON.asset, secondary_description=CON.module, extension=CON.data)
		self.nodes.module_data = self.create_group_node(name)

	def add_rig_vis_attributes(self):
		pm.addAttr(self.nodes.rig_vis, ln='rigJointsVis', at='bool')
		self.nodes.rig_vis.rigJointsVis.set(k=True)
		pm.addAttr(self.nodes.rig_vis, ln='bindJointsVis', at='bool')
		self.nodes.rig_vis.bindJointsVis.set(k=True)
		pm.addAttr(self.nodes.rig_vis, ln='tipJointsVis', at='bool')
		self.nodes.rig_vis.tipJointsVis.set(k=True)
		pm.addAttr(self.nodes.rig_vis, ln='controlJointsVis', at='bool')
		self.nodes.rig_vis.controlJointsVis.set(k=True)
		pm.addAttr(self.nodes.rig_vis, ln='groupJointsVis', at='bool')
		self.nodes.rig_vis.groupJointsVis.set(k=True)
	
	def add_rig_version(self):
		node = self.nodes.get_node(node_key='modules_grp')
		pm.addAttr(node, ln='ninja_rigVersion', dt='string')
		node.ninja_rigVersion.set(self.version)
	
	def create_group_node(self, group_name):
		if pm.objExists(group_name):
			return pm.PyNode(group_name)
		else:
			return pm.createNode('transform', name=group_name)

	def create_hierarchy(self):
		for node_key, node_data in self.constants_data.asset_nodes_data.items():
			#parent_node_key = self.constants_data.asset_groups[node_key].get('parent', None)
			parent_node_key = node_data['parent']
			if parent_node_key is None:
				continue
			node = self.nodes.get_node(node_key=node_key)
			parent_node = self.nodes.get_node(node_key=parent_node_key)
			pm.parent(node, parent_node)
		
		node = self.nodes.get_node(node_key='module_data')
		parent_node = self.nodes.get_node(node_key='modules_data_grp')
		pm.parent(node, parent_node)
	
	def record_build_data_from_existing_rig(self):
		pass
	
	def set_build_data(self):
		module_data = self.nodes.get_node(node_key='module_data')
		if module_data is not None:
			if pm.attributeQuery('ninja_preBuildScript', node=module_data, exists=True):
				self.pre_build_script = module_data.preBuildScript.get()
			if pm.attributeQuery('ninja_postBuildScript', node=module_data, exists=True):
				self.post_build_script = module_data.postBuildScript.get()
			if pm.attributeQuery('ninja_preModuleBuildScript', node=module_data, exists=True):
				self.pre_module_build_script = module_data.preModuleBuildScript.get()
			if pm.attributeQuery('ninja_postModuleBuildScript', node=module_data, exists=True):
				self.post_module_build_script = module_data.postModuleBuildScript.get()
			if pm.attributeQuery('ninja_buildData', node=module_data, exists=True):
				self.build_data = module_data.buildData.get()
	
	def tag_nodes(self):
		general_data = {
			'rig_type': self.rig_type,
			'module_type': self.module_type,
			'identifier': self.identifier,
			'basename': ''
		}
		
		for node_key in self.constants_data.asset_nodes_data:
			node = self.nodes.get_node(node_key=node_key)
			node_type = self.nodes.get_type(node_key=node_key)
			self.tag_node(node=node, node_type=node_type, **general_data)
		
		node_key = 'module_data'
		node = self.nodes.get_node(node_key=node_key)
		node_type = self.nodes.get_type(node_key=node_key)
		self.tag_node(node=node, node_type=node_type, **general_data)
	
	def all_nodes_exists(self):
		for node_key in self.constants_data.asset_nodes_data:
			if self.nodes.get_node(node_key=node_key) is None:
				return False

		node_key = 'module_data'
		if self.nodes.get_node(node_key=node_key) is None:
			return False
		
		return True
	
	def find(self):
		self.reset_nodes()
		
		module_nodes = self.find_all_module_nodes(module_type=self.module_type)
		
		for node_key in self.constants_data.asset_nodes_data:
			node_type = self.nodes.get_type(node_key=node_key)
			node = self.find_node_from_list(node_list=module_nodes, node_type=node_type)
			setattr(self.nodes, node_key, node)
		
		node_key = 'module_data'
		node_type = self.nodes.get_type(node_key=node_key)
		node = self.find_node_from_list(node_list=module_nodes, node_type=node_type)
		setattr(self.nodes, node_key, node)
	
	def reset_nodes(self):
		for node_key in self.constants_data.asset_nodes_data:
			setattr(self.nodes, node_key, None)
		
		node_key = 'module_data'
		setattr(self.nodes, node_key, None)
