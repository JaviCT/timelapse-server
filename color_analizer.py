import cv2
import numpy as np
import os
import shutil
from skimage.measure import compare_ssim
import datetime

class ColorAnalyser():
    def compare_images(self, prevPath):
        score = 0
        if prevPath:
            imageA = cv2.imread(prevPath, 1)
            imageA = cv2.resize(imageA, (0,0), fx=0.1, fy=0.1)
            grayA = cv2.cvtColor(imageA, cv2.COLOR_BGR2GRAY)
            grayB = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)

            (score, diff) = compare_ssim(grayA, grayB, full=True)

        return score

    def clean_date(self):
        # c1 = 10
        # r1 = 10
        # img = self.img[c1:c1+25,r1:r1+25]
        # cv2.imshow("Image", img)

        # self.r = cv2.selectROI(self.img)
        # self.date = self.img[int(self.r[1]):int(self.r[1]+self.r[3]), int(self.r[0]):int(self.r[0]+self.r[2])]
        # self.we, self.he, self.channelsDate = self.date.shape
        # print("ROI", self.r)
        for y in range(0, self.he):
            for x in range(0, self.we):
                RGB = (self.date[x,y,2], self.date[x,y,1], self.date[x,y,0])
                if RGB[0] < 25 or RGB[1] < 25 or RGB[2] < 25 or RGB[0] > 220 or RGB[1] > 220 or RGB[2] > 220:
                    self.date[x,y] = RGB2
                else:
                    RGB2 = RGB
        x_offset=self.r[0]
        y_offset=self.r[1]
        self.img[y_offset:y_offset + self.date.shape[0], x_offset:x_offset + self.date.shape[1]] = self.date
        cv2.imshow('title',self.img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def count_colors(self):
        bgr = [20, 20, 20]
        thresh = 20

        minBGR = np.array([bgr[0] - thresh, bgr[1] - thresh, bgr[2] - thresh])
        maxBGR = np.array([bgr[0] + thresh, bgr[1] + thresh, bgr[2] + thresh])

        for y in range(0, self.h):
            for x in range(0, self.w):
                RGB = (self.img[x,y,2],self.img[x,y,1],self.img[x,y,0])
                if RGB[0] == RGB[1] == RGB[2]:
                    self.gray += 1
                else:
                    self.color += 1
                if RGB in self.colors_count:
                    self.colors_count[RGB] += 1
                else:
                    self.colors_count[RGB] = 1

        if self.color < 100:
            print("GRAY")
            self.black = 1

    def move(self):
        if os.path.exists(self.loc):
            s = self.loc.split("/")[-5:]
            print(s)
            name = get_time(s)
            dest = self.folder + "/" + str(name) + ".jpg"
            shutil.copy(self.loc, dest)

    def variance_of_laplacian(image):
        return cv2.Laplacian(image, cv2.CV_64F).var()

    def detect_blur(self, imageLoc, threshold):
        if os.path.exists(self.loc):
            img = cv2.imread(self.loc, 1)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            fm = self.variance_of_laplacian(gray)
            if fm > float(threshold):
                print(self.loc + " - Not Blurry: " + str(fm))
            if fm < float(threshold):
                print(self.loc + " - Blurry: " + str(fm))
                self.blur = 1

    def get_time(s):
        year = int(s[0])
        month = int(s[1])
        day = int(s[2])
        hour = int(s[3])
        s2 = s[4].split("_")
        minute = int(s2[0])
        second = int(s2[1])
        dt = datetime.datetime(year, month, day, hour, minute, second)
        seconds = dt.timestamp()
        return int(seconds)

    def main(self, imageLoc, prevPath, folder):
        image = cv2.imread(imageLoc, 1)
        self.img = cv2.resize(image, (0,0), fx=0.1, fy=0.1)
        self.colors_count = {}
        self.w, self.h, self.channels = self.img.shape
        self.total_pixels = self.w*self.h
        self.color = 0
        self.gray = 0
        self.loc = imageLoc
        self.percentage_of_first = 0
        self.blur = 0
        self.black = 0
        self.folder = folder
        if ((self.img == None).all()):
            print("No image data. Check image location for typos")
        else:
            self.count_colors()
        dif = self.compare_images(prevPath)
        if self.black == 0 and self.blur == 0 and dif < 0.95:
            # self.move()
            return True
        else:
            return False
