from helpers import *
from Line import *

def detectLanes(img, params):

    # Find HSV color space image
    hsv = getHSV(img)


    # Filter pixels based on the Variance value
    bMask = hsv[:,:,2] > params.get("bThresh", 200)
    if params["useBrightness"]:
        gray = bMask.astype(np.uint8)*255
    else:
        gray = grayscale(img)


    # Apply gaussian blur
    blkrSize = params["blurKernalSize"]
    blur = gaussian_blur(gray, kernel_size=blkrSize)
       

    # Find Canny Edges from blurred filtered image
    ht = params["cannyHT"]
    lt = params["cannyLT"]
    canny_edges = canny(blur, low_threshold=lt, high_threshold=ht)


    # Find hough lines from canny edges
    rho = 1 
    theta = np.pi/180 
    threshold = params.get("hThresh", 10)
    min_line_length = params.get("hMinLineLen", 20)
    max_line_gap = params.get("hMaxLineGap", 1)
    hLines = get_hough_lines(canny_edges, rho, theta, threshold, min_line_length, max_line_gap)
    houghImg = draw_hough_lines(canny_edges, hLines)


    # Find single best estimate line representing each lane
    lnValsLeft = []
    lnValsRight = []

    for l in hLines:
        ln = LineFromCVLine(l)
        if(ln.isValidLaneCandidate(params)):
                
            lnVal = (img.shape[0] - max(ln.y1, ln.y2) , ln.length(), ln.slope, ln)
            if(ln.slope < 0):
                lnValsLeft.append(lnVal)
            else:
                lnValsRight.append(lnVal)

    lnValsLeft.sort(key=lambda x: x[0] + 1000/x[1])
    lnValsRight.sort(key=lambda x: x[0] + 1000/x[1])
    leftLine, rightLine = lnValsLeft[0][3], lnValsRight[0][3]


    # Finding the maximium height upto which to extrapolate the lines
    curY = min(leftLine.y1, leftLine.y2, rightLine.y1, rightLine.y2, int(img.shape[0]/1.6))
    if "minY" not in params:
        params["minY"] = int(img.shape[0]/1.6) 
    delta = curY - params["minY"]
    lowestY = int(params["minY"] + int(0.05* float(delta)))
    params["minY"] = lowestY


    # Smoothing the slope and bias of the new lines so that no drastic deviations in the
    # detected lines are visible
    smoothingRate = 0.3
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
    
    
    # Extrapolate lines and draw the lines to generate annotated image
    finalImg_rough = np.copy(img)
    params["maskLineThickness"] = 11
    lLine = LineFromSlopeBias(finalLine[0], finalLine[1], lowestY, img.shape[0])
    lLine.draw(finalImg_rough, params)
    rLine = LineFromSlopeBias(finalLine[2], finalLine[3], lowestY, img.shape[0])
    rLine.draw(finalImg_rough, params)


    # Select the output stage to return (for testing purposes only)
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

    }

    stage = params["outputStage"]
    return outpDict[stage]
