#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, optparse, codecs, os.path
import Config
import Console
import MkaProc
import CuesheetProc
import MatroskaProc

from textfile import *

VERSION = '1.0'

if __name__ == '__main__':
	# Define a command-line option parser.
	parser = optparse.OptionParser(
		usage="%prog [options] <target> [<target2> ...]\n"
		"Execute a job for each matroska files.",
		version="MkaProc %s" % VERSION
		)
	parser.add_option(
		"-f", "--filter",
		action="store", type="string", dest="filter",
		default=None,
		help="Specify a filter for cuesheet. The default value for this option is '%default'."
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
		"-c", "--config",
		action="store", type="string", dest="configfile",
		default="config.xml",
		help="Specify a cofiguration file. The default value for this option is '%default'."
		)
	parser.add_option(
		"-e", "--extractonly",
		action="store_true", dest="extractonly", default=False,
		help="Extract only."
		)
	parser.add_option(
		"--cuesheetmode",
		action="store_true", dest="cuesheetmode", default=False,
		help="Cuesheet mode."
		)
	parser.add_option(
		"--cover",
		action="store", type="string", dest="coverfile",
		default=None,
		help="Specified cover image file. the default value for thes option is '%default'."
		)
	parser.add_option(
		"-t", "--workroot",
		action="store", type="string", dest="workroot",
		default=None,
		help="Specified working root directory. this option is ignored when specified with --cuesheetmode option. the default value for thes option is '%default'."
		)
	parser.add_option(
		"-d", "--destroot",
		action="store", type="string", dest="destroot",
		default=None,
		help="Specified destination root directory. the default value for thes option is '%default'."
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
	
	if options.workroot is not None:
		config.workroot = os.path.abspath(options.workroot.decode(options.syscharset))
	
	if options.destroot is not None:
		config.o_destroot = os.path.abspath(options.destroot.decode(options.syscharset))
	
	mode = None
	if options.cuesheetmode:
		config.workroot = None
		mode = CuesheetProc.CuesheetProc(config)
	else:
		mode = MatroskaProc.MatroskaProc(config)
	
	mode.run(options, args)
	
