import glfw
import math
import numpy as np
from OpenGL.GL import *
from OpenGL.GLUT import *

from Scene import Scene


class RenderWindow:
    def __init__(self):
        # save current working directory
        cwd = os.getcwd()

        # Initialize the library
        if not glfw.init():
            return

        # restore cwd
        os.chdir(cwd)

        # buffer hints
        glfw.window_hint(glfw.DEPTH_BITS, 32)

        # define desired frame rate
        self.frame_rate = 100

        # make a window
        self.width, self.height = 640, 480
        self.aspect = self.width / float(self.height)
        self.window = glfw.create_window(self.width, self.height, "2D Graphics", None, None)
        if not self.window:
            glfw.terminate()
            return
        self.mouseX = None
        self.mouseY = None
        self.doRotation = False
        self.doZoom = False
        self.doTranslate = False
        self.colors = {"black": (0.0, 0.0, 0.0, 0.0), "white": (1.0, 1.0, 1.0, 0.0), "red": (1.0, 0.0, 0.0, 0.0),
                       "blue": (0.0, 0.0, 1.0, 0.0), "yellow": (1.0, 1.0, 0.0, 0.0)}
        self.color = self.colors["yellow"]
        self.projections = "ortho"

        # Make the window's context current
        glfw.make_context_current(self.window)

        # create 3D
        self.scene = Scene(self.width, self.height)

        # initialize GL

        glViewport(0, 0, self.width, self.height)
        glEnable(GL_DEPTH_TEST)
        glClearColor(*self.color)
        glMatrixMode(GL_PROJECTION)
        glOrtho(-1.5, 1.5, -1.5, 1.5, -10.0, 10.0)
        # glOrtho(-self.width/2,self.width/2,-self.height/2,self.height/2,-2,2)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_NORMALIZE)

        # set window callbacks
        glfw.set_mouse_button_callback(self.window, self.onMouseButton)
        glfw.set_key_callback(self.window, self.onKeyboard)
        glfw.set_window_size_callback(self.window, self.onSize)
        glfw.set_cursor_pos_callback(self.window, self.mouse_moved)

        # exit flag
        self.exitNow = False

        # animation flag
        self.animation = True

    def onMouseButton(self, win, button, action, mods):

        if button == glfw.MOUSE_BUTTON_LEFT:
            r = min(self.width, self.height) / 2.0
            if glfw.get_mouse_button(win, button) == glfw.PRESS:
                self.doRotation = True
                self.scene.startP = self.projectOnSphere(self.mouseX, self.mouseY, r)
            if glfw.get_mouse_button(win, button) == glfw.RELEASE:
                self.doRotation = False
                self.scene.actOri = self.scene.actOri * self.scene.rotate(self.scene.angle, self.scene.axis)
                self.scene.angle = 0

        if button == glfw.MOUSE_BUTTON_MIDDLE:
            if glfw.get_mouse_button(win, button) == glfw.PRESS:
                self.doZoom = True
                self.scene.startP = [self.mouseX, self.mouseY, 0]
                self.scene.zoom = self.scene.startP[1]
            if glfw.get_mouse_button(win, button) == glfw.RELEASE:
                self.doZoom = False

        if button == glfw.MOUSE_BUTTON_RIGHT:
            if glfw.get_mouse_button(win, button) == glfw.PRESS:
                self.doTranslate = True
                self.scene.startP = [self.mouseX, self.mouseY, 0]
            if glfw.get_mouse_button(win, button) == glfw.RELEASE:
                self.doTranslate = False

    def mouse_moved(self, win, x, y):
        self.mouseX = x
        self.mouseY = y

        if self.doRotation:
            r = min(self.width, self.height) / 2.0
            moveP = self.projectOnSphere(x, y, r)
            dot = np.dot(self.scene.startP, moveP)
            self.scene.angle = math.acos(dot)
            self.scene.axis = np.cross(self.scene.startP, moveP)

        if self.doZoom:
            if self.scene.zoom > y and self.scene.scale > 0:
                self.scene.scale += abs(float(float((y - self.scene.startP[1])) / self.height))

            if self.scene.zoom <= y and self.scene.scale > 0:
                self.scene.scale -= abs(float(float((y - self.scene.startP[1])) / self.height))
            # if scale is to small/big
            if self.scene.scale <= 0.0015:
                self.scene.scale = 0.1
            if self.scene.scale >= 10:
                self.scene.scale = 8
            self.scene.zoom = y

        if self.doTranslate:
            self.scene.translateXY = self.scene.translateXY[0] + float(float((x - self.scene.startP[0])) / self.width), \
                                     self.scene.translateXY[1] + float(float((y - self.scene.startP[1])) / self.height)
            self.scene.startP = [self.mouseX, self.mouseY, 0]

    def onKeyboard(self, win, key, scancode, action, mods):

        if action == glfw.PRESS:

            if key == glfw.KEY_P:
                print("ortho")
                self.projections = "ortho"
                self.onSize(self.window, self.width, self.height)

            if key == glfw.KEY_O:
                print("central")
                self.projections = "central"
                self.onSize(self.window, self.width, self.height)

            if key == glfw.KEY_H:
                self.scene.showShadow = not self.scene.showShadow
                print("shadow", self.scene.showShadow)

            if mods:
                if key == glfw.KEY_S:
                    self.color = self.colors["black"]
                    glClearColor(*self.color)

                if key == glfw.KEY_W:
                    self.color = self.colors["white"]
                    glClearColor(*self.color)

                if key == glfw.KEY_R:
                    self.color = self.colors["red"]
                    glClearColor(*self.color)

                if key == glfw.KEY_G:
                    self.color = self.colors["yellow"]
                    glClearColor(*self.color)

                if key == glfw.KEY_B:
                    self.color = self.colors["blue"]
                    glClearColor(*self.color)



            # lower Case changes Object
            else:
                if key == glfw.KEY_S:
                    self.scene.color = self.scene.colors["black"]
                if key == glfw.KEY_W:
                    self.scene.color = self.scene.colors["white"]
                if key == glfw.KEY_R:
                    self.scene.color = self.scene.colors["red"]
                if key == glfw.KEY_G:
                    self.scene.color = self.scene.colors["yellow"]
                if key == glfw.KEY_B:
                    self.scene.color = self.scene.colors["blue"]

    def onSize(self, win, width, height):
        print("onsize: ", width, height)
        self.width = width
        self.height = height
        self.aspect = width / float(height)

        aspectHeight = float(height) / width

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glViewport(0, 0, self.width, self.height)

        if self.projections in "ortho":
            print("ortho")
            if width <= height:
                glOrtho(-1.5, 1.5, (-1.5) * aspectHeight,
                        1.5 * aspectHeight, -10.0, 10.0)
            else:
                glOrtho((-1.5) * self.aspect, 1.5 * self.aspect, -1.5, 1.5,
                        -10.0, 10.0)

        else:
            print("central")

        glMatrixMode(GL_MODELVIEW)


    def run(self):
        # initializer timer
        glfw.set_time(0.0)
        t = 0.0
        while not glfw.window_should_close(self.window) and not self.exitNow:
            # update every x seconds
            currT = glfw.get_time()
            if currT - t > 1.0 / self.frame_rate:
                # update time
                t = currT
                # clear
                glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

                # render scene
                self.scene.render()

                glfw.swap_buffers(self.window)
                # Poll for and process events
                glfw.poll_events()
        # end
        glfw.terminate()

    def projectOnSphere(self, x, y, r):
        x, y = x - self.width / 2.0, self.height / 2.0 - y
        a = min(r * r, x ** 2 + y ** 2)
        z = math.sqrt(r * r - a)
        l = math.sqrt(x ** 2 + y ** 2 + z ** 2)
        return x / l, y / l, z / l


# main() function
def main():
    print("Simple glfw render Window")
    rw = RenderWindow()
    rw.run()


# call main
if __name__ == '__main__':
    main()
