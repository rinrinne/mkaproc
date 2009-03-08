# -*- coding: utf-8 -*-

import sys, optparse, codecs, os, os.path, re
import Matroska
import Config
import Console
import ProcBase

from textfile import *

class CuesheetProc(ProcBase.ProcBase):
	def __init__(self, config):
		ProcBase.ProcBase.__init__(self, config)
		
	def run(self, options, args):
		
		# get filter
		cont = self.config.getcontents("cuesheet")[0]
		filters = cont.getfilters(options.filter)
		if(len(filters)==0):
			sys.stderr.write("Specified filter is not found.")
			return 1
		flt = filters[0]
		
		# Suit coverfile
		if(options.coverfile is not None):
			options.coverfile = os.path.basename(options.coverfile)
		
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
		
		# Process target
		for target in targets:
			if(not os.path.isfile(target)):
				continue
			
			thumbfile = None
			deletes = []
			[path, name] = os.path.split(target)
			
			# cover
			if(options.coverfile is not None and flt.thumb is not None):
				cont = self.config.getcontents("cover")
				if(len(cont)):
					cover = cont[0].getfilters(u'all')
					if(len(cover)):
						cover = cover[0]
						console = Console.Console(options.syscharset)
						console.add_path(cover.path)
						thumbfile = os.path.join(path, cover.format % options.coverfile)
						option = cover.option
						option = option.replace(u'__COVER__', os.path.join(path, options.coverfile))
						option = option.replace(u'__THUMB__', thumbfile)
						
						cmd = [cover.command, option]
						console.execute(cmd)
						
						obj = Matroska.Item()
						obj.name = thumbfile
						deletes.append(obj)
			
			# cuesheet
			console = Console.Console(options.syscharset)
			console.add_path(flt.path)
			
			cmd = [flt.command, flt.option]
			if(thumbfile is not None and os.path.isfile(thumbfile)):
				thumb = flt.thumb.replace(u'__THUMB__', thumbfile)
				cmd.append(thumb)
			cmd.append(target)
			
			console.execute(cmd)
			
			# delete extract file
			self.delete_files(deletes)