import math
from scipy import misc
import glob
import zlib, struct



def png_pack(png_tag, data):
        chunk_head = png_tag + data
        return (struct.pack("!I", len(data)) +
                chunk_head +
                struct.pack("!I", 0xFFFFFFFF & zlib.crc32(chunk_head)))

def write_png(buf, width, height):
    """ buf: must be bytes or a bytearray in Python3.x,
        a regular string in Python2.x.
    """

    # reverse the vertical line order and add null bytes at the start
    width_byte_4 = width * 4
    raw_data = b''.join(b'\x00' + buf[span:span + width_byte_4]
                        for span in range((height - 1) * width_byte_4, -1, - width_byte_4))

    return b''.join([
        b'\x89PNG\r\n\x1a\n',
        png_pack(b'IHDR', struct.pack("!2I5B", width, height, 8, 6, 0, 0, 0)),
        png_pack(b'IDAT', zlib.compress(raw_data, 9)),
        png_pack(b'IEND', b'')])



def saveAsPNG(array, filename):
    if any([len(row) != len(array[0]) for row in array]):
        raise ValueError, "Array should have elements of equal size"

                                #First row becomes top row of image.
    flat = []; map(flat.extend, reversed(array))
                                 #Big-endian, unsigned 32-byte integer.
    buf = b''.join([struct.pack('>I', ((0xffFFff & i32)<<8)|(i32>>24) )
                    for i32 in flat])   #Rotate from ARGB to RGBA.

    data = write_png(buf, len(array[0]), len(array))
    f = open(filename, 'wb')
    f.write(data)
    f.close()



def arctan(y, x):
    if y >= 0:
        return 2*math.pi-math.atan2(y,x)
    else:
        return 0-math.atan2(y,x) 

# radius = 400
# for r in range(radius):
#     x = [[0xffFFFFFF for i in range(1000)] for j in range(1000)]
#     for i in range(1000):
#         for j in range(1000):
#             dist = (i-500)**2+(j-500)**2
#             if abs((r**2) - dist) <= 400:
#                 x[j][i] = 0xff000000
#     saveAsPNG(x, "frame"+str(r)+".png")

def fracColor(x):
    r,g,b = 0,0,0
    if x <= 1.0/6:
        r = 255
        g = x*255*6
        b = 0
    elif x <= 2.0/6:
        r = (1-6*(x-1.0/6))*255
        g = 255
        b = 0
    elif x <= 3.0/6:
        r = 0
        g = 255
        b = (x-2.0/6)*255*6
    elif x <= 4.0/6:
        r = 0
        g = (1-6*(x-3.0/6))*255
        b = 255
    elif x <= 5.0/6:
        r = (x-4.0/6)*255*6
        g = 0
        b = 255
    else:
        r = 255
        g = 0
        b = (1-6*(x-5.0/6))*255
    r,g,b = int(r), int(g), int(b)
    return 0xff000000+r*256*256+256*g+b





def parameterCurve(f, steps, thickness, startTime, endTime, numFrames): #f: [0,1]x[startTime, endTime] -> ([-500, 500]x[-500, 500])x[startTime, endTime]
    canvas = [[0xffFFFFFF for i in range(1000)] for j in range(1000)]
    t = startTime
    frame = 0
    while t < endTime:
        s = 0
        changes =[]
        while s < 1:
            center = f(s,t)
            offset = f(s+.0005, t)
            dx = offset[0] - center[0]
            dy = offset[1]-center[1]
            if dx**2 + dy**2 != 0:
                dx, dy = dx/((dx**2+dy**2)**.5), dy/((dx**2+dy**2)**.5)
                for q in range(-thickness, thickness):
                    changes.append((int(round(dx*q+center[1]))+500, int(round(-dy*q+center[0]))+500))
                    canvas[changes[-1][0]][changes[-1][1]] = fracColor(s)
            s += 1/float(steps)
        saveAsPNG(canvas, "frame"+str(frame)+".png")
        print "Created frame", frame
        for i in changes:
                canvas[i[0]][i[1]] = 0xffFFFFFF
        frame += 1
        t += (endTime - startTime)/float(numFrames)



def traceCurve(f, numSteps, thickness, numFrames): #f: [0,1] -> ([-500, 500]x[-500, 500])x[startTime, endTime]
    canvas = [[0xffFFFFFF for i in range(1000)] for j in range(1000)]
    numFrames -= 1
    t = 0
    frame = 0
    saveAsPNG(canvas, "frame"+str(frame)+".png")
    print "Created frame", frame
    step = 0
    interval = numSteps/numFrames
    while step <= numSteps:
        center = f(t)
        offset = f(t+.005)
        dx = offset[0] - center[0]
        dy = offset[1]-center[1]
        if dx**2 + dy**2 != 0:
            dx, dy = dx/((dx**2+dy**2)**.5), dy/((dx**2+dy**2)**.5)
            for q in range(-thickness, thickness):
                canvas[int(round(dx*q+center[1]))+500][int(round(-dy*q+center[0]))+500] = fracColor(t)
        if frame*interval == step:
            frame += 1
            saveAsPNG(canvas, "frame"+str(frame)+".png")
            print "Created frame", frame
        step += 1
        t += 1/float(numSteps)
    frame += 1
    saveAsPNG(canvas, "frame"+str(frame)+".png")
    print "Created frame", frame







def circ(t,r):
    return (r*math.cos(2*math.pi*t), r*math.sin(2*math.pi*t))

def sin(t,h):
    return (t*800-400, 100*math.sin(2*math.pi*h/100)*math.sin(8*math.pi*t))

def flower(theta, k):
    return (400*math.cos(2*math.pi*theta)*math.sin(2*math.pi*k*theta), 400*math.sin(2*math.pi*theta)*math.sin(2*math.pi*k*theta))

def straightLineHomotopy(c1, c2): #c1 and c2 are curves parameterized by x
    def homotopy(s, t):
        dx = c2(s)[0]-c1(s)[0]
        dy = c2(s)[1] - c1(s)[1]
        return (t*dx+c1(s)[0], t*dy+c1(s)[1])
    return homotopy

def square(t, length):
    t = (2-t+.375) % 1
    if t <=.25:
        return (-1*length/2+4*t*length, length/2)
    elif t <= .5:
        return (length/2, length/2 - 4*(t-.25)*length)
    elif t <= .75:
        return (length/2 - 4*(t-.5)*length, -1*length/2)
    else:
        return (-1*length/2, 4*(t-.75)*length-length/2)

def spiral(b, length):
    def curve(t):
        t *= length
        return ((b*t)*math.cos(t), (b*t)*math.sin(t))
    return curve


# parameterCurve(flower, 1000, 5, 0, 2, 100)
parameterCurve(flower, 20000, 5, 0, 16, 100)
# traceCurve(lambda t: circ(t,400), 10000, 10, 1000)
# parameterCurve(straightLineHomotopy(lambda t: square(t, 200), lambda t: circ(t, 400)), 20000, 5, 0, 1, 1000)

# traceCurve(spiral(20, 6*math.pi), 20000, 5, 100)





