# -*- coding: utf-8 -*-

import sys, codecs, os, os.path

class Console:
    def __init__(self, charset = 'iso8859-1'):
        self.writable = False
        self.executable = True
        self.syscharset = charset
        self.paths = []
        self.current = None
    
    def root(self, current):
        unless os.path.isdir(current):
            os.mkdir(current)
        self.current = current
    
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
        cwd = os.getcwd()
        line = ' '.join(cmd)
        if self.writable:
            sys.stderr.write('[EXEC]: ' + line)
            sys.stderr.write('\n')
        if self.executable:
            if len(self.paths)>0:
                orig_path = os.environ['path']
                pathlist = []
                for path in self.paths:
                    pathlist += path.encode(self.syscharset)
                os.environ['path'] = os.pathsep.join(pathlist + [orig_path])
            
            if self.current is not None:
                os.chdir(self.current.encode(self.syscharset))
            
            ret = os.system(line.encode(self.syscharset))
            
            if self.current is not None:
                os.chdir(cwd)
            
            if len(self.paths)>0:
                os.environ['path'] = orig_path
            return ret
        else:
            return -1
