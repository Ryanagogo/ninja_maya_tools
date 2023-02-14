from maya import cmds
from maya import mel
import pymel.core as pm

# from .. import DEFAULT_CONSTANTS as CON

# reload(CON)


def record_default_transform(node=None):
	if not pm.attributeQuery('defaultTranslate', node=node, exists=True):
		pm.addAttr(node, ln='defaultTranslate', at='double3')
		pm.addAttr(node, ln='defaultTranslateX', at='double', p='defaultTranslate')
		pm.addAttr(node, ln='defaultTranslateY', at='double', p='defaultTranslate')
		pm.addAttr(node, ln='defaultTranslateZ', at='double', p='defaultTranslate')
	if not pm.attributeQuery('defaultRotate', node=node, exists=True):
		pm.addAttr(node, ln='defaultRotate', at='double3')
		pm.addAttr(node, ln='defaultRotateX', at='double', p='defaultRotate')
		pm.addAttr(node, ln='defaultRotateY', at='double', p='defaultRotate')
		pm.addAttr(node, ln='defaultRotateZ', at='double', p='defaultRotate')
	if not pm.attributeQuery('defaultScale', node=node, exists=True):
		pm.addAttr(node, ln='defaultScale', at='double3')
		pm.addAttr(node, ln='defaultScaleX', at='double', p='defaultScale')
		pm.addAttr(node, ln='defaultScaleY', at='double', p='defaultScale')
		pm.addAttr(node, ln='defaultScaleZ', at='double', p='defaultScale')

	t = node.translate.get()
	r = node.rotate.get()
	s = node.scale.get()

	node.defaultTranslate.set(*t)
	node.defaultRotate.set(*r)
	node.defaultScale.set(*s)


def set_default_transform(node=None):
	if pm.attributeQuery('defaultTranslate', node=node, exists=True):
		t = node.defaultTranslate.get()
		node.translate.set(*t)
	if pm.attributeQuery('defaultRotate', node=node, exists=True):
		t = node.defaultRotate.get()
		node.rotate.set(*t)
	if pm.attributeQuery('defaultScale', node=node, exists=True):
		t = node.defaultScale.get()
		node.scale.set(*t)


def tag_as_bind_joint(joint=None):
	if not pm.attributeQuery('bindJoint', node=joint, exists=True):
		pm.addAttr(joint, ln='bindJoint', at='message')


def uniform_scale(node, attr, value=1):
	if not pm.attributeQuery(attr, node=node, exists=True):
		pm.addAttr(node, ln=attr, at='double', dv=value)
		node.attr(attr).set(value, k=True)

	node.attr(attr).connect(node.sx, f=True)
	node.attr(attr).connect(node.sy, f=True)
	node.attr(attr).connect(node.sz, f=True)

	node.sx.set(k=False)
	node.sy.set(k=False)
	node.sz.set(k=False)


def vis_toggle(driver, attr, driven, value=None, shapes=False, title=None):
	if title is not None:
		if not pm.attributeQuery(title, node=driver, exists=True):
			pm.addAttr(driver, ln=title, at='enum', en='---------:')
			driver.SPACE.set(k=True)

	if not pm.attributeQuery(attr, node=driver, exists=True):
		pm.addAttr(driver, ln=attr, at='bool')
		driver.attr(attr).set(k=True)

	if shapes is False:
		driver.attr(attr).connect(driven.visibility, f=True)
	else:
		for shape in driven.getShapes():
			driver.attr(attr).connect(shape.visibility, f=True)

	if value is not None:
		driver.attr(attr).set(value)


def bone_vis_toggle(driver, attr, joint, value=None):
	if not pm.attributeQuery(attr, node=driver, exists=True):
		pm.addAttr(driver, ln=attr, at='bool')
		driver.attr(attr).set(k=True)

	condition_name = '{}_{}_vis_condition'.format(joint.nodeName(), attr)
	if pm.objExists(condition_name):
		condition = pm.PyNode(condition_name)
	else:
		condition = pm.createNode('condition', name=condition_name)
		driver.attr(attr).connect(condition.firstTerm, f=True)
		condition.colorIfTrueR.set(2)
		condition.colorIfFalseR.set(0)

	condition.outColorR.connect(joint.drawStyle, f=True)

	if value is not None:
		driver.attr(attr).set(value)


def cleanup_control_attributes(node, attributes=()):
	translates = ['tx', 'ty', 'tz']
	rotates = ['rx', 'ry', 'rz']
	scales = ['sx', 'sy', 'sz']

	for attr_type in attributes:
		attr_cleaned = False
		if attr_type == 'all' or attr_type == 't':
			attr_cleaned = True
			for attr in translates:
				node.attr(attr).set(k=False, l=True)
		if attr_type == 'all' or attr_type == 'r':
			attr_cleaned = True
			for attr in rotates:
				node.attr(attr).set(k=False, l=True)
		if attr_type == 'all' or attr_type == 's':
			attr_cleaned = True
			for attr in scales:
				node.attr(attr).set(k=False, l=True)

		if not attr_cleaned and pm.attributeQuery(attr_type, node=node, exists=True):
			node.attr(attr_type).set(k=False, l=True)

	node.visibility.set(k=False)

	if pm.attributeQuery('radius', node=node, exists=True):
		node.radius.set(k=False)


def set_joint_label(joint, side='none', label=''):
	#if side == CON.left:
	#	side = 'left'
	#elif side == CON.right:
	#	side = 'right'

	side_value = {'center': 0, 'left': 1, 'right': 2, 'none': 3}
	joint.side.set(side_value[side])
	joint.attr('type').set(18)
	joint.otherType.set(label)


def type_tag(attr=None, source_node=None, destination_node=None, connect=True):
	if attr is None:
		return
	
	if source_node is not None:
		source_node = pm.PyNode(source_node)
		if not pm.attributeQuery(attr, node=source_node, exists=True):
			pm.addAttr(source_node, ln=attr, at='message')
	
	if destination_node is not None:
		destination_node = pm.PyNode(destination_node)
		if not pm.attributeQuery(attr, node=destination_node, exists=True):
			pm.addAttr(destination_node, ln=attr, at='message')
	
	if connect:
		if source_node is not None and destination_node is not None:
			source_node.attr(attr).connect(destination_node.attr(attr), f=True)


def message_attr_tag(attr=None, node=None):
	if attr is None or node is None:
		return
	
	node = pm.PyNode(node)
	
	if not pm.attributeQuery(attr, node=node, exists=True):
		pm.addAttr(node, ln=attr, at='message')


def string_attr_tag(attr=None, node=None, data=None, lock=True):
	if attr is None or node is None:
		return
	
	node = pm.PyNode(node)
	
	if not pm.attributeQuery(attr, node=node, exists=True):
		pm.addAttr(node, ln=attr, dt='string')
	
	if data is not None:
		node.attr(attr).set(l=False)
		node.attr(attr).set(data, l=lock)


def script_string_attr(attr=None, node=None, script=''):
	if attr is None or node is None:
		return
	
	node = pm.PyNode(node)
	
	if not pm.attributeQuery(attr, node=node, exists=True):
		pm.addAttr(node, ln=attr, dt='string')
	
	node.attr(attr).set(l=False)
	node.attr(attr).set(script, l=True)
