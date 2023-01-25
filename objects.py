from ratefunctions import *
from vec2d import *
from game_tools import *

class Window:
    def __init__(self, screenSize):
        self.screenSize = screenSize
        self.screen = pygame.display.set_mode(screenSize)
    def toPixel(self, coords):
        #takes in (width, height) as fraction of total size and returns pixel coordinates
        return self.camera.toPixel(coords)
    def getScreen(self):
        return self.screen


class Element:
    def __init__(self, parent, pos, dim):
        #pos: top-left, dim: width-height, expressed as fraction of parent elements
        self.parent = parent
        self.pos = pos
        self.dim = dim
        self.elements = [] #contains subelements
        self.mobjects = [] #contains mobjects
    def toParentCoords(self, coords):
        return self.pos + coords * self.dim
    def toPixel(self, coords):
        return self.parent.toPixel(self.toParentCoords(coords))
    def getScreen(self):
        return self.parent.getScreen()
    def add_graph(self, pos, dim, **kwargs):
        graph = Graph(self, pos, dim, **kwargs)
        self.elements.append(graph)
        return graph
    def update(self):
        for element in self.elements:
            element.update()
        for mobject in self.mobjects:
            mobject.update()
    def draw(self):
        for element in self.elements:
            element.draw()
        for mobject in self.mobjects:
            mobject.draw()

class Mobject:
    def __init__(self, parent, **kwargs):
        self.parent = parent
        if self.parent != None: self.screen = parent.getScreen()
        self.currentMovements = []
        self.mobjects = []
        self.params.update(kwargs)
        for name, value in self.params.items():
            if type(value) == list or type(value) == tuple:
                value = np.array(value)
            setattr(self, name, value)
    def setParent(self, parent):
        self.parent = parent
        self.screen = parent.getScreen()
    def getScreen(self):
        return self.parent.getScreen()
    def toPixel(self, coords):
        return self.parent.toPixel(coords)
    def move(self):
        for movement in self.currentMovements:
            movement.step()
            if movement.t >= movement.time:
                self.currentMovements.remove(movement)
    def update(self):
        self.move()
        #should objects in self.mobjects be updated here as well?
    def rotateBy(self, angle, axis, time, delay=0, ratefunc=SmoothMove()):
        self.currentMovements.append(
            Rotation(
                parent = self,
                angle = angle,
                axis = axis,
                time = time,
                delay = delay,
                ratefunc = ratefunc
                )
            )
    def changeColorTo(self, endColor, time, delay=0, ratefunc=ConstantRF()):
        self.currentMovements.append(
            ChangeColor(
                parent = self,
                endColor = endColor,
                time = time,
                delay = delay,
                ratefunc = ratefunc
            )
        )

class Graph(Element, Mobject):
    params = {
        'xRange': (-10,10),
        'yRange': (-10, 10),
        'xGridlines': 1,
        'yGridlines': 1,
        'curves': [],
        'vectors': [],
        'axisColor': white,
        'gridlineColor': (50,50,50),
        'tickColor': white,
        'tickInterval': 0.5,
        'gridlineInterval': 1
        }
    def __init__(self, parent, pos, dim, **kwargs):
        Element.__init__(self, parent, pos, dim)
        Mobject.__init__(self, parent, **kwargs)
        self.create_axes()
    def toParentCoords(self, coords):
        #convert graph coordinates to fraction of total graph dimension, then convert to fraction of parent element
        xMin, xMax = self.xRange
        yMin, yMax = self.yRange
        x, y = coords
        newX = (x - xMin) / (xMax - xMin) * self.dim[0] + self.pos[0]
        newY = (yMax - y) / (yMax - yMin) * self.dim[1] + self.pos[1]  #the 'yMax - y' term is different to flip the y-axis
        return np.array([newX, newY])
    def create_axes(self):
        self.xAxis = Axis(
            parent = self,
            angle = 0,
            domain = self.xRange,
            extent = self.yRange, #how far the gridlines extend perpendicular to the axis (come up with a better name/system for this)
            tickInterval = self.tickInterval,
            gridlineInterval = self.gridlineInterval,
            axisColor = self.axisColor,
            tickColor = self.tickColor,
            gridlineColor = self.gridlineColor,
            name = 'x axis'
            )
        self.yAxis = Axis(
            parent = self,
            angle = np.pi/2,
            domain = self.yRange,
            extent = self.xRange,
            tickInterval = self.tickInterval,
            gridlineInterval = self.gridlineInterval,
            axisColor = self.axisColor,
            tickColor = self.tickColor,
            gridlineColor = self.gridlineColor,
            name = 'y axis'
            )
    def add_curve(self, curve):
        curve.setParent(self)
        self.mobjects.append(curve)
        return curve
    def plot_vector(self, params):
        self.vectors.append(Vector(params))
    def add_line(self, **kwargs):
        line = Line(parent=self, **kwargs)
        self.mobjects.append(line)
        return line
    def add_circle(self, **kwargs):
        circle = Circle(parent=self, **kwargs)
        self.mobjects.append(circle)
        return circle
    def draw_axes(self):
        self.xAxis.draw()
        self.yAxis.draw()
    def draw_curves(self): #obsolete?
        for curve in self.curves:
            curve.draw()
        for vector in self.vectors:
            vector.draw()
    def draw(self):
        self.draw_axes()
        for mobject in self.mobjects:
            mobject.draw()

class Axis(Mobject):
    params = {
        'angle': 0,
        'tickInterval': 1,
        'gridlineInterval': 1,
        'domain': (-10,10),
        'name': None
        }

    def __init__(self, parent, **kwargs):
        Mobject.__init__(self, parent, **kwargs)
        self.create_axis()
        self.create_ticks()
        self.create_gridlines()
    def create_axis(self):
        self.axisLine = Line(
            parent = self,
            start = vec(self.domain[0], self.angle),
            end = vec(self.domain[1], self.angle),
            width = 0.01,
            color = self.axisColor,
            arrowLength = 0
            )
    def create_ticks(self):
        self.ticks = []
        for n in np.arange(self.domain[0], self.domain[1]+self.tickInterval, self.tickInterval):
            if n != 0:
                self.ticks.append(Tick(
                    parent = self,
                    pos = vec(n, self.angle),
                    angle = self.angle + np.pi/2,
                    color = self.tickColor
                    ))
    def create_gridlines(self):
        self.gridlines = []
        for n in np.arange(self.domain[0], self.domain[1]+self.gridlineInterval, self.gridlineInterval):
            if n!= 0:
                self.gridlines.append(Gridline(
                    parent = self,
                    pos = vec(n, self.angle),
                    angle = (self.angle + np.pi/2) % np.pi, #prevents angle being set to pi
                    color = self.gridlineColor,
                    domain = self.domain,
                    extent = self.extent
                    ))
    def draw(self):
        for gridline in self.gridlines:
            gridline.draw()
        self.axisLine.draw()
        for tick in self.ticks:
            tick.draw()

class Tick(Mobject):
    params = {
        'pos': (0,0),
        'length': 0.1,  #previously 0.2
        'angle': 0
        }

    def __init__(self, parent, **kwargs):
        Mobject.__init__(self, parent, **kwargs)
        self.create_line()

    def create_line(self):
        start = self.pos + vec(self.length/2, self.angle)
        end = self.pos - vec(self.length/2, self.angle)
        self.line = Line(self,
                         start = start,
                         end = end,
                         color = self.color
                         )
    def draw(self):
        self.line.draw()

class Gridline(Mobject):
    params = {
        'pos': (0,0),
        'domain': (-10,10),
        'extent': (-10, 10), #how far gridlines reach perpendicular to axis (mentioned above)
        'angle': 0,
        }

    def __init__(self, parent, **kwargs):
        Mobject.__init__(self, parent, **kwargs)
        self.create_line()

    def create_line(self):
        start = self.pos + vec(self.extent[0], self.angle)
        end = self.pos + vec(self.extent[1], self.angle)
        self.line = Line(
            parent = self,
            start = start,
            end = end,
            color = self.color
            )
    def draw(self):
        self.line.draw()

class Line(Mobject):
    params = {
        'start': (0,0),
        'end': (10,10),
        'color': white,
        'width': 0.001,
        'draw_start_arrow': False,
        'draw_end_arrow': False,
        'arrowWidth': 0.1,
        'arrowLength': 0.15
        }

    def __init__(self, parent, **kwargs):
        Mobject.__init__(self, parent, **kwargs)
        self.update_vectors()
        self.end_arrow_base = self.end-self.arrowLength*self.unit_vector  #need to restructure this a bit
        #self.create_arrows()  #need to include 'Triangle' class first
        self.update_vertices()


    def update_vectors(self):
        self.vector = r_vec(self.start, self.end)
        self.unit_vector = norm(r_vec(self.start, self.end))
        self.normal_vector = rotate(self.unit_vector, np.pi/2)

    def update_vertices(self):
        self.update_vectors()
        self.end_arrow_base = self.end-self.arrowLength*self.unit_vector

        p1 = self.end_arrow_base + self.width/2 * self.normal_vector
        p2 = self.end_arrow_base - self.width/2 * self.normal_vector
        p3 = self.start - self.width/2 * self.normal_vector
        p4 = self.start + self.width/2 * self.normal_vector

        self.vertices = np.array([p1, p2, p3, p4])
        self.midpoint = self.get_midpoint()
        if self.draw_start_arrow:
            self.start_arrow.vertices = self.get_start_arrow_vertices()
        if self.draw_end_arrow:
            self.end_arrow.vertices = self.get_end_arrow_vertices()

    def get_midpoint(self):
        return self.start + (self.end-self.start)/2

    def get_start_arrow_vertices(self):
        return np.array([self.start_arrow_base + self.normal_vector*self.arrowWidth,
                         self.start_arrow_base - self.normal_vector*self.arrowWidth,
                         self.start_arrow_base + self.unit_vector*self.arrowLength])

    def get_end_arrow_vertices(self):
        return np.array([self.end_arrow_base + self.normal_vector*self.arrowWidth,
                         self.end_arrow_base - self.normal_vector*self.arrowWidth,
                         self.end_arrow_base + self.unit_vector*self.arrowLength])

    def create_arrows(self):
        if self.draw_start_arrow:
            self.start = self.start + self.unit_vector*self.arrowLength
            self.start_arrow = Triangle(params={'vertices': self.get_start_arrow_vertices(), 'color': self.color})
        if self.draw_end_arrow:
            self.end_arrow = Triangle(params={'vertices': self.get_end_arrow_vertices(), 'color': self.color})

    def update(self):
        self.pointlist = np.array([self.start, self.end])
        self.move()   #Mobject.update(self)
        self.start, self.end = self.pointlist
        self.update_vertices()

    def draw(self):
        color = self.color.astype(int)

        if self.draw_start_arrow:
            self.start_arrow.color = color
        if self.draw_end_arrow:
            self.end_arrow.color = color



        #converted_vertices = list(map(lambda x: parent.toPixel().astype(int), self.vertices))

        convertedPoints = []
        for vertex in self.vertices:
            convertedPoints.append(self.parent.toPixel(vertex).astype(int))   #make it so 'toPixel' can handle arrays of coordinates

        pygame.gfxdraw.aapolygon(self.screen, convertedPoints, color)
        pygame.gfxdraw.filled_polygon(self.screen, convertedPoints, color)

        # if self.draw_start_arrow:

        #     self.start_arrow.draw(graph)
        # if self.draw_end_arrow:
        #     self.end_arrow.draw(graph)

class Circle(Mobject):
    params = {
        'center': (0,0),
        'radius': 1,
        'color': white,
        'width': 1, #use width=0 to fill shape
        'resolution': 100 #number of points
        }

    def __init__(self, parent, **kwargs):
        Mobject.__init__(self, parent, **kwargs)
        self.update()
        if self.width == 0:
            self.filled = True
        else:
            self.filled = False

    def update(self):
        angles = np.linspace(0, 2*np.pi, self.resolution)
        self.points = self.radius * np.transpose(np.array([np.cos(angles), np.sin(angles)]))

    def draw(self): #needs work
        points = []
        for point in self.points:
            points.append(self.parent.toPixel(point).astype(int))
        if self.filled:
            gfxdraw.filled_polygon(self.screen, points, self.color)
        else:
            gfxdraw.aapolygon(self.screen, points, self.color)

class Curve(Mobject):
    params = {
        'func': np.sin,
        'domain': (-np.pi, np.pi),
        'color': blue,
        'width': 2,
        'res': 100
    }

    def __init__(self, parent=None, **kwargs):
        Mobject.__init__(self, parent, **kwargs)
        self.update()

    def update(self):
        self.xpoints = np.linspace(self.domain[0], self.domain[1], self.res)
        self.ypoints = self.func(self.xpoints)
        Mobject.update(self)

    def draw(self):
        points = np.transpose(np.array([self.xpoints, self.ypoints]))
        ppixel = np.array([self.toPixel(point).astype(int) for point in points])
        for i in range(0, self.res-1):
            pygame.draw.line(self.screen, self.color, ppixel[i], ppixel[i+1], self.width)

class Trace(Mobject):
    params = {
        'leader': None,
        'domain': (-np.pi, np.pi),
        'res': 100,
        'color': blue,
        'width': 2
    }

    def __init__(self, parent=None, **kwargs):
        self.points = []
        Mobject.__init__(self, parent, **kwargs)

    def set_leader(self, leader):
        self.leader = leader
        leader.setParent(self)
        self.mobjects.append(leader)
        self.points = [leader.pos]*2

    def update(self):
        if self.leader != None:
            self.leader.update()
            newPoint = self.leader.pos
            if np.sqrt(np.sum((newPoint-self.points[-1])**2)) > (self.domain[1]-self.domain[0])/self.res:
                self.points.append(newPoint)
        Mobject.update(self)

    def draw(self):
        if len(self.points) > 1:
            ppixel = np.array([self.toPixel(point).astype(int) for point in np.array(self.points)])
            pygame.draw.lines(self.screen, self.color, False, ppixel, self.width)
        self.leader.draw()


class Point(Mobject):
    params = {
        'pos': (0,0),
        'func': None,
        'color': red,
        'radius': 2,
        'width': 0
    }

    def __init__(self, parent=None, **kwargs):
        Mobject.__init__(self, parent, **kwargs)

    def update(self):
        if self.func != None:
            self.pos = self.func(1)

    def draw(self):
        pygame.draw.circle(self.screen, self.color, self.toPixel(self.pos).astype(int), self.radius, self.width)
