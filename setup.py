#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
	MkaProc setup.

	Copyright (c) 2009 by rin_ne

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA, or visit
http://www.gnu.org/copyleft/gpl.html .
"""

from distutils.core import setup
import py2exe

setup(
	name='mkaproc',
	version='1.0',
	description='Matroska Processor (MkaProc)',
	author='Hahahaha',
	author_email='rin_ne@big.or.jp',
	url='http://www20.big.or.jp/~rin_ne/',
	py_modules=[
		"startup",
		"MkaProc",
		"Matroska",
		"Config",
		"textfile",
		"Console",
		"ProcBase",
		],
	console=['startup.py'],
	options={"py2exe": {"packages": ["encodings"]}},
	)
