import cv2 as cv
import numpy as np

class RectSelector:
    def __init__(self, win, callback):
        self.win = win
        self.callback = callback
        cv.setMouseCallback(win, self.onmouse)
        self.drag_start = None
        self.drag_rect = None
    def onmouse(self, event, x, y, flags, param):
        x, y = np.int16([x, y])
        if event == cv.EVENT_LBUTTONDOWN:
            self.drag_start = (x, y)
            return
        if self.drag_start:
            if flags & cv.EVENT_FLAG_LBUTTON:
                xo, yo = self.drag_start
                x0, y0 = np.minimum([xo, yo], [x, y])
                x1, y1 = np.maximum([xo, yo], [x, y])
                self.drag_rect = None
                if x1-x0 > 0 and y1-y0 > 0:
                    self.drag_rect = (x0, y0, x1, y1)
            else:
                rect = self.drag_rect
                self.drag_start = None
                self.drag_rect = None
                if rect:
                    self.callback(rect)
    def draw(self, vis):
        if not self.drag_rect:
            return False
        x0, y0, x1, y1 = self.drag_rect
        cv.rectangle(vis, (x0, y0), (x1, y1), (0, 255, 0), 2)
        return True
    @property
    def dragging(self):
        return self.drag_rect is not None


class PointSelector:
    def __init__(self, win, callback):
        self.win = win
        self.callback = callback
        cv.setMouseCallback(win, self.onmouse)
        self.drag_start = None
        self.drag_rect = None
        self.state = False

    def onmouse(self, event, x, y, flags, param):
        x, y = np.int16([x, y])
        if event == cv.EVENT_LBUTTONDOWN:
            self.drag_start = (x, y)
            self.state = not self.state
            return
        elif self.state:
            x0, y0 = self.drag_start
            if abs(x0-x) > 100:
                x0 = x
                self.drag_start = (x0,y)
            if abs(y0-y) > 100:
                y0 = y
                self.drag_start = (x,y0)
                
            if x0 != x or y0 != y:
                self.drag_rect = (x0, y0, x, y)
                self.callback(self.drag_rect)
