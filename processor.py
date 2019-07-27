import cv2 as cv
import numpy as np
import pickle
THRS1, THRS2 = pickle.load(open("config.pkl", 'rb'))

class Processor:
    def __init__(self, img, yml_file_name):
        self.store_coors = []
        fs = cv.FileStorage(cv.samples.findFile(yml_file_name), cv.FILE_STORAGE_READ)
        self.camera_matrix = fs.getNode('camera_matrix').mat()
        self.dist_coefs = fs.getNode('distortion_coefficients').mat()
        self.h, self.w = img.shape[:2]

        self.retina = cv.bioinspired_Retina.create((img.shape[1], img.shape[0]))
        self.retina.write('retinaParams.xml')
        self.retina.setup('retinaParams.xml')

        self.newcameramtx, (self.x, self.y, self._w, self._h) = cv.getOptimalNewCameraMatrix(
                    self.camera_matrix, self.dist_coefs, (self.w, self.h), 1, (self.w, self.h))

    def undistorted(self, img):
        dst = cv.undistort(img, self.camera_matrix, self.dist_coefs, None, self.newcameramtx)
        dst = dst[self.y:self.y+self._h, self.x:self.x+self._w]
        return img

    def base_proc(self, img):
        self.retina.run(img)
        img = self.retina.getParvo()

        img = self.undistorted(img)
        img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
        img = cv.GaussianBlur(img, (5, 5), 0)
        canny_output = cv.Canny(img, THRS1, THRS2, apertureSize=5)
        contours, _ = cv.findContours(canny_output,
                            cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
        centers = [None]*len(contours)
        radius = [None]*len(contours)
        for i, c in enumerate(contours):
            # centers[i], radius[i] = cv.minEnclosingCircle(cv.approxPolyDP(c, 3, True))
            x,y,w,h = cv.boundingRect(c)
            # cv.rectangle(circles,(x,y),(x+w,y+h),(0,255,0),2)
            centers[i] = x+w/2, y+h/2
            radius[i] = (w if w<h else h)/2
        return contours, centers, radius


    def is_in_rect(self, x, y, rect):
        return (x > rect[0]) and ( x < rect[2]) and (y > rect[1]) and (y < rect[3])

    def centers_detect(self, vis, the_rect, color, store):
        store_points = []
        store_radius = []
        cnts,centers,radius = self.base_proc(vis)
        for i in range(len(cnts)):
            cX, cY = int(centers[i][0]), int(centers[i][1])
            if self.is_in_rect(cX, cY, the_rect):
                cv.circle(vis, (cX, cY), int(radius[i]), color, -1)

                if store:
                    store_points.append([cX, cY])
                    store_radius.append(radius[i])
        return vis, store_points, store_radius

    def line_clustering(self, centers, orien):
        if orien=="col":
            orien = 0
        elif orien=="row":
            orien = 1
        lines = np.float32([(p[orien], 0) for (i,p) in enumerate(centers)])
        _, line_labels, _ = cv.kmeans(lines, 8, None, (cv.TERM_CRITERIA_EPS, 40, 1), 15, cv.KMEANS_PP_CENTERS)

        line_labels = line_labels.ravel()
        lines = lines[:,0].ravel()
        first_values_ind = np.argsort(np.int64([lines[np.argwhere(line_labels==i)[0]][0] for i in range(8)]))
        return first_values_ind, line_labels

    def coordinate(self, id, row_ind, row_labels, col_ind, col_labels):
        return int(np.where(row_ind==row_labels[id])[0]), int(np.where(col_ind==col_labels[id])[0])

    def grid(self, img, points, radius, paused):
        points = np.float32(points)
        radius = np.float32(radius)
        _, labels, centers = cv.kmeans(points, 64, None, (cv.TERM_CRITERIA_EPS, 40, 1), 15, cv.KMEANS_PP_CENTERS)

        labels = labels.ravel()
        radius = np.float32([np.mean(radius[np.argwhere(labels==i).ravel()]) for i in range(64)])

        col_ind, col_labels = self.line_clustering(centers, "col")
        row_ind, row_labels = self.line_clustering(centers, "row")

        sample_radius = np.float32([(i,0) for i in radius])

        _,srlabels,_ = cv.kmeans(sample_radius, 2, None, (cv.TERM_CRITERIA_EPS, 15, 1), 15, cv.KMEANS_PP_CENTERS)
        srlabels = srlabels.ravel()

        sample = [radius[np.argwhere(srlabels==i)[0]][0] for i in range(2)]
        diff_pieces = sample[1] - sample[0] > 2

        for (id,p) in enumerate(centers):
            coor = self.coordinate(id, row_ind, row_labels, col_ind, col_labels)

            if diff_pieces and srlabels[id]==1:
                if coor not in self.store_coors:
                    print("human:", coor)
                    self.store_coors.append(coor)
                textcolor = (0,255,0)
            else:
                if coor in self.store_coors:
                    textcolor = (0,0,0)
                else:
                    textcolor = (255,0,0)
            cv.putText(img,str(coor), tuple(p), cv.FONT_HERSHEY_PLAIN, 0.8, textcolor, thickness = 1)
        return img
