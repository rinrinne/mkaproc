# -*- coding: utf-8 -*-

import sys, codecs, os, os.path

from subprocess import *

class Console:
    def __init__(self, charset = 'iso8859-1'):
        self.writable = False
        self.executable = True
        self.logging = False
        self.syscharset = charset
        self.paths = []
        self.current = None
        self.log = []
    
    def __repr__(self):
        """String representation."""
        return '<%r: writable=%r, executable=%r, logging=%r, syscharset=%r, paths=%r, current=%r, log=%r>' % (
            self.__class__.__name__, self.writable, self.executable, self.logging, self.syscharset, self.paths, self.current, self.log
        )
    
    def root(self, current):
        if not os.path.isdir(current):
            os.mkdir(current)
        self.current = current
    
    def write(self, line, prefix = u'[WRITE]: ', fd=None):
        if self.writable:
            if fd is not None:
                out = sys.stdout
            else:
                out = fd
            out.write((prefix + line).encode(self.syscharset))
            out.write('\n')
        
        if self.logging:
            self.log.append(prefix + line)
            self.log.append('\n')
    
    def writeerr(self, line, prefix = u'[ERROR]: '):
        self.write(line, prefix, sys.stderr)
    
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
        self.writeerr(line, u'[EXEC]: ')
        if self.executable:
            if len(self.paths)>0:
                orig_path = os.environ['path']
                pathlist = []
                for path in self.paths:
                    pathlist += path
                os.environ['path'] = os.pathsep.join(map(lambda x: x.encode(self.syscharset), pathlist) + [orig_path])
            
            if self.logging:
                proc = Popen(line.encode(self.syscharset), shell=True, stdout=PIPE, stderr=STDOUT, cwd=self.current)
                
                for line in proc.stdout:
                    self.write(line.decode(self.syscharset))
                
                ret = proc.retcode
            else:
                ret = call(line.encode(self.syscharset), shell=True, cwd=self.current)

            if len(self.paths)>0:
                os.environ['path'] = orig_path
            
            return ret
        else:
            return -1
