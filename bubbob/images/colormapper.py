import cStringIO

def decodepixmap(data):
    f = cStringIO.StringIO(data)
    sig = f.readline().strip()
    assert sig == "P6"
    while 1:
        line = f.readline().strip()
        if not line.startswith('#'):
            break
    wh = line.split()
    w, h = map(int, wh)
    sig = f.readline().strip()
    assert sig == "255"
    data = f.read()
    f.close()
    return w, h, data

def encodepixmap(w, h, data):
    return 'P6\n%d %d\n255\n%s' % (w, h, data)


INPUT = 'fish_0.ppm'
OUTPUT = 'fish_1.ppm'

COLORMAP = {
    '\x00\x99\x00': '\x00\x66\xFF',
    '\x00\xCC\x00': '\x66\xCC\xFF',
    '\x33\xCC\x00': '\x33\x99\xFF',
    '\x00\xBB\x00': '\x33\x99\xFF',
    '\x00\xAA\x00': '\x33\x99\xFF',
    '\x00\x88\x00': '\x00\x66\xFF',

    '\xFF\xFF\x00': '\xCC\xCC\xFF',
    '\xFF\xCC\x33': '\xCC\x99\xFF',
    '\xFF\xCC\x00': '\xCC\x99\xFF',
    '\xFF\x99\x00': '\xCC\x66\xFF',
    '\xFF\x66\x00': '\x99\x66\xFF',
    }


w, h, data = decodepixmap(open(INPUT, 'rb').read())

res = []
for i in range(0, len(data), 3):
    x = data[i:i+3]
    res.append(COLORMAP.get(x, x))

open(OUTPUT, 'wb').write(encodepixmap(w, h, ''.join(res)))
