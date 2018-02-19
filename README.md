# **Finding Lane Lines on the Road** 

---


## Reflection

### 1. Describe your pipeline. As part of the description, explain how you modified the draw_lines() function.

####Finding approximate 2-d lines equation corresponding to both the lanes:

1. Instead of using gray image, I converted the images to **HSV** format and picked up the *Variance* values for those pixels whose *Variance*/*Brightness* was more than approximately *200*. This reduced the image to mostly bright yellow and white colors, which usually belong to the lanes. This step reduced noisy pixels from the image.
![HSV Filter](writeup_images/hsvfilter.png "Applying HSV Variance filter")

2. In order to find **hough lines**, next step was to find the **canny edges** on the above reduced image after applying the **gaussian blur** filter.
![HSV Filter](writeup_images/hough.png "Finding Hough Lines")


3. The bunch of hough lines calculated in the previous step contained atleast one line corresponding to each lane. To find the line which best represented a lane:
	
	3.a) Firstly, I filterd all the lines based on the following criteria:
	1. The magnitude of the **slope** should be between approximate *30 degrees* to *60 degrees* (Experimentally determined values)
	2. The **length** of the line segment should be greator than *20 pixels*

	3.b) Secondly, I categorized all lines having **negative** slope to the left lane and **positive** slope to the right.
	
	3.c) Thirdly, for each lane side, I picked up one best estimate line by sorting all the candidate lines based on their **distance from the base line** of the image ( lines closer to the base preferred ) and based on the **length of the line segment** ( larger line length preferred ).   	





### 2. Identify potential shortcomings with your current pipeline


One potential shortcoming would be what would happen when ... 

Another shortcoming could be ...


### 3. Suggest possible improvements to your pipeline

A possible improvement would be to ...

Another potential improvement could be to ...
