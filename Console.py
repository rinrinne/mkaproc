# -*- coding: utf-8 -*-

import sys, codecs, os

class Console:
    def __init__(self, charset = 'iso8859-1'):
        self.writable = False
        self.executable = True
        self.syscharset = charset
        self.paths = []
    
    def write(self, line):
        if self.writable:
            sys.stdout.write('[WRITE]: ' + line)
            sys.stdout.write('\n')
    
    def appendpath(self, path):
        if isinstance(path, str):
            self.paths.append([path])
        elif isinstance(path, list):
            self.paths.append(path)
    
    def poppath(self, depth=0):
        ret = []
        if(depth==0):
            ret = self.paths
            self.paths = []
        else:
            for i in range(depth):
                ret.append(self.paths.pop())
        return ret
    
    def execute(self, cmd):
        line = ' '.join(cmd)
        if self.writable:
            sys.stderr.write('[EXEC]: ' + line)
            sys.stderr.write('\n')
        if self.executable:
            if len(self.paths)>0:
                orig_path = os.environ['path']
                pathlist = []
                for path in self.paths:
                    pathlist += path
                os.environ['path'] = os.pathsep.join(pathlist + [orig_path])
            
            ret = os.system(line.encode(self.syscharset))
            
            if len(self.paths)>0:
                os.environ['path'] = orig_path
            return ret
        else:
            return -1
