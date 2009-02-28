# -*- coding: utf-8 -*-

import os, os.path, sys, string, re
import xml.etree.ElementTree as ET

INFOCMD    = u'mkvinfo'
EXTRACTCMD = u'mkvextract'

PATH_TOOL  = u'mkvtoolnix/path'

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
		self.command = None
		self.option = None
		self.format = "s_%s"
		self.thumb = False

	def __repr__(self):
		"""String representation."""
		return '<%r: type=%r, command=%r, option=%r, format=%r, thumb=%r>' % (
			self.__class__.__name__, self.type, self.command, self.option, self.format, self.thumb
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

class Config:
	def __init__(self, file=None):
		self.syscharset = 'iso8859-1'
		self.toolpath = None
		self.contents = []
		
		if file:
			self.load(file)
	
	def __repr__(self):
		"""String representation."""
		return '<%r: syscharset=%r, toolpath=%r, contents=%r>' % (
			self.__class__.__name__, self.syscharset, self.toolpath, self.contents
		)
	
	def load(self, conffile):
		dom = ET.ElementTree(file=conffile)
		if dom == None:
			raise ConfigParseError(u'XML tree not found', conffile, u'')
		
		# mkvtoolnix
		elem = dom.find(PATH_TOOL)
		
		## mkvtoolnix
		if elem != None:
			text = elem.text
			if text:
				text = os.path.normpath(text)
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
			if elem.tag == u'command':
				flt.command = elem.text
			if elem.tag == u'option':
				flt.option  = elem.text
			if elem.tag == u'format':
				flt.format  = elem.text
			if elem.tag == u'thumb':
				flt.thumb   = True
		
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
	
class Item:
	def __init__(self):
		self.number = 0
		self.id = 0
		self.type = None
		self.name = None
		self.extracted = False

class Track(Item):
	def __init__(self):
		Item.__init__(self)
		self.codec = None

class AudioTrack(Track):
	def __init__(self):
		Track.__init__(self)
		self.freq = 0
		self.channel = 0
		self.bitdepth = 0
	
	def __repr__(self):
		"""String representation."""
		return '<%r: number=%r, id=%r, type=%r, name=%r, extracted=%r, codec=%r, freq=%r, channel=%r, bitdepth=%r>' % (
			self.__class__.__name__, self.number, self.id, self.type, self.name, self.extracted, self.codec, self.freq, self.channel, self.bitdepth
		)


class VideoTrack(Track):
	def __init__(self):
		Track.__init__(self)

class Attachment(Item):
	def __init__(self):
		Item.__init__(self)
		self.desc = ''
	
	def __repr__(self):
		"""String representation."""
		return '<%r: number=%r, id=%r, type=%r, name=%r, extracted=%r, desc=%r>' % (
			self.__class__.__name__, self.number, self.id, self.type, self.name, self.extracted, self.desc
		)
	
class Matroska:
	def __init__(self, conf):
		self.config = conf
		self.dom = None
		self.name = None
	
	def __repr__(self):
		"""String representation."""
		return '<%r: config=%r, dom=%r, name=%r>' % (
			self.__class__.__name__, self.config, self.dom, self.name
		)
	def load(self, file):
		infocmd = os.path.normpath(self.config.toolpath + INFOCMD)
		infoopt = ""
		cmd = [infocmd, infoopt]
		cmd.append("\"%s\"" % file)
		self.dom = self.__parseebml(os.popen(" ".join(cmd).encode(self.config.syscharset), "r"))
		self.name = file
	
	def __parseebml(self,fd):
		
		prev_depth = 0
		stack = []
		
		root = ET.Element(u'ebml')
		current = root
		prevelem = None
		
		for line in fd:
			depth = line.index("+")
			str = re.sub(r'\(.*?\)', '', line[depth+2:]).strip().split(u',', 1)[0]
			
			item = str.split(u':', 2)
			item[0] = item[0].strip().lower().replace(u' ', '')
			
			elem = ET.Element(item[0])
			if len(item) != 1:
				elem.text = item[1].strip()
			
			if depth > prev_depth:
				stack.append(current)
				current = prevelem
			
			elif depth < prev_depth:
				for i in range(prev_depth-depth):
					current = stack.pop()
			
			current.append(elem)
			prevelem = elem
			
			prev_depth = depth
			
		if len(root.getchildren()) == 0:
			return None
		else:
			return ET.ElementTree(root)
		
		
	def attachments(self):
		attachs = []
		attachroot = self.dom.find('segment/attachments')
		
		if attachroot is not None:
			for cnt, elem in enumerate(attachroot.findall('attached')):
				attach = Attachment()
				attach.number	= cnt+1
				attach.name		= elem.find('filename').text
				attach.type		= elem.find('mimetype').text
				attach.id		= elem.find('fileuid').text
				attach.desc		= elem.find('filedescription').text
				attachs.append(attach)
			
		return attachs


	def tracks(self):
		trks = []
		trkroot = self.dom.find('segment/segmenttracks')
		
		for elem in trkroot.findall('atrack'):
			if 'audio' in elem.findtext('tracktype', ''):
				track = AudioTrack()
			else:
				continue
			
			track.number	= elem.find('tracknumber').text
			track.id		= elem.find('trackuid').text
			track.type		= elem.find('tracktype').text
			track.codec		= elem.find('codecid').text
			
#			if 'audio' in elem.find('tracktype').text:
			if isinstance(track, AudioTrack):
				subelem = elem.find('audiotrack')
				if subelem is not None:
					track.freq		= subelem.find('samplingfrequency').text
					track.channel	= subelem.find('channels').text
					track.bitdepth	= subelem.find('bitdepth').text
			
			
			trks.append(track)
		
		return trks
	
	def extract(self, items):
		tracks = []
		attachs = []
		returns = []
		extcmd = os.path.normpath(self.config.toolpath + EXTRACTCMD)
		extopt = ""
		
		for item in items:
			if item.name is not None:
				if 'Track' in item.__class__.__bases__[0].__name__:
					if item.number is not None:
						tracks.append(item)
				
				elif 'Attachment' in item.__class__.__name__:
					if item.id is not None:
						attachs.append(item)
				
				else:
					pass
		
		if len(tracks) > 0:
			cmd = [extcmd, extopt,]
			cmd.append('tracks')
			cmd.append("\"%s\"" % self.name)
			for track in tracks:
				cmd.append(" %s:\"%s\"" % (track.number, track.name))
			
			ret = os.system(" ".join(cmd).encode(self.config.syscharset))
			returns.append((ret, tracks))
			
			
		if len(attachs) > 0:
			cmd = [extcmd, extopt,]
			cmd.append('attachments')
			cmd.append("\"%s\"" % self.name)
			for attach in attachs:
#				cmd.append("%s:\"%s\"" % (attach.id, attach.name))
				cmd.append("%s:\"%s\"" % (attach.number, attach.name))
			
			ret = os.system(" ".join(cmd).encode(self.config.syscharset))
			returns.append((ret, attachs))
			
		# Check extract file exist?
		for item in items:
			if os.path.isfile(item.name.encode(self.config.syscharset)):
				item.extracted = True
		
		# command result check
		for ret in returns:
			(errno, lists) = ret
			if errno != 0:
				for item in lists:
					item.extracted = False