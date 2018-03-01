# #animated_color_wheel_1.py
# # >>>>>>>>>>>>>>>>>>>>>>>
# from Tkinter import *
# root = Tk()
# root.title("Animated Color Wheel")

# cw = 300                                      # canvas width
# ch = 300                                      # canvas height
# canvas_1 = Canvas(root, width=cw, height=ch, background="black")
# canvas_1.grid(row=0, column=1)                              
# cycle_period = 200

# redFl = 255.0
# greenFl = 0
# blueFl = 0
# kula = "#000000"

# arcStart = 89
# arcEnd = 90

# xCentr = 150
# yCentr = 160
# radius = 130
# circ = xCentr - radius, yCentr + radius, xCentr + radius, yCentr - \ radius

# # angular position markers, degrees
# A_ANG = 0
# B_ANG = 60
# C_ANG = 120
# D_ANG = 180
# E_ANG = 240
# F_ANG = 300
# #G_ANG = 1
# G_ANG = 359
# intervals...


from PIL import Image
import numpy as np
import colorsys

def make_wheel_image(width = 500, height = 500, radius = 250, bgColor = (255, 255, 255)):
	centerX = width/2
	centerY = height/2

	wheelArray = []
	for y in range(height):
		newRow = []
		for x in range(width):
			dx = x - centerX
			dy = y - centerY
			currRadius = np.sqrt(dx*dx + dy*dy)
			if currRadius < radius:
				# then make it a color
				angle = (np.arctan2(-dy, -dx)+np.pi)/np.pi/2
				newRow.append(hsv_to_rgb(angle, currRadius/radius, 1))
			else:
				newRow.append(bgColor)
		wheelArray.append(newRow)

	#wheelArray = [[(x*255/width, y*255/height, 255) for x in range(width)] for y in range(height)] # a 2d array
	wheelArray = np.array(wheelArray, dtype = "uint8")
	Image.fromarray(wheelArray).show()

	while True:
		x = 0 # to let the user see the photo


def hsv_to_rgb(h, s, v):
	return tuple(i*255 for i in colorsys.hsv_to_rgb(h, s, v))


if __name__ == "__main__":
	make_wheel_image()