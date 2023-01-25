import pygame
import numpy as np

pygame.font.init()

white = (255,255,255)
black = (0,0,0)
grey = (160,160,160)
red = (200,0,0)
green = (0,200,0)
blue = (0,0,200)
yellow = (240,240,0)
orange = (255,179,0)
violet = (170,0,255)
purple = (212,0,255)
magenta = (255,0,191)

def HSVtoRGB(color):
    h,s,v = color
    c = v*s
    x = c*(1-abs((h/60) % 2 - 1))
    m = v - c


    #should be 0 <= h < 60; this is a quick fix for an error I don't fully understand
    if h < 60:
        rp, gp, bp = (c,x,0)
    elif 60 <= h < 120:
        rp, gp, bp = (x,c,0)
    elif 120 <= h < 180:
        rp, gp, bp = (0,c,x)
    elif 180 <= h < 240:
        rp, gp, bp = (0,x,c)
    elif 240 <= h < 300:
        rp, gp, bp = (x,0,c)
    elif 300 <= h: #< 360:
        rp, gp, bp = (c,0,x)
    else:
        print('Error converting HSV to RGB')
        print(h, s, v)

    return np.round(((np.array([rp, gp, bp]) + m) * 255)).astype(int)
def RGBtoHSV(color):
    r, g, b = color
    rp, gp, bp = np.array([r,g,b]) / 255
    cMax = max([rp, gp, bp])
    cMin = min([rp, gp, bp])
    delta = cMax - cMin

    if delta == 0:
        h = 0
    elif cMax == rp:
        h = 60 * (((gp - bp)/delta) % 6)
    elif cMax == gp:
        h = 60 * (((bp - rp)/delta) + 2)
    elif cMax == bp:
        h = 60 * (((rp - gp)/delta) + 4)

    if cMax == 0:
        s = 0
    else:
        s = delta / cMax

    v = cMax

    #cheap fix for unknown errors causing it to overshoot color bounds
    if h < 0:
        h = 0
    elif h > 360:
        h = h % 360
    if s < 0:
        s = 0
    elif s > 1:
        s = 1
    if v < 0:
        v = 0
    elif v > 1:
        v = 1
    return np.array([h,s,v])

class Button(object):
    def __init__(self, text, pos, dim, on=True, col=black, text_col=white, size=15, font="freesansbold.ttf"):
        self.text = text
        self.pos = np.array(pos)
        self.dim = np.array(dim)
        self.on = on
        self.col = col
        self.text_col = text_col
        self.font = pygame.font.Font(font,size)
        self.button = pygame.rect.Rect(self.pos, self.dim)
        self.border = pygame.rect.Rect(self.pos-1, self.dim+2)

    def draw(self, screen):
        pygame.draw.rect(screen, black, self.border)
        pygame.draw.rect(screen, self.col, self.button)
        text_size = self.font.size(self.text)
        text_pos = (self.button.center[0]-text_size[0]/2,
                    self.button.center[1]-text_size[1]/2)
        show_text(screen, self.text, text_pos, col=self.text_col, font=self.font)

    def click(self, cursor):
        if (self.button.left < cursor[0] < self.button.right and
            self.button.top < cursor[1] < self.button.bottom):
            return True
        else:
            return False


class Slider(object):
    def __init__(self, pos, dim, lim):
        self.pos = np.array(pos)
        self.dim = np.array(dim)
        self.lim = lim
        self.bar = pygame.rect.Rect(self.pos, self.dim)
        self.button = pygame.rect.Rect(self.pos, (30, self.dim[1]))
        self.scale = (self.lim[1]-self.lim[0])/(self.bar.width-self.button.width+1)
        self.offset = None

    def move(self):
        cursor = pygame.mouse.get_pos()
        new_pos = cursor[0]-self.offset

        if new_pos - slider.button.left > 0: #moving right
            if slider.button.right < slider.bar.right:
                slider.button.left = cursor[0]-self.offset

        elif new_pos - slider.button.left < 0: #moving left
            if slider.button.left > slider.bar.left:
                slider.button.left = cursor[0]-self.offset

        if slider.button.right > slider.bar.right+1:
            slider.button.right = slider.bar.right+1
        elif slider.button.left < slider.bar.left:
            slider.button.left = slider.bar.left


    def draw(self):
        pygame.draw.line(screen, (0,0,0), (self.bar.left, self.bar.center[1]),
                                          (self.bar.right, self.bar.center[1]), 2)
        pygame.draw.rect(screen, (100,0,0), self.button)

    def click(self, cursor):
        if (self.button.left < cursor[0] < self.button.right and
            self.button.top < cursor[1] < self.button.bottom):

            self.offset = cursor[0]-self.button.left
            return True

        else:
            return False

    def val(self):
        return int((self.button.left-self.bar.left)*self.scale + self.lim[0])



def show_text(surface, text, pos, size=15, col=black, font="freesansbold.ttf"):
    if type(font) == str:
        font = pygame.font.Font(font,size)
    text = font.render(text, True, col)
    surface.blit(text, pos)

def save(filename, objects):
    pickle.dump(objects, open(filename+".p", "wb"))
    print("Objects saved in "+filename+".p\n")

def load(filename):
    return pickle.load(open(filename+".p", "rb"))
