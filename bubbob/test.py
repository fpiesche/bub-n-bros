import os, sys
LOCALDIR = sys.argv[0]
LOCALDIR = os.path.dirname(os.path.abspath(LOCALDIR))

sys.path.append(os.path.join(os.path.dirname(LOCALDIR), 'common'))
sys.path.append(LOCALDIR)
import gamesrv

import images, boards
gamesrv.game = gamesrv.Game()
gamesrv.game.levelfile = 'levels/Arena.bin'
gamesrv.game.extralife = 5
gamesrv.game.limitlives = 5
boards.loadmodules()

import player, bonuses, bubbles, monsters


import posixpath as ospath

def dump():
    fn = {}
    for filename, rect in images.sprmap.values():
        fn[filename] = True
    fn = fn.keys()
    fn.sort()
    for filename in fn:
        path = []
        while filename:
            filename, component = ospath.split(filename)
            assert component, "invalid file path"
            path.insert(0, component)
        print path

import ext5, ext2, ext7, ext6, ext1, ext4, ext3

dump()
