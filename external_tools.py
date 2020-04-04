
def _pnmtopng_convert_ppm_to_png(data, colorkey=None):
    """Disabled version that uses the external 'pnmtopng' tool"""
    import subprocess
    cmdline = ['pnmtopng']
    if colorkey is not None:
        cmdline.append('-transparent')
        cmdline.append('=rgb:%02X/%02X/%02X' % (
            colorkey & 0xFF, (colorkey >> 8) & 0xFF, colorkey >> 16))
    #
    popen = subprocess.Popen(cmdline,
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE)
    popen.stdin.write(data)
    popen.stdin.close()
    result = popen.stdout.read()
    popen.stdout.close()
    exitcode = popen.wait()
    if exitcode != 0:
        raise Exception("pnmtopng: exit code %r" % exitcode)
    return result

def convert_ppm_to_png(data, colorkey=None):
    import png
    import io, array
    f = io.StringIO(data)
    header = f.readline()
    assert header.rstrip() == 'P6'
    width, height = map(int, f.readline().split())
    maxcol = f.readline()
    assert maxcol.rstrip() == '255'
    a = array.array('B')
    a.fromstring(f.read())
    f.close()

    if colorkey is not None:
        colorkey = (colorkey & 0xFF, (colorkey >> 8) & 0xFF, colorkey >> 16)

    w = png.Writer(width, height, transparent=colorkey)
    g = io.BytesIO()
    w.write_array(g, a)
    return g.getvalue()
