# -*- coding: utf-8 -*-

import sys, optparse, codecs, os, os.path, re
import Matroska
import Config
import Console
import ProcBase

from textfile import *

class MatroskaProc(ProcBase.ProcBase):
	def __init__(self, config):
		ProcBase.ProcBase.__init__(self, config)
		
	def run(self, options, args):
		
		mka = Matroska.Matroska(self.config)
		
		# Determine targets.
		targets = []
		for arg in args:
			targets.append(os.path.normpath(arg.decode(options.syscharset)).strip('()[]{}'))
		
		if options.targets:
			try:
				for line in open_textfile(options.targets, 'r', options.syscharset):
					line = line.strip()
					if line.startswith('#'):
						continue
					targets.append(os.path.normpath(line).strip('()[]{}'))
			except Exception, e:
				sys.stderr.write(str(e) + "\n")
		
		if not targets:
			sys.stderr.write("No target specified.")
			return 1
		
		console = Console.Console(options.syscharset)
		if self.config.workroot is not None:
			console.root = self.config.workroot
		
		for target in targets:
			try:
				mka.load(target)
				atts = mka.attachments()
				trks = mka.tracks()
				
				mka.extract(atts)
			except Exception, e:
				sys.stderr.write(str(e) + "\n")
				continue
			
			cnt = 0
			sheets = []
			items = []
			for attach in atts:
				conts = self.config.findcontents(attach.name, attach.desc)
				if conts:
					for cont in conts:
						
						# Cover Image
						if(cont.type == "cover" and attach.extracted):
							filters = cont.getfilters(u'all')
							if len(filters) > 0:
								convert = ProcBase.Convert()
								convert.type = cont.type
								convert.name = attach.name
								convert.filters = filters
								items.append(convert)
						
						# CUE Sheet
						if(cont.type == "cuesheet" and attach.extracted):
							filters = cont.getfilters(options.filter)
							if len(filters) > 0:
								convert = ProcBase.Convert()
								convert.type = cont.type
								convert.name = attach.name
								convert.filters = filters
								sheets.append(convert)
							
							for line in open_textfile(attach.name.encode(options.syscharset), 'r', options.atcharset):
								match = re.search(r'FILE "(.+?)"', line)
								if match is not None:
									if len(trks) > cnt:
										trks[cnt].name = match.group(1)
										cnt += 1
			
			mka.extract(trks)
			
			if not options.extractonly:
				thumbfile = None
				deletes = []
				
				# pre convert
				for item in items:
					if item.type == "cover":
						flt = item.filters[0]
						console.appendpath(flt.path)
						thumbfile = flt.format % item.name
						option = flt.option
						option = option.replace(u'__COVER__', item.name)
						option = option.replace(u'__THUMB__', thumbfile)
						
						cmd = [flt.command, option]
						console.execute(cmd)
						console.poppath()
						
						obj = Matroska.Item()
						obj.name = thumbfile
						deletes.append(obj)
				
				# cuesheet convert
				for sheet in sheets:
					flt = sheet.filters[0]
					if self.config.o_destroot is not None:
						flt.destroot = self.config.o_destroot
					console.appendpath(flt.path)
					
					cmd = [flt.command, flt.option, u'-b "%s"' % flt.destroot]
					if flt.thumb:
						thumb = flt.thumb.replace(u'__THUMB__', thumbfile)
						cmd.append(thumb)
					cmd.append(sheet.name)
					
					console.execute(cmd)
					console.poppath()
					
				# delete extract file
				self.delete_files(atts)
				self.delete_files(trks)
				self.delete_files(deletes)
