from __future__ import print_function

import cv2 as cv
import numpy as np
import time

from rect_selector import RectSelector
from processor import Processor
from play import Play

class App:
    def __init__(self, camera):
        self.cap = cv.VideoCapture(camera)
        # run `ffmpeg -f v4l2 -list_formats all -i /dev/video0` to check
        # list of available video modes
        resolutions = "1280x720"
        resolutions = [int(i) for i in "1280x720".split('x')]
        self.cap.set(cv.CAP_PROP_FRAME_WIDTH, resolutions[0])
        self.cap.set(cv.CAP_PROP_FRAME_HEIGHT, resolutions[1])

        _, self.frame = self.cap.read()
        self.processor = Processor(self.frame, "camera.yml")
        self.player = Play()
        cv.namedWindow('processed')
        self.rect_sel = RectSelector('processed', self.onrect)

        self.the_rect = 0, 0, self.processor.w, self.processor.h
        self.color = (128,255,255)

        self.start_play = False
        self.paused = False
        self.store = False
        self.end = False
        self.winner = None
        self.store_points = []
        self.store_radius = []
        self.location = tuple()

    def reset_store(self):
        self.store_points = []
        self.store_radius = []

    def onrect(self, rect):
        self.the_rect = rect
        print("select rect:", self.the_rect)
        self.reset_store()
        self.store = True

    def read_frame(self, timeout):
        start_time = time.time()
        while True:
            _, self.frame = self.cap.read()
            self.frame, tsps,tsrs = self.processor.centers_detect(self.frame.copy(),
                                self.the_rect, self.color, self.store)
            self.store_points.extend(tsps)
            self.store_radius.extend(tsrs)
            if (time.time() - start_time) > timeout:
                break

    def ai_play(self):
        self.read_frame(0.5)
        self.location, self.end, self.winner = self.player.game.play()
        print("AI move:", self.location)
        self.processor.store_coors.append(tuple(self.location))
        self.processor.grid(self.frame, self.store_points, self.store_radius, self.paused)

    def run(self):
        while True:
            if not self.start_play:
                self.read_frame(0)
                self.rect_sel.draw(self.frame)
            elif not self.paused:
                self.ai_play()

            cv.imshow("processed", self.frame)
            k = cv.waitKey(5) & 0xFF
            if k == 27:
                break
            if k == ord('p'):
                print(len(self.store_points))
            if k == ord('c'):
                print("clean store coordinates!")
                self.processor.store_coors = []
            if k == ord('s'):
                cv.imwrite('frame.png',self.frame)
                print("frame saved")

            if k == ord(' ') and self.store:
                self.start_play = True
                self.paused = not self.paused

                if self.paused:
                    self.ai_play()

                else:
                    durations = 1.4
                    while True:
                        self.read_frame(durations)
                        ai_loc = self.processor.store_coors[-1]
                        self.processor.grid(self.frame, self.store_points, self.store_radius, self.paused)
                        location = self.processor.store_coors[-1]
                        if ai_loc != location:
                            location, self.end, winner = self.player.game.play(location)
                            print("Human move:", location)
                            break
                        print("Human not found,trying..")
                        durations += 0.3
                    self.reset_store()
                if self.end:
                    print("game end")
                    print("the winner is:", winner)
                    break

        cv.destroyAllWindows()

if __name__ == '__main__':
    try:
        camera = 0
    except:
        camera = 1
    App(camera).run()
