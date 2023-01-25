from ratefunctions import *

class Camera:
    def __init__(self, window, pos, zoom):
        self.pos = np.array(pos)
        self.zoom = zoom
        self.window = window
        window.camera = self
        self.currentMovements = []

    def toPixel(self, coords):
        topLeft = self.pos - (1/self.zoom) / 2 #top left corner of camera viewport in window frame
        newCoords = (coords - topLeft) * self.zoom #coordinate's position relative to top left in camera frame
        return self.window.screenSize * newCoords #convert to pixels

    def panTo(self, pf, time, delay=0, ratefunc=SmoothMove()):
        self.currentMovements.append(
            Pan(
                camera = self,
                p0 = self.pos,
                pf = pf,
                time = time,
                delay = delay,
                ratefunc = ratefunc
            )
        )

    def zoomTo(self, zf, time, delay=0, ratefunc=SmoothMove()):
        self.currentMovements.append(
            Zoom(
                camera=self,
                zf=zf,
                time=time,
                delay=delay,
                ratefunc=ratefunc
            )
        )

    def update(self):
        for movement in self.currentMovements:
            movement.step()
            if movement.t >= movement.time:
                self.currentMovements.remove(movement)


class Zoom:
    def __init__(self, camera, zf, time, delay=0, ratefunc=SmoothMove()):
        self.camera = camera
        self.z0 = None  #wait until after delay to set initial zoom
        self.zf = zf
        self.time = time
        self.t = -delay
        self.ratefunc = ratefunc

    def zoom(self, stepsize):
        self.camera.zoom += stepsize

    def step(self):
        self.t += 1
        if self.t >= 0 and self.t < self.time:
            if self.z0 == None:
                self.z0 = self.camera.zoom
                self.delta_z = (self.zf-self.z0)/self.time
            ds = self.ratefunc.get_ds(self.t, self.time)
            self.zoom(self.delta_z*ds)


class Pan:
    def __init__(self, camera, p0, pf, time, delay=0, ratefunc=SmoothMove()):
        self.camera = camera
        self.p0 = np.array(p0)
        self.pf = np.array(pf)
        self.time = time
        self.t = -delay
        self.ratefunc = ratefunc
        self.delta_p = (pf-p0)/time

    def pan(self, stepsize):
        self.camera.pos += stepsize

    def step(self):
        self.t += 1
        if self.t >= 0 and self.t < self.time:
            ds = self.ratefunc.get_ds(self.t, self.time)
            self.pan(self.delta_p*ds)
