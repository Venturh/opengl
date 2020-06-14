import math
import numpy as np
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.arrays import vbo

FILE ="bunny"
#FILE ="elephant"

class Scene:
    def __init__(self, width, height):
        self.vertices = []
        self.vnormals = []
        self.faces = []
        self.createObjFromFile()
        self.minimum, self.maximum = self.createBoundingBox()
        centerMin = np.array((self.minimum[0]/2, self.minimum[1]/2, self.minimum[2]/2))
        centerMax = np.array((self.maximum[0]/2, self.maximum[1]/2, self.maximum[2]/2))
        self.center = (centerMin + centerMax) /2
        print("center", self.center)
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
        self.zoom = self.scale
        self.initScale = self.scale
        self.startP = [0, 0, 0]
        self.moveP = 0
        self.translateXY = (0.0, 0.0)
        self.colors = {"black": (0.0, 0.0, 0.0), "white": (1.0, 1.0, 1.0), "red": (1.0, 0.0, 0.0),
                       "blue": (0.0, 0.0, 1.0), "yellow": (1.0, 1.0, 0.0)}
        self.color = self.colors["blue"]
        self.showShadow = False
        print("scaloe", self.scale)

    def createObjFromFile(self):
        #for line in open(sys.argv[1]):
        for line in open(FILE +".obj"):
            if line.split():
                type = line.split()[0]
                if (type == 'v'):
                    self.vertices.append(list(map(float, line.split()[1:])))
                if (type == 'vn'):
                    self.vnormals.append(list(map(float, line.split()[1:])))
                if (type == "f"):
                    if(len(self.vnormals) > 0):
                        for face in line.split()[1:]:
                            self.faces.append(list(map(float, face.split('//'))))
                    elif (len(self.vnormals) == 0):
                        for face in line.splitlines():
                            self.faces.append(list(map(float, face[1:].split())))

    def createBoundingBox(self):
        minimum = (
            min([x[0] for x in self.vertices]), min([x[1] for x in self.vertices]), min([x[2] for x in self.vertices]))

        maximum = (
            max([x[0] for x in self.vertices]), max([x[1] for x in self.vertices]), max([x[2] for x in self.vertices]))
        return minimum, maximum

    def scaleIt(self, minimum, maximum):
        xmin, ymin, zmin = minimum
        xmax, ymax, zmax = maximum
        return 2.0 / max(abs(xmax - xmin),
                         abs(ymax - ymin), abs(zmax - zmin),)

    def translateIt(self, minimum, maximum):
        xmin, ymin, zmin = minimum
        xmax, ymax, zmax = maximum
        transx = - ((xmax + xmin) / 2.0)
        transy = - ((ymax + ymin) / 2.0)
        transz = - ((zmax + zmin) / 2.0)

        return transx, transy, transz

    def createData(self):
        newData = []
        if len(self.vnormals) == 0:
            while len(self.vnormals) < len(self.vertices):
                self.vnormals.append(np.zeros(3))
            for face in self.faces:
                v1 = np.array(self.vertices[int(face[0]) - 1])
                v2 = np.array(self.vertices[int(face[1]) - 1])
                v3 = np.array(self.vertices[int(face[2]) - 1])
                n = np.cross(v2 - v1, v3 - v1)
                #print("normals",  np.cross(v2 - v1, v3 - v1))
                self.vnormals[int(face[0]) - 1] = n
                self.vnormals[int(face[1]) - 1] = n
                self.vnormals[int(face[2]) - 1] = n
            print(self.vnormals)

        for vertex in self.faces:
            vn = int(vertex[0]) - 1
            nn = int(vertex[1]) - 1
            newData.append(self.vertices[vn] + self.vnormals[nn])

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
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_NORMALIZE)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)


        light = (self.maximum[1] - self.minimum[1]) * 2,(self.maximum[1] - self.minimum[1]) * 3, (self.maximum[1] - self.minimum[1]) * 2

        glMatrixMode(GL_MODELVIEW)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        self.vb.bind()
        glEnableClientState(GL_VERTEX_ARRAY)
        glEnableClientState(GL_NORMAL_ARRAY)

        glVertexPointer(3, GL_FLOAT, 24, self.vb)
        glNormalPointer(GL_FLOAT, 24, self.vb + 12)

        glLightfv(GL_LIGHT0, GL_POSITION, light)
        if self.showShadow:
            p = [1.0, 0, 0, 0, 0, 1.0, 0, -1.0 / light[1], 0, 0, 1.0, 0, 0, 0, 0, 0]
            glMatrixMode(GL_MODELVIEW)
            glPushMatrix()
            glTranslatef(light[0], light[1], light[2])
            glTranslatef(0.0, self.minimum[1], 0.0)
            glDisable(GL_DEPTH_TEST)
            glDisable(GL_LIGHTING)

            glMultMatrixf(p)
            glColor3fv(self.colors["black"])
            glTranslatef(0.0, -self.minimum[1], 0.0)
            glTranslatef(-light[0], -light[1], -light[2])
            glDrawArrays(GL_TRIANGLES, 0, len(self.data))

            glEnable(GL_LIGHTING)
            glEnable(GL_DEPTH_TEST)
            glPopMatrix()

        glLoadIdentity()

        if self.translateXY:
            glTranslate(self.translateXY[0], -self.translateXY[1], 0.0)


        glColor3fv(self.color)
        glScale(self.scale, self.scale, self.scale)
        glTranslate(-self.center[0], -self.center[1], -self.center[2])
        glMultMatrixf(self.actOri * self.rotate(self.angle, self.axis))
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        glDrawArrays(GL_TRIANGLES, 0, len(self.data))

        self.vb.unbind()
        glDisableClientState(GL_VERTEX_ARRAY)
        glDisableClientState(GL_NORMAL_ARRAY)
