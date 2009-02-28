# -*- coding: utf-8 -*-

import os, codecs

def open_textfile(filename, mode='r', encoding = 'utf-8'):
	hasBOM = False
	if os.path.isfile(filename):
		f = open(filename,'rb')
		header = f.read(4)
		f.close()
		
		# Don't change this to a map, because it is ordered
		encodings = [ ( codecs.BOM_UTF32, 'utf-32' ),
			( codecs.BOM_UTF16, 'utf-16' ),
			( codecs.BOM_UTF8, 'utf-8' ) ]
		
		for h, e in encodings:
			if header.startswith(h):
				encoding = e
				hasBOM = True
				break
		
	f = codecs.open(filename,mode,encoding)
	# Eat the byte order mark
	if hasBOM:
		f.read(1)
	return f
