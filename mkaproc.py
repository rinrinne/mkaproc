#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, optparse, codecs, os, os.path, re
import xml.etree.ElementTree as ET
import Matroska
import Config
import Console

from textfile import *

VERSION = '1.0'

def delete_files(items):
	for item in items:
		if(item.name and os.path.isfile(item.name)):
			os.remove(item.name)

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


if __name__ == '__main__':
	# Define a command-line option parser.
	parser = optparse.OptionParser(
		usage="%prog [options] <target> [<target2> ...]\n"
		"Execute a job for each matroska files.",
		version="MkaProc %s" % VERSION
		)
	parser.add_option(
		"-c", "--output",
		action="store", type="string", dest="output",
		default=None,
		help="Specify a output file format. The default value for this option is '%default'."
		)
	parser.add_option(
		"--target",
		action="store", type="string", dest="targets",
		default=None,
		help="Specify a text file describing the list of target filenames. Useful for converting a number of Matroska Audio files at a time with a list file generated by --find option."
		)
	parser.add_option(
		"-W", "--syscharset",
		action="store", type="string", dest="syscharset",
		default="mbcs",
		help="Specify a charset for the current operating system. The default value for this option is '%default'."
		)
	parser.add_option(
		"-w", "--atcharset",
		action="store", type="string", dest="atcharset",
		default="utf-8",
		help="Specify a charset for the attached text(s). The default value for this option is '%default'."
		)
	parser.add_option(
		"-f", "--config",
		action="store", type="string", dest="configfile",
		default="config.xml",
		help="Specify a cofiguration file. The default value for this option is '%default'."
		)
	parser.add_option(
		"-e", "--extractonly",
		action="store_true", dest="extractonly", default=False,
		help="Extract only."
		)

	# Parse command-line arguments.
	(options, args) = parser.parse_args()
	
	# codec check
	try:
		charset = codecs.lookup(options.syscharset)
	except LookupError, e:
		options.syscharset = sys.getdefaultencoding()		

	try:
		charset = codecs.lookup(options.atcharset)
	except LookupError, e:
		options.atcharset = sys.getdefaultencoding()		

	# Wrap IO streams.
	sys.stdout = codecs.getwriter(options.syscharset)(sys.stdout)
	sys.stderr = codecs.getwriter(options.syscharset)(sys.stderr)
	
	try:
		config = Config.Config(options.configfile)
	except Exception, e:
		sys.stderr.write(str(e) + "\n")
		sys.exit(1)
	
	config.syscharset = options.syscharset
	mka = Matroska.Matroska(config)
	


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
		sys.exit(1)

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
			conts = config.findcontents(attach.name, attach.desc)
			if conts:
				for cont in conts:
					
					# Cover Image
					if(cont.type == "cover" and attach.extracted):
						filters = cont.getfilters(u'all')
						if len(filters) > 0:
							convert = Convert()
							convert.type = cont.type
							convert.name = attach.name
							convert.filters = filters
							items.append(convert)
					
					# CUE Sheet
					if(cont.type == "cuesheet" and attach.extracted):
						filters = cont.getfilters(options.output)
						if len(filters) > 0:
							convert = Convert()
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
					console = Console.Console(options.syscharset)
					console.add_path(flt.path)
					thumbfile = flt.format % item.name
					option = flt.option
					option = option.replace(u'__COVER__', item.name)
					option = option.replace(u'__THUMB__', thumbfile)
					
					cmd = [flt.command, option]
					console.execute(cmd)
					
					obj = Matroska.Item()
					obj.name = thumbfile
					deletes.append(obj)
			
			# cuesheet convert
			for sheet in sheets:
				flt = sheet.filters[0]
				console = Console.Console(options.syscharset)
				console.add_path(flt.path)
				
				cmd = [flt.command, flt.option]
				if flt.thumb:
					thumb = flt.thumb.replace(u'__THUMB__', thumbfile)
					cmd.append(thumb)
				cmd.append(sheet.name)
				
				console.execute(cmd)

			# delete extract file
			delete_files(atts)
			delete_files(trks)
			delete_files(deletes)
