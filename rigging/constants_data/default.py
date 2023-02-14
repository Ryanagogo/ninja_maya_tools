from collections import OrderedDict as odict


#################################
# Name Convention
#################################

token_order = [
	'side',
	'main_description',
	'secondary_description',
	'padded_index',
	'extension'
]

#################################
# Suffix
#################################

aim = 'aim'
anchor = 'anchor'
auto = 'auto'
blend = 'blend'
blend_joint = 'blendJnt'
cluster = 'cluster'
control = 'ctrl'
curve = 'curve'
data = 'data'
default = 'default'
distance = 'distance'
group = 'grp'
ik_handle = 'ikHandle'
ik_spline_handle = 'ikSplineHandle'
joint = 'jnt'
locator = 'loc'
module = 'module'
offset = 'offset'
point = 'point'
pole_vector = 'pv'
position = 'position'
rig = 'rig'
fitrig = 'fitrig'
rig_joint = 'rigJnt'
switch = 'switch'
sub = 'sub'
values = 'values'
vector = 'vector'

#################################
# Ik Fk
#################################

fk = 'fk'
ik = 'ik'
ikfk = 'ikfk'
ikfk_attr = 'ikFk'

#################################
# Sides, Areas and Directions
#################################

left = 'lf'
right = 'rt'
middle = 'mid'
upper = 'upper'
lower = 'lower'
up = 'up'

root = 'root'
tip = 'tip'
sub = 'sub'

#################################
# asset
#################################

asset = 'asset'
master_group = 'master'
model_group = 'model'
rig_group = 'rig'
fitrig_group = 'fitrig'
rig_vis = 'rig_vis'
proxy_group = 'proxy'
lores_group = 'lores'
hires_group = 'hires'
modules_group = 'modules'
joints_group = 'joints'

#################################
# Limbs
#################################

bendy = 'bendy'

#################################
# Settings
#################################

neck_number_of_controls = 2
neck_number_of_joints = 3

spine_number_of_controls = 2
spine_number_of_joints = 3


#################################
# Base Names
#################################

look_at_basename = 'lookAt'
eye_socket_basename = 'eyeSocket'

chest_basename = 'chest'
clavicle_basename = 'clavicle'
clavicle_tip_basename = 'shoulder'
cog_basename = 'fly'

foot_basename = 'foot'
god_control_basename = 'god'

hand_basename = 'hand'
head_basename = 'head'

hip_basename = 'pelvis'
hip_control_basename = 'body'
hip_sub_control_basename = 'pelvis'

root_basename = 'ground'
settings_basename = 'gear'

ik_spine_basename = 'ik_spine'
spine_basename = 'spine'
neck_basename = 'neck'

digit_token = 'digit'

#################################
# Fingers
#################################
finger_basename = 'finger'

digit_type_finger = 'finger'
finger_palm = 'palm'

finger_index = 'index'
finger_middle = 'middle'
finger_ring = 'ring'
finger_pinky = 'pinky'
finger_thumb = 'thumb'

#################################
# Toes
#################################
toe_basename = 'finger'

digit_type_toe = 'toe'
toe_palm = 'palm'

toe_index = 'index'
toe_middle = 'middle'
toe_ring = 'ring'
toe_pinky = 'pinky'
toe_thumb = 'thumb'

#################################
# Colors
#################################
red = [1, 0, 0]
green = [0, 1, 0]
blue = [0, 0, 1]
yellow = [1, 1, 0]
light_blue = [0, 1, 1]
pink = [1, 0.5, 0.5]

right_color = red
left_color = light_blue

ik_color = red
fk_color = yellow
center_color = light_blue

#################################
# asset group nodes and hierarchy
#################################
asset_nodes_data = odict(
	[
		('master', dict(
			parent=None,
			node_type='master_group',
			name=dict(main_description=master_group),
		)),
		
		('model', dict(
			parent='master',
			node_type='model_group',
			name=dict(main_description=model_group, extension=group),
		)),
		('lores_grp', dict(
			parent='model',
			node_type='lores_group',
			name=dict(main_description=lores_group, extension=group),
		)),
		('hires_grp', dict(
			parent='model',
			node_type='hires_group',
			name=dict(main_description=hires_group, extension=group),
		)),
		
		('rig_grp', dict(
			parent='master',
			node_type='rig_group',
			name=dict(main_description=rig_group, extension=group),
		)),
		('rig_vis', dict(
			parent='rig_grp',
			node_type='rig_visibility',
			name=dict(main_description=rig_vis),
		)),
		('proxy_grp', dict(
			parent='rig_grp',
			node_type='proxy_group',
			name=dict(main_description=proxy_group, extension=group),
		)),
		('modules_grp', dict(
			parent='rig_grp',
			node_type='modules_group',
			name=dict(main_description=modules_group, extension=group),
		)),
		('modules_data_grp', dict(
			parent='rig_grp',
			node_type='modules_data_group',
			name=dict(main_description=modules_group, secondary_description=data, extension=group),
		)),
		
		('fitrig_grp', dict(
			parent='master',
			node_type='fitrig_group',
			name=dict(main_description=fitrig_group, extension=group),
		)),
		('joints_grp', dict(
			parent='master',
			node_type='joints_group',
			name=dict(main_description=joints_group, extension=group),
		)),
	]
)
