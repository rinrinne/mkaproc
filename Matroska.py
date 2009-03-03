# -*- coding: utf-8 -*-

import os, os.path, sys, string, re
import xml.etree.ElementTree as ET
	
INFOCMD    = u'mkvinfo'
EXTRACTCMD = u'mkvextract'

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

if __name__ == '__main__':
	exit()
