import numpy as np

def mag(u):
    return np.sqrt(u[0]**2 + u[1]**2)

def norm(u):
    return u/mag(u)

def proj(u, v):
    return np.dot(u, norm(v))

def vec(r, theta):
    return np.array([r*np.cos(theta), r*np.sin(theta)])

def angle(u, v=(1,0)):
    return np.arccos(np.dot(u, v) / (mag(u)*mag(v)))

def r_vec(u, v):
    return np.array([v[0]-u[0], v[1]-u[1]])

def reflection(theta):
    return np.array([[np.cos(2*theta), np.cos(2*theta - np.pi/2)],
                     [np.sin(2*theta), np.sin(2*theta - np.pi/2)]])

def rotate(u, theta):
    matrix = np.array([[np.cos(theta), -np.sin(theta)],
                       [np.sin(theta), np.cos(theta)]])
    return np.dot(matrix, u)
