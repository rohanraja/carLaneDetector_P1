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


    linedImg = np.zeros_like(gray)

    lnValsLeft[0][3].draw(linedImg)
    lnValsRight[0][3].draw(linedImg)
    lnValsLeft[0][3].extrapolateTillBase(linedImg,lnValsRight[0][3], params)
    lnValsRight[0][3].extrapolateTillBase(linedImg,lnValsLeft[0][3], params)


    lineMask = cv2.bitwise_and(img, img, mask=linedImg)
    lineMask = cv2.cvtColor(lineMask, cv2.COLOR_BGR2RGB)

    cnts = findContours(lineMask, params)
    finalImg = np.copy(img)
    cv2.drawContours(finalImg, cnts, -1, (0,255,0), 3)

    outpDict = {
            "final": finalImg,
            "blur": blur,
            "gray": gray,
            "canny": canny_edges,
            "hsv": hsv,
            "brightness": hsv[:,:,2],
            "hue": hsv[:,:,1],
            "saturation": hsv[:,:,0],
            "bMask": bMask,
            "hough": houghImg,

    }

    return outpDict[stage]
