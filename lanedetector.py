from helpers import *

def detectLanes(img, params):

    blkrSize = params["blurKernalSize"]
    cht = params["cannyHT"]
    clt = params["cannyLT"]
    stage = params["outputStage"]

    gray = grayscale(img)
    blur = gaussian_blur(gray, kernel_size=blkrSize)
       
    ht = cht
    lt = clt
    canny_edges = canny(blur, low_threshold=lt, high_threshold=ht)

    outpDict = {
            "final": canny_edges,
            "blur": blur,
            "gray": gray,
            "canny": canny_edges,
    }

    return outpDict[stage]
