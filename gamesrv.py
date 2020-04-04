import os, bubbob, hashlib

BB_DIR = os.path.dirname(bubbob.__file__)


class Game:
    width     = 640
    height    = 480
    backcolor = 0x000000

    FnDesc    = "NoName"
    FnFrame   = lambda self: 1.0
    FnExcHandler=lambda self, k: 0
    FnServerInfo=lambda self, s: None
    FnPlayers = lambda self: {}
    FnKeys    = []
    FnUnknown = lambda self: None
    FnDisconnected = lambda self: None
    FnChangeLevels = None

    def __init__(self):
        global game      # :-/
        game = self
        self._time_delta = 0.0

    def openserver(self):
        pass

    def mainstep(self):
        self._time_delta += 0.025
        iterations = 0
        while self._time_delta > 0.0:
            self._time_delta -= self.FnFrame()
            iterations += 1
        return iterations

    def cheat(self, bonusname):
        import bubbob.bonuses
        cheat = bubbob.bonuses.__dict__['__cheat']
        cheat(bonusname)

    def FnExtraDesc(self):
        players = 0
        for player in self.FnPlayers().values():
            if player.isplaying():
                players += 1
        if players == 0:
            return 'no players'
        elif players == 1:
            return 'one player'
        else:
            return '%d players' % players


class Player:
    standardplayericon = None

    def playerjoin(self):
        pass

    def playerleaves(self):
        pass

    def _playerleaves(self):
        if self.isplaying():
            client = self._client
            del self._client
            client.gs_killplayer(self)
        self.playerleaves()

    def isplaying(self):
        return hasattr(self, "_client")

# ____________________________________________________________

clients = []

# ____________________________________________________________

sprites = ['']
sprites_by_n = {}

def clearsprites():
    sprites_by_n.clear()
    sprites[:] = ['']

def compactsprites(insert_new=None, insert_before=None):
    global sprites, sprites_by_n
    if insert_before is not None:
        if insert_new.alive:
            insert_before = insert_before.alive
        else:
            insert_before = None
    newsprites = ['']
    newd = {}
    l = sprites_by_n.items()
    l.sort()
    for n, s in l:
        if n == insert_before:
            prevn = insert_new.alive
            newn = insert_new.alive = len(newsprites)
            newsprites.append(sprites[prevn])
            newd[newn] = insert_new
            l.remove((prevn, insert_new))
        newn = s.alive = len(newsprites)
        newsprites.append(sprites[n])
        newd[newn] = s
    sprites = newsprites
    sprites_by_n = newd

def _pack_msg(x, y, icocode):
    # Encode x, y and icocode into one unicode character each.
    # For x and y, use values in the range 1 to 2001.  After
    # being encoded as utf-8 for transport over a websocket,
    # it is guaranteed to turn into (at most) 2 bytes.
    if x < -700: x = -700
    if y < -700: y = -700
    if x > 1300: x = 1300
    if y > 1300: y = 1300
    return unichr(x + 701) + unichr(y + 701) + unichr(icocode)

def _unpack_msg(msg):
    return ord(msg[0]), ord(msg[1]), ord(msg[2])


class Sprite:
    def __init__(self, ico, x, y):
        self.x = x
        self.y = y
        self.ico = ico
        self.alive = len(sprites)
        if (-ico.w < x < game.width and
            -ico.h < y < game.height):
            sprites.append(_pack_msg(self.x, self.y, self.ico.code))
        else:
            sprites.append('')  # starts off-screen
        sprites_by_n[self.alive] = self

    def move(self, x,y, ico=None):
        self.x = x
        self.y = y
        if ico is not None:
            self.ico = ico
        sprites[self.alive] = _pack_msg(x, y, self.ico.code)

    def setdisplaypos(self, x, y):
        # special use only (self.x,y are not updated)
        s = sprites[self.alive]
        if s:
            _, _, ocode = _unpack_msg(s)
            sprites[self.alive] = _pack_msg(x, y, ocode)

    def setdisplayicon(self, ico):
        # special use only (self.ico is not updated)
        s = sprites[self.alive]
        if s:
            ox, oy, _ = _unpack_msg(s)
            sprites[self.alive] = _pack_msg(ox, oy, ico.code)

    def getdisplaypos(self):
        # special use only (normally, read self.x,y,ico directly)
        s = sprites[self.alive]
        if self.alive and s:
            ox, oy, _ = _unpack_msg(s)
            return ox, oy
        else:
            return None, None

    def step(self, dx,dy):
        self.x = self.x + dx
        self.y = self.y + dy
        sprites[self.alive] = _pack_msg(self.x, self.y, self.ico.code)

    def seticon(self, ico):
        self.ico = ico
        sprites[self.alive] = _pack_msg(self.x, self.y, ico.code)

    def hide(self):
        sprites[self.alive] = ''

    def kill(self):
        if self.alive:
            del sprites_by_n[self.alive]
            sprites[self.alive] = ''
            self.alive = 0

    def prefix(self, n, m=0):
        pass

    def to_front(self):
        if self.alive and self.alive < len(sprites)-1:
            self._force_to_front()

    def _force_to_front(self):
        info = sprites[self.alive]
        sprites[self.alive] = ''
        del sprites_by_n[self.alive]
        self.alive = len(sprites)
        sprites_by_n[self.alive] = self
        sprites.append(info)

    def to_back(self, limit=None):
        assert self is not limit
        if limit:
            n1 = limit.alive + 1
        else:
            n1 = 1
        if self.alive > n1:
            if n1 in sprites_by_n:
                keys = sprites_by_n.keys()
                keys.remove(self.alive)
                keys.sort()
                keys = keys[keys.index(n1):]
                reinsert = [sprites_by_n[n] for n in keys]
                for s1 in reinsert:
                    s1._force_to_front()
                assert n1 not in sprites_by_n
            info = sprites[self.alive]
            sprites[self.alive] = ''
            del sprites_by_n[self.alive]
            self.alive = n1
            sprites_by_n[n1] = self
            sprites[n1] = info

    def __repr__(self):
        if self.alive:
            return "<sprite %d at %d,%d>" % (self.alive, self.x, self.y)
        else:
            return "<killed sprite>"

# ____________________________________________________________


class DataChunk:
    def send_definition_to_clients(self, msgdef):
        self._msgdef = msgdef
        for c in clients:
            c.gs_send_definition(self)

    def read(self, slice=None):
        f = open(os.path.join('bubbob', self.filename), "rb")
        data = f.read()
        f.close()
        if slice:
            start, length = slice
            data = data[start:start+length]
        return data


class Bitmap(DataChunk):
    def __init__(self, filename, colorkey=None):
        self.filename = filename
        self.icons = {}
        self.colorkey = colorkey

    def geticon(self, x, y, w, h, alpha=255):
        rect = (x, y, w, h)
        try:
            return self.icons[rect]
        except KeyError:
            ico = Icon(self, Icon.count, x, y, w, h, alpha)
            Icon.count += 1
            self.icons[rect] = ico
            return ico

    def geticonlist(self, w, h, count):
        return map(lambda i, fn=self.geticon, w=w, h=h: fn(i*w, 0, w, h),
                   range(count))


class MemoryBitmap(Bitmap):
    def __init__(self, data, colorkey=None):
        self.data = data
        Bitmap.__init__(self, hashlib.md5(data).hexdigest(), colorkey)

    def read(self, slice=None):
        data = self.data
        if slice:
            start, length = slice
            data = data[start:start+length]
        return data


class Icon(DataChunk):
    count = 1

    def __init__(self, bitmap, code, x, y, w, h, alpha=255):
        self.w = w
        self.h = h
        self.origin = (bitmap, x, y)
        self.code = code
        self.alpha = alpha
        self.filename = bitmap.filename
        self.send_definition_to_clients('ico`%%s`%d`%d`%d`%d`%d' % (
            code, x, y, w, h))

    def getimage(self):
        from bubbob import pixmap
        bitmap, x, y = self.origin
        image = pixmap.decodepixmap(bitmap.read())
        return pixmap.cropimage(image, (x, y, self.w, self.h))

    def getorigin(self):
        bitmap, x, y = self.origin
        return bitmap, (x, y, self.w, self.h)


class Sample:
    def __init__(self, code, filename, freqfactor=1):
        self.code = code
        self.filename = filename
        self.freqfactor = freqfactor

    def play(self, lvolume=1.0, rvolume=None, pad=0.5, singleclient=None):
        # XXX volume control
        if singleclient is None:
            clist = clients[:]
        else:
            clist = [singleclient]
        for c in clist:
            c.gs_play_sound(self.filename)


class Music:
    def __init__(self, filename, filerate=44100):
        self.filename = filename
        self.filerate = filerate


# ____________________________________________________________

bitmaps = {}
samples = {}
currentmusics = [0]

def getbitmap(filename, colorkey=None):
    try:
        return bitmaps[filename]
    except KeyError:
        fullfilename = os.path.join(BB_DIR, filename)
        bmp = Bitmap(filename, colorkey)
        bitmaps[filename] = bmp
        return bmp

def newbitmap(data, colorkey=None):
    bmp = MemoryBitmap(data, colorkey)
    bitmaps['dynamic', bmp.filename] = bmp
    return bmp

def getsample(filename, freqfactor=1):
    try:
        return samples[filename, freqfactor]
    except KeyError:
        snd = Sample(len(samples), filename, freqfactor)
        samples[filename, freqfactor] = snd
        return snd

def getmusic(filename, filerate=44100):
    try:
        return samples[filename]
    except KeyError:
        mus = Music(filename, filerate)
        samples[filename] = mus
        #music_by_id[mus.fileid] = mus
        return mus

def has_loop_music():
    return currentmusics[0] < len(currentmusics)-1

def finalsegment(music1, music2):
    intro1 = music1[1:1+music1[0]]
    intro2 = music2[1:1+music2[0]]
    loop1 = music1[1+music1[0]:]
    loop2 = music2[1+music2[0]:]
    return loop1 == loop2 and intro1 == intro2[len(intro2)-len(intro1):]

def set_musics(musics_intro, musics_loop, reset=1):
    mlist = []
    loop_from = len(musics_intro)
    mlist.append(loop_from)
    for m in musics_intro + musics_loop:
        mlist.append(m)
    reset = reset or not finalsegment(mlist, currentmusics)
    currentmusics[:] = mlist
    if reset:
        for c in clients:
            c.gs_start_music()

def fadeout(time=1.0):
    # XXX
    print "fadeout: not implemented"
