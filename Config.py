# -*- coding: utf-8 -*-

import os, os.path, sys, string, re
import xml.etree.ElementTree as ET
import Matroska

PATH_TOOL  = u'mkvtoolnix/path'
ROOT_WORK  = u'workroot'

MSG_NOELEMENT   = u'element not found'
MSG_NOELEMTEXT  = u'element text not found'
MSG_NODIRECTORY = u'directory not found'


class ConfigParseError(Exception):
	def __init__(self, msg, file, path):
		self.path = path
		self.filename = file
		self.msg = msg
		
	def __str__(self):
		return "%s[%s] %s: %s" % (self.__class__.__name__, self.path, self.msg, self.filename)


class Filter:
	def __init__(self):
		self.type = None
		self.path = []
		self.command = None
		self.option = None
		self.format = "s_%s"
		self.thumb = None
		self.destroot = None

	def __repr__(self):
		"""String representation."""
		return '<%r: type=%r, command=%r, option=%r, format=%r, thumb=%r, destroot=%r>' % (
			self.__class__.__name__, self.type, self.command, self.option, self.format, self.thumb, self.destroot
		)

class Content:
	def __init__(self):
		self.type = None
		self.name = None
		self.desc = None
		self.filters = []

	def __repr__(self):
		"""String representation."""
		return '<%r: type=%r, name=%r, desc=%r, filters=%r>' % (
			self.__class__.__name__, self.type, self.name, self.desc, self.filters
		)
	
	def getfilters(self, type=None):
		if type == None:
			return []
		
		result = []
		for flt in self.filters:
			if type == "all":
				result.append(flt)
			else:
				if flt.type == type:
					result.append(flt)
		return result

class Config(Matroska.Config):
	def __init__(self, file=None):
		self.contents = []
		self.workroot = None
		self.o_destroot = None
		self.verbose  = False
		
		if file:
			self.load(file)
	
	def __repr__(self):
		"""String representation."""
		return '<%r: workroot=%r, o_destroot=%r, verbose=%r, contents=%r>' % (
			self.__class__.__name__, self.workroot, self.o_destroot, self.verbose, self.contents
		)
	
	def load(self, conffile):
		dom = ET.ElementTree(file=conffile)
		if dom == None:
			raise ConfigParseError(u'XML tree not found', conffile, u'')
		
		# workroot
		elem = dom.find(ROOT_WORK)
		if elem != None:
			text = elem.text
			if text:
				text = os.path.abspath(text)
				if os.path.isdir(text):
					self.workroot = text + os.sep
		
		# mkvtoolnix
		elem = dom.find(PATH_TOOL)
		
		## mkvtoolnix
		if elem != None:
			text = elem.text
			if text:
				text = os.path.abspath(text)
				if os.path.isdir(text):
					self.toolpath = text + os.sep
				else:
					raise ConfigParseError(MSG_NODIRECTORY, conffile, PATH_TOOL)
			else:
				self.toolpath = ""
		else:
			raise ConfigParseError(MSG_NOELEMENT, conffile, PATH_TOOL)
		
		## Contents
		mkvroot = dom.find(u'matroska')
		
		if mkvroot == None:
			raise ConfigParseError(MSG_NOELEMENT, conffile, u'matroska')
		
		for elem in mkvroot:
			content = self.__createContent(elem)
			if content:
				self.contents.append(content)
	
	def __createFilter(self, root):
		flt = Filter()
		flt.type = root.get(u'type')
		for elem in root:
			if elem.tag == u'path':
				flt.path.append(os.path.abspath(elem.text))
			if elem.tag == u'command':
				flt.command  = elem.text
			if elem.tag == u'option':
				flt.option   = elem.text
			if elem.tag == u'format':
				flt.format   = elem.text
			if elem.tag == u'thumb':
				flt.thumb    = elem.text
			if elem.tag == u'destroot':
				flt.destroot = elem.text
		
		if self.o_destroot is not None:
			flt.destroot = self.o_destroot
		
		if not flt.command:
			return None
		else:
			return flt
	
	def __createContent(self, root):
		cntnt = Content()
		cntnt.type  = root.tag
		cntnt.name = root.get(u'name')
		cntnt.desc = root.get(u'description')
		
		for elem in root:
			flt = self.__createFilter(elem)
			if flt:
				cntnt.filters.append(flt)
		return cntnt
	
	def getcontents(self, type=None):
		if type:
			result = []
			for content in self.contents:
				if content.type == type:
					result.append(content)
			return result
		else:
			return self.contents
	
	def findcontents(self, name, desc):
		result = []
		for content in self.contents:
			if content.name == None or content.name == name:
				if content.desc == None or desc in content.desc:
					result.append(content)
		return result

if __name__ == '__main__':
    exit()
