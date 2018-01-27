from helpers import *

def detectLanes(img, params):

    blkrSize = params["blurKernalSize"]
    cht = params["cannyHT"]
    clt = params["cannyLT"]

    blur_gray = gaussian_blur(grayscale(img), kernel_size=blkrSize)
       
    ht = cht
    lt = clt
    canny_edges = canny(blur_gray, low_threshold=lt, high_threshold=ht)

    return canny_edges
