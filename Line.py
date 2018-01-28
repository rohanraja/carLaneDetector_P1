import numpy as np
import cv2


def LineFromCVLine(l):
    return Line(l[0][0], l[0][1], l[0][2], l[0][3])

class Line:
    """
    A Line is defined from two points (x1, y1) and (x2, y2) as follows:
    y - y1 = (y2 - y1) / (x2 - x1) * (x - x1)
    Each line has its own slope and intercept (bias).
    """
    def __init__(self, x1, y1, x2, y2):

        self.x1 = np.float32(x1)
        self.y1 = np.float32(y1)
        self.x2 = np.float32(x2)
        self.y2 = np.float32(y2)

        self.slope = self.compute_slope()
        self.bias = self.compute_bias()

    def compute_slope(self):
        return (self.y2 - self.y1) / (self.x2 - self.x1 + np.finfo(float).eps)

    def compute_bias(self):
        return self.y1 - self.slope * self.x1

    def get_coords(self):
        return np.array([self.x1, self.y1, self.x2, self.y2])


    def distBetween(self, x1, x2, y1, y2):
        return ((x1 - x2)**2  + (y1 - y2)**2 )


    def distFromPoint(self, x, y):

        d1 = self.distBetween(x,self.x1,y,self.y1)
        d2 = self.distBetween(x,self.x2,y,self.y2)
        return np.sqrt(min(d1, d2))


    def length(self):
        return np.sqrt((self.x1 - self.x2)**2  + (self.y1 - self.y2)**2 )

    def set_coords(self, x1, y1, x2, y2):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2

    def isValidLaneCandidate(self, params={}):
        if self.length() < 20:
            return False

        if not (0.5 <= np.abs(self.slope) <= 2):
            return False

        return True

    def draw(self, img, color=[255, 0, 0], thickness=3):

        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.line(img, (self.x1, self.y1), (self.x2, self.y2), color, thickness)

        midPoint = (int((self.x1+self.x2)/2),int((self.y1+self.y2)/2 ))

        # cv2.putText(img,"%.2f"%self.slope, midPoint, cv2.FONT_HERSHEY_PLAIN, 2, (200,233,250), 2)


    def solveForY(self, x):
        return self.slope*x + self.bias

    def solveForX(self, y):
        return (y - self.bias)/self.slope

    def extrapolateTillBase(self, img, othLine, color=[255, 0, 0], thickness=3):

        lowx = self.x1
        lowy = self.y1
        highx = self.x2
        highy = self.y2

        if self.y2 > self.y1:
            lowx = self.x2
            lowy = self.y2
            highx = self.x1
            highy = self.y1

        baseY = img.shape[0]
        baseX = int(self.solveForX(baseY))

        midY = min(self.y1, self.y2, othLine.y1, othLine.y2)
        midX = int(self.solveForX(midY))

        cv2.line(img, (lowx, lowy), (baseX, baseY), color, thickness)

        cv2.line(img, (highx, highy), (midX, midY), color, thickness)

