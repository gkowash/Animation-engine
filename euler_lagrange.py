from animFW import *
import time


#initialize clock
fps = 30
clock = pygame.time.Clock()

#initialize window
myWindow = Window(
    screenSize = (1200,600)  #size in pixels
)

#initialize camera
myCam = Camera(
    window=myWindow,
    pos=(0.50, 0.50),
    zoom=1.00
)

#initialize main canvas
myCanvas = Element(
    parent = myWindow,
    pos = (0,0),
    dim = (1,1)
)



def show_text(text=None, pos=None, font_name="freesansbold.ttf", font_size=25, font_col=white, surface=myWindow.screen):
    if text != None:
        font = pygame.font.Font(font_name, font_size)
        text_obj = font.render(text, True, font_col)
        text_size = font.size(text)
        surface.blit(text_obj, (pos[0]-int(text_size[0]/2), pos[1]-int(text_size[1]/2)))
    


class LCurve(Curve):
    params = {
        'func': lambda x: x,
        'eta': lambda x,a,b: 0,
        'eps': 0,
        'a': 0,
        'b': 0,
        'domain': (-5, 5),
        'color': green,
        'width': 3,
        'res': 100
    }
    
    def getLagrangian(self, xvals, scale=1):
        if xvals.size != self.xpoints.size:
            print("Array supplied to Lagrangian function has incorrect dimension. Check that the domain and resolution are the same as for the position curve.")
            raise SystemExit
        
        lagr = []
        for i,x in enumerate(xvals[1:-1]):
            j = i+1  #account for shift from starting at index 1        
            U = self.ypoints[j]  #particle of mass 1 in gravitational field in -y direction
            v = (self.ypoints[j+1]-self.ypoints[j-1]) / (self.xpoints[j+1]-self.xpoints[j-1])
            K = 0.5*1*v**2  #kinetic energy
            lagr.append(K-U)
        lagr.insert(0, lagr[0]) #pad start and end values to match dimension of xpoints
        lagr.append(lagr[-1])
        return np.array(lagr)*scale

    def getAction(self):
        lagr = self.getLagrangian(self.xpoints)
        dt = (self.domain[1]-self.domain[0])/self.res
        return np.sum(lagr)*dt
    
    def varyBy(self, eta, time, epsRange=None, aRange=None, bRange=None, delay=0, ratefunc=SmoothMove()):
        self.currentMovements.append(
            Variation(
                parent=self,
                eta=eta,
                epsRange=epsRange,
                aRange=aRange,
                bRange=bRange,
                time=time,
                delay=delay,
                ratefunc=ratefunc
            )
        ) 
    def update(self):
        self.xpoints = np.linspace(self.domain[0], self.domain[1], self.res)
        self.ypoints = self.func(self.xpoints) + self.eps*self.eta(self.xpoints, self.a, self.b)
        Mobject.update(self)


class Variation:
    def __init__(self, parent, eta, time, epsRange=None, aRange=None, bRange=None, delay=0, ratefunc=SmoothMove()):
        self.parent = parent
        self.parent.eta = eta
        self.epsRange = epsRange
        self.aRange = aRange
        self.bRange = bRange
        self.time = time
        self.delay = delay
        self.ratefunc = ratefunc
        if epsRange != None:
            self.parent.eps = epsRange[0]
            self.delta_eps = (epsRange[1]-epsRange[0])/self.time
        else:
            self.delta_eps = 0
        if aRange != None:
            self.parent.a = aRange[0]
            self.delta_a = (aRange[1]-aRange[0])/self.time
        else:
            self.delta_a = 0
        if bRange != None:
            self.parent.b = bRange[0]
            self.delta_b = (bRange[1]-bRange[0])/self.time
        else:
            self.delta_b = 0
        self.t = -self.delay
        
    def vary(self, eps_inc, a_inc, b_inc):
        self.parent.eps += eps_inc
        self.parent.a += a_inc
        self.parent.b += b_inc
        
    def step(self):
        self.t += 1
        if self.t >= 0:
            ds = self.ratefunc.get_ds(self.t, self.time)
            self.vary(self.delta_eps*ds, self.delta_a*ds, self.delta_b*ds)




class Lagrange:
    def __init__(self, func, srange):
        #set assumed path y(x) and range for action plot (this is a little janky)
        self.func = func
        self.srange = srange
        #initialize subcanvases/scene elements
        self.graph_pos = myCanvas.add_graph(
            pos = (0.01, 0.01),   #as fraction of full width/height
            dim = (0.48, 0.48),
            xRange = (-1, 6),
            yRange = (-5, 20),
            tickInterval = 1,
            gridlineColor = (40, 40, 70),
            axisColor = (180, 180, 180),
            tickColor = (180, 180, 180)
        )
        self.graph_lagr = myCanvas.add_graph(
            pos = (0.51, 0.51),   #as fraction of full width/height
            dim = (0.48, 0.48),
            xRange = (-1, 6),
            yRange = (-8, 20),
            tickInterval = 1,
            gridlineColor = (40, 40, 70),
            axisColor = (180, 180, 180),
            tickColor = (180, 180, 180)
        )
        self.graph_act = myCanvas.add_graph(
            pos = (0.01, 0.51),   #as fraction of full width/height
            dim = (0.48, 0.48),
            xRange = (-8, 8),
            yRange = self.srange,
            tickInterval = 10,
            gridlineColor = (40, 40, 70),
            axisColor = (180, 180, 180),
            tickColor = (180, 180, 180)
        )
        
        self.curve_pos = self.graph_pos.add_curve(
            LCurve(
                func = self.func,
                domain = (0,5),
                color = blue,
                width = 2,
                res = 400
            )
        )
        self.curve_lagr = self.graph_lagr.add_curve(
            Curve(
                func = lambda x: self.curve_pos.getLagrangian(x, scale=0.1),
                domain = (0,5),
                color = green,
                width = 2,
                res = 400
            )
        )

        self.point_act = Point(
            func = lambda x: np.array([self.curve_pos.eps, self.curve_pos.getAction()]),
            radius = 3
        )
            
        self.curve_act = self.graph_act.add_curve(
            Trace(
                domain = (-7,7),
                res = 200,
                color = orange
            )
        )
        self.curve_act.set_leader(self.point_act)


    def seg1(self):
        self.curve_pos.varyBy(
            eta = lambda x,a,b: np.exp(-30*(x-1)**2),
            epsRange = (0,3),
            time = 1*fps,
            delay = 1*fps
        )
        myCam.zoomTo(
            zf=2,
            time=1.5*fps
        )
        myCam.panTo(
            pf=(0.25,0.25),
            time=1.5*fps
        )

    def seg2(self):
        self.curve_pos.varyBy(
            eta = lambda x,a,b: np.exp(-30*(x-1)**2),
            epsRange = (3,-4),
            time = 1*fps
        )

    def seg3(self):
        self.curve_pos.varyBy(
            eta = lambda x,a,b: np.exp(-a*(x-b)**2),
            aRange = (30,5),
            bRange = (1,4),
            time = 1.5*fps,
        )
        myCam.zoomTo(
            zf=1.5,
            time=0.75*fps
        )
        myCam.zoomTo(
            zf=2,
            time=0.75*fps,
            delay=0.75*fps
        )
        myCam.panTo(
            pf=(0.75,0.75),
            time=1.5*fps
        )

    def seg4(self):
        self.curve_pos.varyBy(
            eta = lambda x,a,b: np.exp(-a*(x-b)**2),
            epsRange = (-4,4),
            aRange = (5,30),
            bRange = (4,1),
            time = 1.5*fps,
        )
        
    def seg5(self):
        self.curve_pos.varyBy(
            eta = lambda x,a,b: np.exp(-a*(x-b)**2),
            epsRange = (4,-6),
            aRange = (30,1),
            bRange = (1,3),
            time = 1*fps,
        )
        myCam.zoomTo(
            zf=1.75,
            time=0.75*fps
        )
        myCam.zoomTo(
            zf=2,
            time=0.75*fps,
            delay=0.75*fps
        )
        myCam.panTo(
            pf=(0.25,0.75),
            time=1.5*fps
        )
        

    def seg6(self):
        self.curve_pos.varyBy(
            eta = lambda x,a,b: np.exp(-a*(x-b)**2),
            epsRange = (-6,0),
            aRange = (1,10),
            bRange = (3,2),
            time = 1*fps,
        )

    def seg7(self):
        self.curve_pos.varyBy(
            eta = lambda x,a,b: np.exp(-a*(x-b)**2)*np.sin(3*x),
            epsRange = (0,5),
            aRange = (1,20),
            bRange = (2,4),
            time = 1*fps,
        )
##        myCam.zoomTo(
##            zf=1,
##            time=1*fps
##        )
##        myCam.panTo(
##            pf=(0.5,0.5),
##            time=1*fps
##        )


    def seg8(self):
        self.curve_pos.varyBy(
            eta = lambda x,a,b: np.exp(-a*(x-b)**2)*np.sin(3*x),
            epsRange = (5,0),
            time = 1*fps,
        )
        myCam.zoomTo(
            zf=1,
            time=1*fps,
            delay=1*fps
        )
        myCam.panTo(
            pf=(0.5,0.5),
            time=1*fps,
            delay=1*fps
        )
        
    def show(self, frames):
        for i in range(round(frames)):
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    raise SystemExit
            myWindow.screen.fill(black)
            myCam.update()
            for element in myCanvas.elements:
                element.update()
                element.draw()
            show_text("Action: {}".format(round(self.curve_pos.getAction())), np.array(myWindow.screenSize)*np.array([0.87,0.10]))
            show_text("x", self.graph_pos.toPixel((-0.3,19)))
            show_text("t", self.graph_pos.toPixel((5.5,-1)))
            show_text("L", self.graph_lagr.toPixel((-0.3,19)))
            show_text("t", self.graph_lagr.toPixel((5.5,-1)))
            show_text("S", self.graph_act.toPixel((-0.5,25)))
            show_text("epsilon", self.graph_act.toPixel((6,-4)))

            pygame.display.flip()
            clock.tick(fps)
            
    def play(self):
        self.seg1()
        self.show(2*fps)
        self.seg2()
        self.show(1*fps)
        self.seg3()
        self.show(2*fps)
        self.seg4()
        self.show(2*fps)
        self.seg5()
        self.show(1*fps)
        self.seg6()
        self.show(1*fps)
        self.seg7()
        self.show(1*fps)
        self.seg8()
        self.show(3*fps)

        self.curve_act.points = self.curve_act.points[:2] #reset point list in case of multiple run-throughs






testPath = Lagrange(func=lambda x: np.sin(5*x)+15-2.8*x, srange=(0,120))
testPath.play()
print("Finished running test path")

##truePath = Lagrange(func=lambda x: -0.5*x**2 + 15, srange=(-50,30))
##truePath.play()
##del(truePath)
##print("Finished running true path")

print("Scene complete")

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
    time.sleep(0.1)

