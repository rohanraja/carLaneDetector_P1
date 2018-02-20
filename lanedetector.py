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


def detectLanes(img, params):

    blkrSize = params["blurKernalSize"]
    cht = params["cannyHT"]
    clt = params["cannyLT"]
    stage = params["outputStage"]


    hsv = getHSV(img)

    bMask = hsv[:,:,2] > params.get("bThresh", 200)

    if params["useBrightness"]:
        # gray = hsv[:,:,2]
        gray = bMask.astype(np.uint8)*255
    else:
        gray = grayscale(img)

    blur = gaussian_blur(gray, kernel_size=blkrSize)
       
    ht = cht
    lt = clt
    canny_edges = canny(blur, low_threshold=lt, high_threshold=ht)

    #hsv = getHSV(img)
    bMask = cv2.bitwise_and(img, img, mask=bMask.astype(np.uint8))
    bMask = cv2.cvtColor(bMask, cv2.COLOR_BGR2RGB)


    rho = 1 # distance resolution in pixels of the Hough grid
    theta = np.pi/180 # angular resolution in radians of the Hough grid
    threshold = params.get("hThresh", 10)
    min_line_length = params.get("hMinLineLen", 20)
    max_line_gap = params.get("hMaxLineGap", 1)

    # houghImg = hough_lines(canny_edges, rho, theta, threshold, min_line_length, max_line_gap)


    hLines = get_hough_lines(canny_edges, rho, theta, threshold, min_line_length, max_line_gap)
    houghImg = draw_hough_lines(canny_edges, hLines)



    lnValsLeft = []
    lnValsRight = []

    for l in hLines:
        ln = LineFromCVLine(l)
        if(ln.isValidLaneCandidate(params)):
                
            lnVal = (540 - max(ln.y1, ln.y2) , ln.length(), ln.slope, ln)
            if(ln.slope < 0):
                lnValsLeft.append(lnVal)
            else:
                lnValsRight.append(lnVal)

    lnValsLeft.sort(key=lambda x: x[0] + 1000/x[1])
    lnValsRight.sort(key=lambda x: x[0] + 1000/x[1])
    #pp.pprint(lnValsLeft)
    #pp.pprint(lnValsRight)

    leftLine = lnValsLeft[0][3]
    rightLine = lnValsRight[0][3]

    linedImg = np.zeros_like(gray)

    finalImg_rough = np.copy(img)

    curY = min(leftLine.y1, leftLine.y2, rightLine.y1, rightLine.y2, int(img.shape[0]/1.6))
    if "minY" not in params:
        params["minY"] = int(img.shape[0]/1.6) 
        # params["minY"] = curY

    delta = curY - params["minY"]
    lowestY = int(params["minY"] + int(0.05* float(delta)))
    params["minY"] = lowestY

    # if "minY" not in params:
    #     params["minY"] = int(img.shape[0]/1.5) 
    #
    # lowestY = min(leftLine.y1, leftLine.y2, rightLine.y1, rightLine.y2, params["minY"])
    # params["minY"] = lowestY


    # leftLine.extrapolate(finalImg_rough, lowestY, params)
    # rightLine.extrapolate(finalImg_rough, lowestY, params)
    #
    params["maskLineThickness"] = 15
    # leftLine.extrapolate(linedImg, lowestY, params)
    # rightLine.extrapolate(linedImg, lowestY, params)

    # actualLeft = processSingleLine(gray,img, leftLine, lowestY, params)
    # actualRight = processSingleLine(gray,img, rightLine, lowestY, params)

    oldVal = params.get("maskLineThickness", 12)
    params["maskLineThickness"] = 7
    # actualLeft.extrapolate(finalImg_rough, lowestY, params)
    # actualRight.extrapolate(finalImg_rough, lowestY, params)
    params["maskLineThickness"] = oldVal
    #
    # lineMask = cv2.bitwise_and(img, img, mask=linedImg)
    # lineMask = cv2.cvtColor(lineMask, cv2.COLOR_BGR2RGB)
    #
    # cnts = findContours(lineMask, params)
    # finalImg = np.copy(img)
    #
    # cv2.drawContours(finalImg, cnts, -1, (0,255,0), 3)


    
    smoothingRate = 0.3
    
    # leftLine = actualLeft
    # rightLine = actualRight

    lSlope = leftLine.slope
    lBias = leftLine.bias
    
    rSlope = rightLine.slope
    rBias = rightLine.bias
    
    curLine = [lSlope, lBias, rSlope, rBias]
    
    if "prevLines" not in params:
        params["prevLines"] = curLine
        
    prevLine = np.array(params["prevLines"])
    curLine = np.array(curLine)
    deltaLine = curLine - prevLine
    finalLine = prevLine + smoothingRate * deltaLine
    
    
    params["maskLineThickness"] = 11

    lLine = LineFromSlopeBias(finalLine[0], finalLine[1], lowestY, img.shape[0])
    lLine.draw(finalImg_rough, params)
    
    rLine = LineFromSlopeBias(finalLine[2], finalLine[3], lowestY, img.shape[0])
    rLine.draw(finalImg_rough, params)

    outpDict = {
            "final": finalImg_rough,
            "blur": blur,
            "gray": gray,
            "canny": canny_edges,
            "hsv": finalImg_rough,
            "brightness": hsv[:,:,2],
            "hue": hsv[:,:,1],
            "saturation": hsv[:,:,0],
            "bMask": bMask,
            "hough": houghImg,
            "linedImg": linedImg,

    }

    return outpDict[stage]
