import maya.cmds as cmds
import maya.mel as mel
import pymel.core as pm

import glob
import os
import json


def check_ninja_custom_data_package():
	maya_dir = pm.internalVar(userAppDir=True)
	scripts_dir = 'scripts'
	data_dir = 'ninja_custom_data'
	data_path = os.path.join(maya_dir, scripts_dir, data_dir)
	if not os.path.exists(data_path):
		os.makedirs(data_path)
		add_package_init_file(folder=data_path)
	
	return data_path
	
	
def add_package_init_file(folder=None):
	if folder is None:
		return
	
	init_path = os.path.join(folder, '__init__.py')
	if os.path.exists(init_path):
		return
	
	with open(init_path, 'w') as init_file:
		pass
	
	
def save_settings_data(settings_file=None, key=None, data=None):
	if settings_file is None or key is None or data is None:
		return
	
	data_for_json = {}
	
	data_path = check_ninja_custom_data_package()
	settings_path = os.path.join(data_path, settings_file)
	
	if os.path.exists(settings_path):
		with open(settings_path) as json_file:
			data_for_json = json.load(json_file)
	
	data_for_json[key] = data
	
	with open(settings_path, "w") as json_file:
		json.dump(data_for_json, json_file)
