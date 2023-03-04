import pymel.core as pm
import pymel.core.datatypes as dt

from . import base_module
from ... import constants_data
from ... tools import name_builder

'''
from ...controls import control
from ...tools import connections
# from ..tools import shape_helper
# from ..tools import copy_node
from ...tools import attributes
# from ..tools import fitrig_nodes

from ... import DEFAULT_CONSTANTS as CON
'''


class Module(base_module.BaseModule):
	def __init__(self, identifier='god_control', basename='god', constants_key='default'):
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
		self.module_type = 'god_control'
		self.identifier = identifier
		
		# self.asset_module = asset_module
		self.basename = basename
		
		self.module_data_parent = None
		self.group_parent = None
		
		# nodes
		CON = self.constants_data
		nb = name_builder.NameConvention(constants_key=self.constants_key)
		self.nodes_data = dict(
			module_data=dict(
				build_type='transform',
				parent_module=None,
				parent_node_key=None,
				parent_node_name=None,
				node_type='module_data',
				name=nb.create_name(main_description=self.basename, secondary_description=CON.module, extension=CON.data),
			),
			group=dict(
				build_type='transform',
				parent_module=None,
				parent_node_key=None,
				parent_node_name=None,
				node_type='group',
				name=nb.create_name(main_description=self.basename, extension=CON.group),
			),
			control=dict(
				build_type='control',
				parent_module=None,
				parent_node_key='group',
				parent_node_name=None,
				node_type='control',
				control_data=dict(
					name=nb.create_name(main_description=self.basename, extension=CON.control),
					shape_type='root', scale_values=[60, 60, 60], rgb_color=[1, 1, 0]
				)
			),
			sub_control=dict(
				build_type='control',
				parent_module=None,
				parent_node_key='control',
				parent_node_name=None,
				node_type='sub_control',
				control_data=dict(
					name=nb.create_name(main_description=self.basename, secondary_description=CON.sub, extension=CON.control),
					shape_type='gear', scale_values=[10, 10, 10], rgb_color=[1, 1, 1], line_width=3
				)
			),
		)
		
		self.nodes = base_module.Nodes()
		for node_key, node_data in self.nodes_data.items():
			self.nodes.initialize(node_key=node_key, node_type=node_data['node_type'])
	
	def set_node_data(self, node_key=None, data_key=None, data=None):
		if node_key is None or data_key is None or data is None:
			return
		
		if not hasattr(self, 'nodes_data'):
			return
		
		if node_key not in self.nodes_data:
			return
		
		self.nodes_data[node_key][data_key] = data
		
	def __repr__(self):
		data = {}
		for node_key, node_data in self.nodes_data.items():
			node = self.nodes.get_node(node_key=node_key)
			data[node_key] = node
		return '{} | {}'.format(self.__module__, str(data))
	
	def create(self):
		self.set_build_data()
		
		self.run_pre_build_script()
		
		self.build_nodes()
		self.tag_nodes()
		self.create_hierarchy()
		
		self.setup_rig_pose_systems()
		self.add_rig_version()
		self.add_rig_vis_attributes()
		
		self.run_post_build_script()
	
	def build_nodes(self):
		for node_key, node_data in self.nodes_data.items():
			build_type = node_data.get('build_type', None)
			if build_type is None:
				continue
			if build_type == 'control':
				control_data = node_data.get('control_data', None)
				if control_data is None:
					continue
				self.nodes.create_control(node_key=node_key, control_data=control_data)
			else:
				name = node_data.get('name', None)
				if name is None:
					continue
				self.nodes.create_group(node_key=node_key, name=name)
	
	def create_hierarchy(self):
		for node_key, node_data in self.nodes_data.items():
			parent_module = node_data.get('parent_module', None)
			parent_node_key = node_data.get('parent_node_key', None)
			parent_node_name = node_data.get('parent_node_name', None)
			parent_node = None
			
			if parent_module is not None:
				parent_node = parent_module.nodes.get_node(node_key=parent_node_key)
			elif parent_node_key is not None:
				parent_node = self.nodes.get_node(node_key=parent_node_key)
			elif parent_node_name is not None:
				if pm.objExists(parent_node_name):
					parent_node = pm.PyNode(parent_node_name)
				
			node = self.nodes.get_node(node_key=node_key)
			
			if node is None or parent_node is None:
				continue
				
			pm.parent(node, parent_node)
	
	def add_rig_version(self):
		pass
	
	def add_rig_vis_attributes(self):
		pass
	
	def setup_rig_pose_systems(self):
		group_node = self.nodes.get_node(node_key='group')
		if group_node is None:
			return
		
		controls = [
			self.nodes.get_node(node_key='control'),
			self.nodes.get_node(node_key='sub_control')
		]
		
		for control in controls:
			self.add_rig_pose(driver_node=group_node, driven_node=control)
	
	def record_build_data_from_existing_rig(self):
		pass
	
	def setup_global_scale_feature(self):
		# attributes.uniform_scale(self.control, 'globalScale')
		pass
	
	def cleanup(self):
		# attributes.cleanup_control_attributes(self.control)
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
	
	'''
	def set_positions(self):
		t = pm.xform(self.fitrig.control, query=True, ws=True, t=True)
		ro = pm.xform(self.fitrig.control, query=True, ws=True, ro=True)

		pm.xform(self.rig_grp, ws=True, t=t)
		pm.xform(self.rig_grp, ws=True, ro=ro)

	def set_shapes(self):
		shape_helper.fitrig_copy_shapes(self.fitrig.control, self.control)

		bb = pm.exactWorldBoundingBox(self.control.getShape(), ii=True)
		v1 = dt.Vector(bb[0], 0, bb[2])
		v2 = dt.Vector(bb[3], 0, bb[5])
		length = v1.distanceTo(v2)
		radius = length * 0.125

		cvs = self.sub_control.cv
		pm.scale(cvs, radius, radius, radius, r=True, p=[0, 0, 0])
	'''
	
	'''
	def integrate_into_rig(self):
		if self.asset_module is not None:
			pm.parent(self.rig_grp, self.asset_module.control_grp)
			pm.parent(self.module_data, self.asset_module.modules_group)

	def setup_layout_control_vis_toggle(self):
		if not pm.attributeQuery('layoutControl', node=self.control, exists=True):
			pm.addAttr(self.control, ln='layoutControl', at='bool')
			self.control.layoutControl.set(0, k=True)

		self.control.layoutControl.connect(self.sub_control.visibility)
	'''
	
	
'''
class FitRig:
	def __init__(self, basename='god', specific_module='god', asset_module=None):
		self.asset_module = asset_module
		self.basename = basename

		self.module = 'god_control'
		self.specific_module = specific_module

		self.module_data = None

		self.fitrig_exists = False

		self.group = None
		self.control = None

	def find(self):
		fitrig_data_node = None
		for node in pm.ls(type='transform'):
			if not pm.attributeQuery('fitrigData', node=node, exists=True):
				continue
			if not pm.attributeQuery('fitrigModule', node=node, exists=True):
				continue
			if not pm.attributeQuery('fitrigSpecificModule', node=node, exists=True):
				continue
			if node.fitrigSpecificModule.get() == self.specific_module:
				fitrig_data_node = node
				break

		if fitrig_data_node is None:
			return

		self.fitrig_exists = True

		self.module_data = fitrig_data_node
		self.group = connections.find_connected('groupNode', fitrig_data_node)
		self.control = connections.find_connected('controlNode', fitrig_data_node)

	def create(self):
		self.build_nodes()
		self.create_custom_attributes()
		self.create_connections()
		self.create_hierarchy()
		self.set_default_positions()
		self.cleanup()

	def delete(self):
		pass

	def build_nodes(self):
		self.module_data = pm.createNode('transform', name='fitrig_{}_module_data'.format(self.basename))
		self.group = pm.createNode('transform', name='fitrig_{}_grp'.format(self.basename))

		kwargs = {
			'shape_type': 'root',
			'name': 'fitrig_{}_ctrl'.format(self.basename),
			'radius': 60,
			'axis': 'y',
			'use_color': True,
			'color': [1, 1, 0]
		}
		self.control = control.create(**kwargs)

	def create_custom_attributes(self):
		attributes.type_tag('fitrigNode', self.module_data)
		attributes.type_tag('fitrigNode', self.group)
		attributes.type_tag('fitrigNode', self.control)

		attributes.type_tag('fitrigData', self.module_data)

		attributes.type_tag('groupNode', self.module_data, self.group)
		attributes.type_tag('controlNode', self.module_data, self.control)

		pm.addAttr(self.module_data, ln='fitrigModule', dt='string')
		self.module_data.fitrigModule.set(self.module)

		pm.addAttr(self.module_data, ln='fitrigSpecificModule', dt='string')
		self.module_data.fitrigSpecificModule.set(self.specific_module)

		pm.addAttr(self.module_data, ln='fitrigBasename', dt='string')
		self.module_data.fitrigBasename.set(self.basename)

		pm.addAttr(self.group, ln='fitrig_controls_vis', at='bool')
		pm.addAttr(self.group, ln='anim_controls_vis', at='bool')
		pm.addAttr(self.group, ln='anim_fk_controls_vis', at='bool')
		pm.addAttr(self.group, ln='anim_ik_controls_vis', at='bool')
		pm.addAttr(self.group, ln='control_orientations_vis', at='bool')

		self.group.fitrig_controls_vis.set(k=True)
		self.group.anim_controls_vis.set(k=True)
		self.group.anim_fk_controls_vis.set(k=True)
		self.group.anim_ik_controls_vis.set(k=True)
		self.group.control_orientations_vis.set(k=True)

	def create_connections(self):
		connections.FitRig.connect_anim_controls_vis(self, self.control)

		if self.asset_module is not None:
			self.asset_module.fitrig.modules_data_grp.fitrig_controls_vis.connect(self.group.fitrig_controls_vis)
			self.asset_module.fitrig.modules_data_grp.anim_controls_vis.connect(self.group.anim_controls_vis)
			self.asset_module.fitrig.modules_data_grp.anim_fk_controls_vis.connect(self.group.anim_fk_controls_vis)
			self.asset_module.fitrig.modules_data_grp.anim_ik_controls_vis.connect(self.group.anim_ik_controls_vis)
			self.asset_module.fitrig.modules_data_grp.control_orientations_vis.connect(self.group.control_orientations_vis)

	def create_hierarchy(self):
		pm.parent(self.control, self.group)

		if self.asset_module is not None:
			pm.parent(self.group, self.asset_module.fitrig.modules_group)
			pm.parent(self.module_data, self.asset_module.fitrig.modules_data_grp)

	def set_default_positions(self):
		self.group.translate.set([0, 0, 0])

	def integrate_into_rig(self):
		pass

	def cleanup(self):
		self.control.visibility.set(k=False)

	def get_data(self):
		data = {'positions': {}, 'shapes': {}, 'attributes': {}}

		data['positions']['group'] = fitrig_nodes.get_transforms(self.group)
		data['positions']['control'] = fitrig_nodes.get_transforms(self.control)

		data['shapes']['control'] = shape_helper.fitrig_get_shape_data(self.control)

		data['attributes']['basename'] = self.basename
		data['attributes']['specific_module'] = self.specific_module

		return data

	def set_data(self, data, set_positions=True, set_orientations=True, set_shapes=True, set_attributes=False):
		if set_positions:
			fitrig_nodes.set_transforms(self.group, data['positions']['group'])
			fitrig_nodes.set_transforms(self.control, data['positions']['control'])
		if set_shapes:
			shape_helper.fitrig_set_shapes_from_data(self.control, data['shapes']['control'])
		if set_attributes:
			self.basename = data['attributes']['basename']
			self.specific_module = data['attributes']['specific_module']

	def set_attribute_data(self, data):
		self.basename = data['attributes']['basename']
		self.specific_module = data['attributes']['specific_module']
'''
