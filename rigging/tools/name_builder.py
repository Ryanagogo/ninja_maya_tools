from .. import constants_data
import pymel.core as pm


class NameConvention:
	def __init__(self, constants_key='default'):
		if not hasattr(constants_data, constants_key):
			pm.warning('constants {} not found. switching to use the default constants'.format(constants_key))
			constants_key = 'default'
			
		self.constants_data = getattr(constants_data, constants_key)
		self.name_convention = self.constants_data.token_order
	
	def create_name(self, **kwargs):
		print('NameConvention | create_name', kwargs)
		name = ''
		separator = ''
		for token_key in self.constants_data.token_order:
			token = kwargs.get(token_key, None)
			if token is None:
				continue
			name += '{}{}'.format(separator, token)
			separator = '_'
		
		return name
	
	def set_constant(self, constants_module=None):
		self.constants_data = getattr(constants_data, constants_module)
