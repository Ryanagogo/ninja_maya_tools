import pymel.core as pm

from ...controls import control
from ...tools import connections
# from ..tools import shape_helper
# from ..tools import copy_node
from ...tools import attributes
# from ..tools import fitrig_nodes

from ... import DEFAULT_CONSTANTS as CON


class Module:
	def __init__(self, asset_module=None, god_control_module=None, basename=CON.root_basename, specific_module='group'):
		self.asset_module = asset_module
		self.basename = basename
		self.module = 'root'
		self.god_control_module = god_control_module
		self.specific_module = specific_module
		self.module_name = self.specific_module
		self.rig_grp = None

		self.module_data = None
		self.build_control_offsets = False

		self.control_01 = None
		self.control_02 = None
		self.control_03 = None

		self.control_01_offset = None
		self.control_02_offset = None
		self.control_03_offset = None

		self.joint = None

		self.fitrig = FitRig(basename=self.basename, specific_module=specific_module, asset_module=self.asset_module)

	def setAssetModule(self, asset_module=None):
		self.asset_module = asset_module

	def create(self, build_control_offsets=None):
		self.fitrig.find()
		if not self.fitrig.fitrig_exists:
			pm.warning('{} fitrig does not exist, can not build {} rig'.format(self.module, self.specific_module))
			return

		if build_control_offsets is not None:
			self.build_control_offsets = build_control_offsets

		self.build_nodes()
		self.tag_bind_joints()
		self.create_hierarchy()
		self.set_positions()
		self.set_shapes()
		self.set_joints_drawstyle()
		self.cleanup()

	def find_fitrig(self):
		self.fitrig.find()

	def create_fitrig(self):
		self.fitrig.create()

	def delete_fitrig(self):
		self.fitrig.delete()

	def integrate_into_fitrig(self):
		self.fitrig.integrate_into_rig()

	def build_nodes(self):
		self.module_data = pm.createNode('transform', name='{}_{}_{}'.format(self.basename, CON.module, CON.data))

		self.rig_grp = pm.createNode('transform', name='{}_grp'.format(self.basename, CON.group))
		self.control_01 = pm.createNode('transform', name='{}_{}'.format(self.basename, CON.control))
		self.control_02 = pm.createNode('transform', name='{}_{}_01_{}'.format(self.basename, CON.sub, CON.control))
		self.control_03 = pm.createNode('transform', name='{}_{}_02_{}'.format(self.basename, CON.sub, CON.control))

		if self.build_control_offsets:
			self.control_01_offset = pm.createNode('transform', name='{}_{}_{}'.format(self.basename, CON.control, CON.offset))
			self.control_02_offset = pm.createNode('transform', name='{}_{}_01_{}_{}'.format(self.basename, CON.sub, CON.control, CON.offset))
			self.control_03_offset = pm.createNode('transform', name='{}_{}_02_{}_{}'.format(self.basename, CON.sub, CON.control, CON.offset))

		pm.select(cl=True)
		self.joint = pm.joint(name='{}_{}'.format(self.basename, CON.joint))

	def tag_bind_joints(self):
		attributes.tag_as_bind_joint(self.joint)

	def create_hierarchy(self):
		pm.parent(self.joint, self.control_03)
		if self.build_control_offsets:
			pm.parent(self.control_03, self.control_03_offset)
			pm.parent(self.control_03_offset, self.control_02)
			pm.parent(self.control_02, self.control_02_offset)
			pm.parent(self.control_02_offset, self.control_01)
			pm.parent(self.control_01, self.control_01_offset)
			pm.parent(self.control_01_offset, self.rig_grp)
		else:
			pm.parent(self.control_03, self.control_02)
			pm.parent(self.control_02, self.control_01)
			pm.parent(self.control_01, self.rig_grp)

	def set_positions(self):
		copy_node.copy_transforms(self.fitrig.control_01, self.rig_grp, transforms='trs')
		copy_node.copy_transforms(self.fitrig.control_01, self.control_01, transforms='trs')
		copy_node.copy_transforms(self.fitrig.control_01, self.control_02, transforms='trs')
		copy_node.copy_transforms(self.fitrig.control_01, self.control_03, transforms='trs')
		copy_node.copy_transforms(self.fitrig.control_01, self.joint)

	def set_shapes(self):
		shape_helper.fitrig_copy_shapes(self.fitrig.control_01, self.control_01)
		shape_helper.fitrig_copy_shapes(self.fitrig.control_02, self.control_02)
		shape_helper.fitrig_copy_shapes(self.fitrig.control_03, self.control_03)

	def integrate_into_rig(self):
		if self.asset_module is not None:
			pm.parent(self.rig_grp, self.asset_module.control_grp)
			pm.parent(self.module_data, self.asset_module.modules_group)

		if self.god_control_module is not None:
			layout_control_name = '{}_layout_ctrl'.format(self.god_control_module.basename)
			if hasattr(self.god_control_module, 'layout_control') and pm.objExists(layout_control_name):
				connections.matrix_constraint(self.god_control_module.sub_control, self.rig_grp)
			else:
				connections.matrix_constraint(self.god_control_module.control, self.rig_grp)

	def set_joints_drawstyle(self):
		attributes.bone_vis_toggle(self.asset_module.rig_vis, 'bindJointsVis', self.joint, value=1)

	def cleanup(self):
		attributes.cleanup_control_attributes(self.control_01, ['s'])
		attributes.cleanup_control_attributes(self.control_02, ['s'])
		attributes.cleanup_control_attributes(self.control_03, ['s'])

		attributes.set_joint_label(self.joint, 'center', 'root')

		self.setup_sub_control_vis()

	def setup_sub_control_vis(self):
		attributes.vis_toggle(self.control_01, 'subControlVis', self.control_02, False, shapes=True)
		attributes.vis_toggle(self.control_01, 'subControlVis', self.control_03, False, shapes=True)


class FitRig:
	def __init__(self, basename='root', specific_module='root', asset_module=None):
		self.asset_module = asset_module
		self.basename = basename

		self.module = 'root'
		self.specific_module = specific_module

		self.module_data = None

		self.fitrig_exists = False

		self.group = None
		self.control_01 = None
		self.control_02 = None
		self.control_03 = None

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
		self.control_01 = connections.find_connected('control01Node', fitrig_data_node)
		self.control_02 = connections.find_connected('control02Node', fitrig_data_node)
		self.control_03 = connections.find_connected('control03Node', fitrig_data_node)

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
			'shape_type': 'ground',
			'name': 'fitrig_{}_01_ctrl'.format(self.basename),
			'radius': 55,
			'direction': 'y',
			'use_color': True,
			'color': [1, 1, 0]
		}
		self.control_01 = control.create(**kwargs)
		kwargs = {
			'shape_type': 'circle',
			'name': 'fitrig_{}_02_ctrl'.format(self.basename),
			'radius': 38,
			'axis': 'y',
			'use_color': True,
			'color': [0, 1, 1]
		}
		self.control_02 = control.create(**kwargs)
		kwargs = {
			'shape_type': 'circle',
			'name': 'fitrig_{}_03_ctrl'.format(self.basename),
			'radius': 35,
			'axis': 'y',
			'use_color': True,
			'color': [1, 0, 0]
		}
		self.control_03 = control.create(**kwargs)

	def create_custom_attributes(self):
		attributes.type_tag('fitrigNode', self.module_data)
		attributes.type_tag('fitrigNode', self.group)
		attributes.type_tag('fitrigNode', self.control_01)
		attributes.type_tag('fitrigNode', self.control_02)
		attributes.type_tag('fitrigNode', self.control_03)

		attributes.type_tag('fitrigData', self.module_data)

		attributes.type_tag('groupNode', self.module_data, self.group)
		attributes.type_tag('control01Node', self.module_data, self.control_01)
		attributes.type_tag('control02Node', self.module_data, self.control_02)
		attributes.type_tag('control03Node', self.module_data, self.control_03)

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
		connections.FitRig.connect_anim_controls_vis(self, self.control_01)
		connections.FitRig.connect_anim_controls_vis(self, self.control_02)
		connections.FitRig.connect_anim_controls_vis(self, self.control_03)

		if self.asset_module is not None:
			self.asset_module.fitrig.modules_data_grp.fitrig_controls_vis.connect(self.group.fitrig_controls_vis)
			self.asset_module.fitrig.modules_data_grp.anim_controls_vis.connect(self.group.anim_controls_vis)
			self.asset_module.fitrig.modules_data_grp.anim_fk_controls_vis.connect(self.group.anim_fk_controls_vis)
			self.asset_module.fitrig.modules_data_grp.anim_ik_controls_vis.connect(self.group.anim_ik_controls_vis)
			self.asset_module.fitrig.modules_data_grp.control_orientations_vis.connect(self.group.control_orientations_vis)

	def create_hierarchy(self):
		pm.parent(self.control_01, self.group)
		pm.parent(self.control_02, self.control_01)
		pm.parent(self.control_03, self.control_02)

		if self.asset_module is not None:
			pm.parent(self.group, self.asset_module.fitrig.modules_group)
			pm.parent(self.module_data, self.asset_module.fitrig.modules_data_grp)

	def set_default_positions(self):
		self.group.translate.set([0, 0, 0])

	def integrate_into_rig(self):
		pass

	def cleanup(self):
		for attr in ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz']:
			self.control_02.attr(attr).set(k=False, l=True)
			self.control_03.attr(attr).set(k=False, l=True)

		self.control_01.visibility.set(k=False)
		self.control_02.visibility.set(k=False)
		self.control_03.visibility.set(k=False)

	def get_data(self):
		data = {'positions': {}, 'shapes': {}, 'attributes': {}}

		data['positions']['group'] = fitrig_nodes.get_transforms(self.group)
		data['positions']['control_01'] = fitrig_nodes.get_transforms(self.control_01)
		data['positions']['control_02'] = fitrig_nodes.get_transforms(self.control_02)
		data['positions']['control_03'] = fitrig_nodes.get_transforms(self.control_03)

		data['shapes']['control_01'] = shape_helper.fitrig_get_shape_data(self.control_01)
		data['shapes']['control_02'] = shape_helper.fitrig_get_shape_data(self.control_02)
		data['shapes']['control_03'] = shape_helper.fitrig_get_shape_data(self.control_03)

		data['attributes']['basename'] = self.basename
		data['attributes']['specific_module'] = self.specific_module

		return data

	def set_data(self, data, set_positions=True, set_orientations=True, set_shapes=True, set_attributes=False):
		if set_positions:
			fitrig_nodes.set_transforms(self.group, data['positions']['group'])
			fitrig_nodes.set_transforms(self.control_01, data['positions']['control_01'])
			fitrig_nodes.set_transforms(self.control_02, data['positions']['control_02'])
			fitrig_nodes.set_transforms(self.control_03, data['positions']['control_03'])
		if set_shapes:
			shape_helper.fitrig_set_shapes_from_data(self.control_01, data['shapes']['control_01'])
			shape_helper.fitrig_set_shapes_from_data(self.control_02, data['shapes']['control_02'])
			shape_helper.fitrig_set_shapes_from_data(self.control_03, data['shapes']['control_03'])
		if set_attributes:
			self.basename = data['attributes']['basename']
			self.specific_module = data['attributes']['specific_module']

	def set_attribute_data(self, data):
		self.basename = data['attributes']['basename']
		self.specific_module = data['attributes']['specific_module']
