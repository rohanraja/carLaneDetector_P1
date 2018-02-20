from helpers import *
from Line import *

def findContours(image, params):
    blurred = cv2.GaussianBlur(image, (5, 5), 0)
    gray = cv2.cvtColor(blurred, cv2.COLOR_BGR2GRAY)
    hsv = getHSV(image)
    bMask = hsv[:,:,2] > params.get("bThresh", 200)
    gray = bMask.astype(np.uint8)*255
    thresh = cv2.threshold(gray, 160, 255, cv2.THRESH_BINARY)[1]

    # find contours in the thresholded image
    cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE)
    #cnts = cnts[0] if imutils.is_cv2() else cnts[1]
    return cnts[1]


def findCentroid(cnt):
    xSum = 0
    ySum = 0
    for pt in cnt:
        pt = pt[0]
        xSum += pt[0]
        ySum += pt[1]
        
    return int(xSum/len(cnt)) , int(ySum/len(cnt))
    
    M = cv2.moments(cnt)
    cx = int(M['m10']/M['m00'])
    cy = int(M['m01']/M['m00'])
    return (cx, cy)

def processSingleLine(gray2, img2, approxLine, lowestY, params):
    linedImg2 = np.zeros_like(gray2)
    #print(linedImg2.shape, img2.shape)
    approxLine.extrapolate(linedImg2, lowestY, params)
    lineMask = cv2.bitwise_and(img2, img2, mask=linedImg2)
    lineMask = cv2.cvtColor(lineMask, cv2.COLOR_BGR2RGB)
    cnts = findContours(lineMask, params)
    if len(cnts) == 1:
        cntroid = findCentroid(cnts[0])
        x1 = cntroid[0] - 15
        y1 = cntroid[1]
        x2 = cntroid[0] + 15
        y2 = cntroid[1]

        cv2.line(linedImg2, (x1, y1) , (x2,y2), color = 0, thickness=10)
        lineMask = cv2.bitwise_and(img2, img2, mask=linedImg2)
        lineMask = cv2.cvtColor(lineMask, cv2.COLOR_BGR2RGB)
        cnts = findContours(lineMask, params)

        assert len(cnts) > 1

    xs = []
    ys = []
    Vals = []

    for cnt in cnts:
        cd = findCentroid(cnt)
        val = (cv2.contourArea(cnt), cd)
        Vals.append(val)
        
        xs.append(cd[0])
        ys.append(cd[1])
        #cv2.circle(outP,(cd[0], cd[1]), 5, (255,0,0), -1)
    
    Vals.sort(key=lambda x: x[0])
    l = Line(Vals[-1][1][0], Vals[-1][1][1], Vals[-2][1][0], Vals[-2][1][1] )
    return l

    def solveForX(z, y):
        return (y - z[1]) / z[0] 

    z1 = np.polyfit(xs, ys, 1)

    lowX = solveForX(z1, img2.shape[0])
    highX = solveForX(z1, int(img2.shape[0]/1.6))

    l = Line(lowX, img2.shape[0], highX, int(img2.shape[0]/1.6))
    
    return l


