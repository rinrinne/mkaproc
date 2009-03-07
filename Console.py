# -*- coding: utf-8 -*-

import sys, codecs, os

class Console:
    def __init__(self, charset = 'iso8859-1'):
        self.writable = False
        self.executable = True
        self.syscharset = charset
        self.path = []

    def write(self, line):
        if self.writable:
            sys.stdout.write('[WRITE]: ' + line)
            sys.stdout.write('\n')

    def add_path(self, path):
        if 'str' in path.__class__.__name__:
            self.path.append(path)
        elif 'list' in path.__class__.__name__:
            self.path += path

    def execute(self, cmd):
        line = ' '.join(cmd)
        if self.writable:
            sys.stderr.write('[EXEC]: ' + line)
            sys.stderr.write('\n')
        if self.executable:
            if len(self.path)>0:
                orig_path = os.environ['path']
                os.environ['path'] = os.pathsep.join(self.path + [orig_path])

            ret = os.system(line.encode(self.syscharset))
            
            if len(self.path)>0:
                os.environ['path'] = orig_path
            return ret
        else:
            return -1
