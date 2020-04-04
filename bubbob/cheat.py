#! /usr/bin/env python

import sys, os

url = 'http://127.0.0.1:8000/?cheat=%s' % sys.argv[1]
g = os.popen('lynx -source %r' % url, 'r')
g.read()
g.close()
