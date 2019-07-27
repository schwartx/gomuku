import cv2 as cv
import numpy as np

import pickle
import sys


if __name__ == '__main__':
    try:
        fn = sys.argv[1]
    except:
        fn = 0

    def nothing(*arg):
        pass

    cv.namedWindow('edge')
    cv.createTrackbar('thrs1', 'edge', 2000, 5000, nothing)
    cv.createTrackbar('thrs2', 'edge', 4000, 5000, nothing)

    cap = cv.VideoCapture(fn)
    flag = False
    img = None
    while flag is False:
        flag, img = cap.read()
    retina = cv.bioinspired_Retina.create((img.shape[1], img.shape[0]))
    retina.write('retinaParams.xml')
    retina.setup('retinaParams.xml')
    # cap = cv.VideoCapture(0)
    while True:
        thrs1 = cv.getTrackbarPos('thrs1', 'edge')
        thrs2 = cv.getTrackbarPos('thrs2', 'edge')
        flag, img = cap.read()
        retina.run(img)
        img = retina.getParvo()
        circles = img.copy()
        gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
        gray = cv.GaussianBlur(gray, (5, 5), 0)
        # gray = cv.erode(gray, np.ones((5,5), np.uint8), iterations=1)
        edge = cv.Canny(gray, thrs1, thrs2, apertureSize=5)
        # edge = cv.dilate(edge, np.ones((5,5), np.uint8), iterations=1)
        contours, hier = cv.findContours(edge,
                            cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

        centers = [None]*len(contours)
        radius = [None]*len(contours)
        for i, c in enumerate(contours):
            # if hier is not None and hier[0][i][2] > -1:
            x,y,w,h = cv.boundingRect(c)
            cv.rectangle(circles,(x,y),(x+w,y+h),(0,255,0),2)
            centers[i] = x+w/2, y+h/2
            radius[i] = (w if w<h else h)/2# math.sqrt(math.pow(w/2, 2) + math.pow(h/2, 2))
            # eps = 0.5*cv.arcLength(c, True)
            # centers[i], radius[i] = cv.minEnclosingCircle(cv.approxPolyDP(c, eps, True))

        # for i in range(len(contours)):
            # if cv.isContourConvex(contours[i]):
            # if hier is not None and hier[0][i][2] > -1:
                # x,y,w,h = cv.boundingRect(contours[i])
                # cv.rectangle(circles,(x,y),(x+w,y+h),(0,255,0),2)
                # cX, cY = int(centers[i][0]), int(centers[i][1])
                # cX, cY = centers[i]
                # cv.circle(circles, (cX, cY), int(radius[i]), (0,255,0), -1)

        vis = img.copy()
        vis = np.uint8(vis/2.)
        vis[edge != 0] = (0, 255, 0)
        cv.imshow('edge', vis)
        cv.imshow('circle', circles)
        ch = cv.waitKey(5)
        if ch == 27:
            break
        elif ch == ord('s'):
            print('thrs1: %d, thrs2: %d' % (thrs1, thrs2))
            pickle.dump((thrs1, thrs2), open('config.pkl', 'wb'))
    cv.destroyAllWindows()
