import math
import numpy as np
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.arrays import vbo


class Scene:
    def __init__(self, width, height):
        self.vertices = []
        self.vnormals = []
        self.faces = []
        self.createObjFromFile()
        self.minimum, self.maximum = self.createBoundingBox()
        self.scale = self.scaleIt(self.minimum, self.maximum)
        self.translate = self.translateIt(self.minimum, self.maximum)
        self.data = self.createData()
        self.vb = vbo.VBO(np.array(self.data, 'f'))
        self.showVector = True
        self.width = width
        self.height = height
        self.angle = 0
        self.actOri = [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]
        self.axis = np.array([0, 0, 1])
        self.zoom = 0
        self.startP = [0, 0, 0]
        self.moveP = 0
        self.translateXY = (0.0, 0.0)
        self.colors = {"black": (0.0, 0.0, 0.0), "white": (1.0, 1.0, 1.0), "red": (1.0, 0.0, 0.0),
                       "blue": (0.0, 0.0, 1.0), "yellow": (1.0, 1.0, 0.0)}
        self.color = self.colors["blue"]

    def createObjFromFile(self):
        for line in open(sys.argv[1]):
            if line.split():
                type = line.split()[0]
                if (type == 'v'):
                    self.vertices.append(list(map(float, line.split()[1:])))
                if (type == 'vn'):
                    self.vnormals.append(list(map(float, line.split()[1:])))
                if (type == "f"):
                    first = line.split()[1:]
                    for face in first:
                        self.faces.append(list(map(float, face.split('//'))))

    def createBoundingBox(self):
        minimum = (
            min([x[0] for x in self.vertices]), min([x[1] for x in self.vertices]), min([x[2] for x in self.vertices]))
        maximum = (
            max([x[0] for x in self.vertices]), max([x[1] for x in self.vertices]), max([x[2] for x in self.vertices]))
        return minimum, maximum

    def scaleIt(self, minimum, maximum):
        xmin, ymin, zmin = minimum
        xmax, ymax, zmax = maximum
        xr = xmax - xmin
        yr = ymax - ymin
        zr = zmax - zmin
        return 2.0 / max(xr, yr, zr)

    def translateIt(self, minimum, maximum):
        xmin, ymin, zmin = minimum
        xmax, ymax, zmax = maximum
        transx = - ((xmax + xmin) / 2.0)
        transy = - ((ymax + ymin) / 2.0)
        transz = - ((zmax + zmin) / 2.0)

        return transx, transy, transz

    def createData(self):
        newData = []
        for vertex in self.faces:
            vn = int(vertex[0]) - 1
            nn = int(vertex[1]) - 1
            if 0 <= nn < len(self.vnormals):
                newData.append(self.vertices[vn] + self.vnormals[nn])
            else:
                self.vnormals = [x - y for x, y in
                                 zip(self.vertices[vn], [self.translate[0], self.translate[1], self.translate[2]])]
                l = math.sqrt(self.vnormals[0] ** 2 + self.vnormals[1] ** 2 + self.vnormals[2] ** 2)
                self.vnormals = [x / l for x in self.vnormals]
                newData.append(self.vertices[vn] + self.vnormals)
        return newData

    def rotate(self, angle, axis):
        c, mc = math.cos(angle), 1 - math.cos(angle)
        s = math.sin(angle)
        l = math.sqrt(np.dot(np.array(axis), np.array(axis)))
        x, y, z = np.array(axis) / l
        r = np.matrix(
            [[x * x * mc + c, x * y * mc - z * s, x * z * mc + y * s, 0],
             [x * y * mc + z * s, y * y * mc + c, y * z * mc - x * s, 0],
             [x * z * mc - y * s, y * z * mc + x * s, z * z * mc + c, 0],
             [0, 0, 0, 1]])
        return r.transpose()

    def render(self):
        # render the vector starting at the point

        glMatrixMode(GL_MODELVIEW)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)

        glEnable(GL_COLOR_MATERIAL)
        glLightfv(GL_LIGHT0, GL_POSITION, np.array([0.0, 100000.0, -0.1, 0.0]))

        self.vb.bind()
        glEnableClientState(GL_VERTEX_ARRAY)
        glEnableClientState(GL_NORMAL_ARRAY)
        glVertexPointer(3, GL_FLOAT, 24, self.vb)
        glNormalPointer(GL_FLOAT, 24, self.vb + 12)

        if self.translateXY is not None:
            glTranslate(self.translateXY[0], -self.translateXY[1], 0.0)

        glMultMatrixf(self.actOri * self.rotate(self.angle, self.axis))

        glColor3fv(self.color)
        glScale(self.scale, self.scale, self.scale)
        glTranslate(-0, -0, -0)
        glDrawArrays(GL_TRIANGLES, 0, len(self.data))

        self.vb.unbind()
        glDisableClientState(GL_VERTEX_ARRAY)
        glDisableClientState(GL_NORMAL_ARRAY)
