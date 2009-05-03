# -*- coding: utf-8 -*-

import sys, codecs, os, os.path

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
    
    def write(self, line, prefix = u'[WRITE]: '):
        if self.writable:
            sys.stdout.write((prefix + line).encode(self.syscharset))
            sys.stdout.write('\n')
            if self.logging:
                self.log.append(prefix + line)
                self.log.append('\n')
    
    def writeerr(self, line, prefix = u'[ERROR]: '):
        if self.writable:
            sys.stderr.write((prefix + line).encode(self.syscharset))
            sys.stderr.write('\n')
            if self.logging:
                self.log.append(prefix + line)
                self.log.append('\n')
    
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
            
            if self.current is not None:
                os.chdir(self.current.encode(self.syscharset))
            
            if self.logging:
                (ip, op) = os.popen4(line.encode(self.syscharset))
                ip.close()
                
                for line in op:
                    self.write(line.decode(self.syscharset))
                
                ret = op.close()
            else:
                ret = os.system(line.encode(self.syscharset))
            
            if self.current is not None:
                os.chdir(cwd)
            
            if len(self.paths)>0:
                os.environ['path'] = orig_path
            return ret
        else:
            return -1
