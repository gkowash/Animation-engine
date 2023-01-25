import os
import time
import numpy as np
import pygame
from pygame import gfxdraw

from camera import *
from objects import *
from transformations import *
from ratefunctions import *
from euler_lagrange import *

#recording parameters
record = True
compile_video = True

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


testPath = Lagrange(window=myWindow, canvas=myCanvas, camera=myCam, func=lambda x: np.sin(5*x)+15-2.8*x, srange=(0,120), fps=fps, clock=clock, record=record)
testPath.play()
print("Finished running test path")

##truePath = Lagrange(func=lambda x: -0.5*x**2 + 15, srange=(-50,30))
##truePath.play()
##del(truePath)
##print("Finished running true path")

print("Scene complete")

if record and compile_video:
    os.system('python3 compile_video.py')

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
    time.sleep(0.1)
