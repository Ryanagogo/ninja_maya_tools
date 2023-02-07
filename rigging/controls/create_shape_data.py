from maya import cmds
from maya import mel
import pymel.core as pm

import os


def create_from_selected():
	accepted_types = ['transform', 'joint']
	for node in pm.ls(sl=True):
		if pm.nodeType(node) in accepted_types:
			create(transform=node)
	

def create(transform=None, name=None, file_path=None, print_data=False):
	approved_types = ['transform', 'joint']
	if pm.nodeType(transform) not in approved_types:
		return
	
	text = ''
	path = os.path.abspath(__file__)
	dir_path = os.path.dirname(path)
	shape_data_path = os.path.join(dir_path, 'shape_data', '{}.py'.format(transform.nodeName()))
	#text += "module path : {}\n".format(dir_path)
	#text += "module shape_data_path : {}\n".format(shape_data_path)
	shapes = transform.getShapes()
	text += "# shape data for : {}\n\n".format(transform.nodeName())
	text += 'shapes = [\n'
	for shape in shapes:
		if pm.nodeType(shape) != 'nurbsCurve':
			continue
		text += '    {\n'
		knots = shape.getKnots()
		cvs = shape.getCVs()
		degree = shape.degree()
		form = shape.form().key
		
		# form
		text += "        'form': '{}',\n".format(form)
		
		# degree
		text += "        'degree': {},\n".format(degree)
		
		# cvs
		text += "        'positions': [\n"
		for index, cv in enumerate(cvs):
			if index < len(cvs) - 1:
				text += "            [{}, {}, {}],\n".format(cv[0], cv[1], cv[2])
			else:
				text += "            [{}, {}, {}]\n".format(cv[0], cv[1], cv[2])
		text += "        ],\n"
		
		# knots
		text += "        'knots': ["
		for index, knot in enumerate(knots):
			if index < len(knots)-1:
				text += "{}, ".format(knot)
			else:
				text += "{}".format(knot)
		text += "]\n"
		text += '    },\n'
	text += ']\n'
	
	if print_data:
		print(text)
		return
	
	print('writing shape data\n')
	print('{}\n'.format(shape_data_path))
	print(text)
	with open(shape_data_path, 'w') as f:
		f.write(text)

