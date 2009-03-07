# -*- coding: utf-8 -*-

import os, os.path
import Matroska

class Convert:
	def __init__(self):
		self.type = None
		self.file = None
		self.filters = None

	def __repr__(self):
		"""String representation."""
		return '<%r: type=%r, file=%r, filters=%r>' % (
			self.__class__.__name__, self.type, self.file, self.filters
		)

class ProcBase:
	def __init__(self, config):
		self.config = config
		
	def __repr__(self):
		"""String representation."""
		return '<%r: config=%r>' % (
			self.__class__.__name__, self.config
		)
	
	def run(self, options, args):
		pass
		
	def delete_files(self, items):
		for item in items:
			if(item.name and os.path.isfile(item.name)):
				os.remove(item.name)
