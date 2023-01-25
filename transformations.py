from ratefunctions import *

class Rotation:
    def __init__(self, parent, angle, time, delay=0, axis=(0,0), ratefunc=SmoothMove()):
        self.parent = parent
        self.angle = angle
        self.time = time
        self.delay = delay
        self.axis = axis
        self.ratefunc = ratefunc
        self.step_angle = self.angle/self.time
        self.t = -self.delay

    def rotate(self, angle):
        rotatedPoints = []
        for point in self.parent.pointlist:
            rotatedPoints.append(rotate(np.array(point)-self.axis, angle)+self.axis) #note that this second 'rotate' function is from vec2d.py
        self.parent.pointlist = rotatedPoints

    def step(self):
        self.t += 1
        if self.t >= 0:
            ds = self.ratefunc.get_ds(self.t, self.time)
            self.rotate(self.step_angle*ds)


class ChangeColor:
    def __init__(self, parent, endColor, time, delay=0, ratefunc=ConstantRF()):
        self.parent = parent
        self.time = time
        self.startColor = RGBtoHSV(np.array(self.parent.color)) #assume that object colors are always RGB (for now!)
        if endColor[0] > 255 or type(endColor[1]) != int or type(endColor[2]) != int:
            self.endColor = np.array(endColor) #assume input is HSV
        else:
            self.endColor = RGBtoHSV(np.array(endColor)) #assume input is RGB
        self.ratefunc = ratefunc
        self.colorChange = self.endColor - self.startColor
        self.stepSize = self.colorChange / self.time
        self.t = -delay

    def fade(self, step):
        c1 = RGBtoHSV(self.parent.color)
        c2 = c1 + step
        self.parent.color = HSVtoRGB(c2)
        for i in range(3):
            if self.parent.color[i] > 255:
                self.parent.color[i] = 255
            elif self.parent.color[i] < 0:
                self.parent.color[i] = 0

    def step(self):
        self.t += 1
        if self.t >= 0 and self.t < self.time:
            ds = self.ratefunc.get_ds(self.t, self.time)
            self.fade(self.stepSize*ds)
