# -*- coding: utf-8 -*-

import sys, optparse, codecs, os, os.path, re, glob
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
			targets.append(os.path.normpath(arg.decode(self.config.syscharset)).strip('()[]{}'))
		
		if options.targets:
			try:
				for line in open_textfile(options.targets, 'r', self.config.syscharset):
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
		console = Console.Console(options.syscharset)
		console.writable = self.config.verbose
		console.logging  = self.config.logfile is not None
		
		for target in targets:
			if(not os.path.isfile(target)):
				continue
			
			thumbfile = None
			deletes = []
			[path, name] = os.path.split(target)
			
			os.chdir(path.encode(self.config.syscharset))
			
			# cover
			if(options.coverfile is not None and flt.thumb is not None):
				cont = self.config.getcontents("cover")
				if(len(cont)):
					cover = cont[0].getfilters(u'all')
					if(len(cover)):
						cover = cover[0]
						
						# numbered cover
						covers = [options.coverfile]
						(fname, ext) = os.path.splitext(options.coverfile)
						ncovers = glob.glob(os.path.join(fname + '_*' + ext))
						for ncover in ncovers:
							covers.append(ncover.decode(self.config.syscharset))
						
						for coverfile in covers:
							if os.path.isfile(coverfile.encode(self.config.syscharset)):
								coverfile = os.path.basename(coverfile)
								thumbfile = cover.format % coverfile
								option = cover.option
								option = option.replace(u'__COVER__', coverfile)
								option = option.replace(u'__THUMB__', thumbfile)
								
								console.appendpath(cover.path)
								cmd = [cover.command, option]
								console.execute(cmd)
								console.poppath()
								
								obj = Matroska.Item()
								obj.name = thumbfile
								deletes.append(obj)
			
			# cuesheet
			console.appendpath(flt.path)
			
			option = flt.option.replace(u'__DESTROOT__', flt.destroot)
			cmd = [flt.command, option]
			if(thumbfile is not None):
				thumb = flt.thumb.replace(u'__THUMB__', thumbfile)
				cmd.append(thumb)
			cmd.append(u'"%s"' % name)
			
			console.execute(cmd)
			console.poppath()
			
			# delete extract file
			self.delete_files(deletes)
