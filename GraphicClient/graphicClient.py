import tkinter as tk
import threading
from functools import partial

# this is for the color wheel generation:
from PIL import Image, ImageTk
import numpy as np
import colorsys

# this is the code that Tristan wrote to communicate to the lights
import sys
import os.path
sys.path.append(
os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

import Client.clientSocketNEW as clientSocket
import Client.configs as configs

IP = configs.server["ip"]
PORT = configs.server["port"]
USER = configs.login["user"]
TOKEN = configs.login["token"]


"""
The way I did this for minecraft was to just remake the buttons each time.
The way I should be doing it is by making pages, and having the pages show themselves.
We need a couple pages here:

Not connected page:
Reconnect Button

Main Pages:
On button
Off button
Brightness slider
	possible presets
Static button
Pattern button
Pattern Presets?

Color picker page:
pattern name
color picker
next button
previous button?

Int picker page
pattern name
int picker
next button
previous button?


the static button just has it set the static pattern
There are also variables for the current setting?
Presets for favorite patterns?
We need a way to set a pattern by automatically going through the required pages


save a bunch of files that each have a preset in them, but only show the preset if the name is one of the patterns sent to us or "static"?

what if I make the colorpicker/intpicker pages a class which I pass in the place to save it? so I just create a bunch of them for making a patern?
that way they save their states...
"""

colorWheelFilename = "colorwheel.png"
sliderImage = "slider.png"
colorWheelRadius = 100 # this is used to calculate the color that was clicked on. I may need to generate this depending on the size of the screen, but whatever...

class Page(tk.Frame):
	def __init__(self, *args, **kwargs):
		self.page_name = "default"
		tk.Frame.__init__(self, *args, **kwargs)
		self.active = False

	def show(self):
		#self.lift(aboveThis=None)
		self.lift()
		self.active = True

	def leave(self):
		self.active = False # the buttons should make sure to call this

class PatternPage(Page):
	def __init__(self, master, patternManager, patternPart):
		Page.__init__(self, master)
		# the pattern is a dictionary, patternPart is the key for what this page should be, and the values[key] is where we should store our value
		# values is essentially the dictionary that we send to the server
		self.patternManager = patternManager
		self.patternPart = patternPart
		# self.backButton = tk.Button(self, text = "Back", command = lambda : self.back())
		# self.nextButton = tk.Button(self, text = "Next", command = lambda : self.next_page())
		# self.prevButton = tk.Button(self, text = "Previous", command = lambda : self.prev_page())
		self.backButton = tk.Button(self, text = "Back", command = self.back)
		self.nextButton = tk.Button(self, text = "Next", command = self.next_page)
		self.prevButton = tk.Button(self, text = "Previous", command = self.prev_page)
		# these get placed into the grid in the creation of the sub class
		self.final_page = False
		self.page_name = "Default Pattern Page"

	def next_page(self):
		self.leave()
		self.patternManager.send_current_pattern() # send the pattern upon exit of the current page
		self.right_page.show()
		if (self.final_page):
			self.main_page.destroy_pages()

	def prev_page(self):
		self.leave()
		self.patternManager.send_current_pattern() # send the pattern upon exit of the current page
		self.left_page.show()

	def back(self):
		self.leave()
		self.main_page.show()
		self.main_page.destroy_pages()

	def set_neighbor_pages(self, main_page, left_page = None, right_page = None, final_page = False):
		self.final_page = final_page
		self.main_page = main_page
		self.right_page = right_page
		self.left_page = left_page
		# I should set the buttons for swapping here too probably, they've already been created, so it's just a matter of setting them active or not I guess...
		if (not left_page): # if there are no pages next door, then don't have the buttons visible
			self.prevButton.pack_forget()
			self.prevButton.grid_remove()
		if (not right_page and not final_page):
			self.nextButton.pack_forget()
			self.nextButton.grid_remove()
		if (final_page):
			self.right_page = self.main_page
			self.nextButton["text"] = "Done"

class ColorPicker(PatternPage):
	def __init__(self, master, patternManager, patternPart, startingValue = {"h" : 0, "s" : 0, "v" : 255}):
		# pass in a starting value if you're using a preset or if you've recieved an update from the server
		PatternPage.__init__(self, master, patternManager, patternPart)

		self.selectedColor = startingValue
		self._prevColor = startingValue # this is used so that it doesn't update the color tooo frequently
		self.colorDistanceUpdate = 0 # if the distance between color vectors is greater than this, update (also update if it's forced to)

		self.master = master
		self.page_name = "Color Picker"

		label = tk.Label(self, text="Color Picker")
		label.grid(column = 1)
		tk.Label(self, text = "test").grid(column = 1)

		self.colorWheelImage = ImageTk.PhotoImage(Image.open(colorWheelFilename))

		self.valueSlider = tk.Scale(self, from_=0, to=255, orient = tk.HORIZONTAL, length = 200)
		self.valueSlider.grid(row = 3, column = 0, columnspan = 3)

		self.selectionRadius = 5
		self.canvasWidth = 250
		self.canvasHeight = 250
		self.create_canvas()
		self.set_color_selection(startingValue)

		self.backButton.grid(row = 0, column = 0)
		self.nextButton.grid(row = 2, column = 2, sticky = "e")
		self.prevButton.grid(row = 2, column = 0)

		self.master.bind("<Button 1>", self.handle_mouse_down)
		self.master.bind("<B1-Motion>", self.handle_mouse_drag)

	def create_canvas(self):
		# this creates the initial canvas
		self.canvas = tk.Canvas(self, width = self.canvasWidth, height = self.canvasHeight)
		#self.canvas.create_rectangle(2, 2, self.canvasWidth-2, self.canvasHeight-2)
		self.imageID = self.canvas.create_image((self.canvasWidth/2, self.canvasHeight/2), image = self.colorWheelImage)
		self.imageCoords = self.canvas.coords(self.imageID)
		self.canvas.grid(column = 1, row = 1)

	def set_color_selection(self, color):
		# color is 0-255 for h, s and v
		self.canvas.delete("selection") # remove the old selection
		h = color["h"]
		s = color["s"]
		v = color["v"]
		self.valueSlider.set(v)
		angle = h/255*2*np.pi
		radius = s/255*colorWheelRadius
		circlePos = (self.imageCoords[0] + np.cos(angle)*radius, self.imageCoords[1] + np.sin(angle)*radius)
		self.canvas.create_oval((circlePos[0]-self.selectionRadius, circlePos[1]-self.selectionRadius, circlePos[0]+self.selectionRadius, circlePos[1]+self.selectionRadius), tags = "selection")

	def handle_mouse_down(self, coords):
		# if this is active, and the mouse press is close to the circle, then set the color, and set the selection
		if (not self.active):
			return # if this page isn't active, it shouldn't do anything obviously
		dx = coords.x - self.imageCoords[0]
		dy = coords.y - self.imageCoords[1]
		currRadius = np.sqrt(dx*dx+dy*dy)
		#print(currRadius, colorWheelRadius)
		if (currRadius < colorWheelRadius):
			# then it's within the circle, so find what color they picked
			h = (np.arctan2(-dy, -dx)+np.pi)/2/np.pi*255
			s = currRadius / colorWheelRadius * 255
			v = self.valueSlider.get() # the current brightness for that
			self.selectedColor = {"h":int(h), "s":int(s), "v":int(v)}
			self.set_color_selection(self.selectedColor)
			self.update_values()
		elif (self.valueSlider.get() != self.selectedColor["v"]):
			self.selectedColor["v"] = self.valueSlider.get();
			#print("updated slider values")
			self.update_values()

	def handle_mouse_up(self, coords):
		if (self.active):
			# force update the lights to this color
			self.update_values(True)

	def update_values(self, forceUpdate = False):
		# update the lights if it's a big enough change?
		dh = self.selectedColor["h"] - self._prevColor["h"]
		ds = self.selectedColor["s"] - self._prevColor["s"]
		dv = self.selectedColor["v"] - self._prevColor["v"]
		self.distance = np.sqrt(dh*dh + ds*ds + dv*dv)
		self._prevColor = {"h":self.selectedColor["h"], "s":self.selectedColor["s"], "v":self.selectedColor["v"]}

		# set the value in the pattern manager
		self.patternManager.current_values[self.patternPart["key"]] = self.selectedColor
		if forceUpdate or self.distance > self.colorDistanceUpdate:
			# force update
			#print("Sending")
			self.patternManager.send_current_pattern()

	def handle_mouse_drag(self, coords):
		# then move the thing unless it's no longer in the radius
		self.handle_mouse_down(coords)

class NumberPicker(PatternPage):
	def __init__(self, master, patternManager, patternPart, startingValue = 0):
		PatternPage.__init__(self, master, patternManager, patternPart)
		pageName = patternPart["display_name"] or patternPart["key"] # try to use the display name, but if that isn't given use the key instead, which should be kinda descriptive
		pageLabel = tk.Label(self, text=pageName)
		pageLabel.pack(side="top", fill="both", expand=True)
		# do other things too, like make buttons
		self.patternPart = patternPart
		self.value = startingValue
		self.page_name = "Number Picker"



class MainPage(PatternPage):
	def __init__(self, master, patternManager, patternPart, startingValue = None):
		PatternPage.__init__(self, master, patternManager, patternPart)
		label = tk.Label(self, text="Main Page")
		label.pack(side="top", fill="both", expand=False)
		# this deals with setting patterns and a bunch of other shit. Hopefully...
		# we have some leftovers from the fact that we are a pattern page, but we can ignore/destroy them
		staticButton = tk.Button(self, text="Set Color", command = lambda : self.set_pattern(self.patternManager.solid_pattern))
		staticButton.pack()
		onButton = tk.Button(self, text = "Brightness 100%", command = self.on_button)
		onButton.pack()
		offButton = tk.Button(self, text = "Brightness 0%", command = self.off_button)
		offButton.pack()
		self.brightness = tk.IntVar()
		self.brightness.set(255)
		self.brightness.trace("w", self.update_brightness)
		self.oldBrightness = 255 # when I eventually get sent the brightness and whatever, then I'll need to set this. For now just exist I guess...
		self.brightnessSlider = tk.Scale(self, from_=0, to=255, orient = tk.HORIZONTAL, length = 200, variable = self.brightness)
		self.brightnessSlider.pack()

		self.pages = []
		self.page_name = "Main Page"

		self.socket = patternManager.socket # need this for on and off and brightness buttons probably

	def set_pattern(self, pattern):
		self.destroy_pages()
		self.patternManager.set_pattern(pattern)
		self.pages = self.patternManager.make_current_pattern_pages()
		if (len(self.pages) > 0):
			self.leave()
			self.pages[0].show()

	def destroy_pages(self):
		for page in self.pages:
			# destroy it
			pass
		self.pages = []

	def update_brightness(self, one, two, three):
		#print(one, two, three)
		if self.brightness.get() != self.oldBrightness:
			#print("Sending brightness")
			self.oldBrightness = self.brightness.get()
			self.send_brightness()

	def send_brightness(self):
		self.socket.send({"mode":"brightness", "brightness":self.brightness.get()})

	def on_button(self):
		# for now just set brightness to 255
		self.brightness.set(255) # the trace should send it

	def off_button(self):
		# for now just set brightness to 0
		self.brightness.set(0) # the trace should send it


class MainView(tk.Frame): # this is the thing that has every page inside it.
	def __init__(self, master, socket):
		tk.Frame.__init__(self, master)
		container = tk.Frame(self) # this is used to make all of the pages the same size

		self.patternManager = PatternManager(master, container, socket)
		main_page = MainPage(master, self.patternManager, None)
		self.patternManager.set_main_page(main_page)

		buttonframe = tk.Frame(self)
		#buttonframe.pack(side="top", fill="x", expand=False)
		container.pack(side="top", fill="both", expand=True)

		#p1.place(in_=container, x=0, y=0, relwidth=1, relheight=1)
		#p2.place(in_=container, x=0, y=0, relwidth=1, relheight=1)
		main_page.place(in_=container, x=0, y=0, relwidth=1, relheight=1)
		main_page.show()


class PatternManager:
	def __init__(self, master, page_container, socket):
		self.socket = socket # takes in an already connected socket. Hopefully anyways. Otherwise this should be able to deal with it maybe?
		self.master = master
		self.main_page = None
		self.page_container = page_container

		# the default pattern is a solid color. This is available always. Other ones may be sent by the server
		self.solid_pattern = {"display_name": "Static",
						"default" : {"mode":"solidcolor", "color":{"h":0, "s":0, "v":255}},
						"command" : [{"key": "color", "display_name":"Color", "type":"color"}]}
		self.current_pattern = self.solid_pattern
		self.current_values = self.deepCopyValues(self.solid_pattern["default"])

		self.pageTypes = {"color":ColorPicker, "int":NumberPicker} # the page classes that can be created
		self.pattern_list = [] # we may not want to put the default pattern on the list of patterns, and have a shortcut instead...

	def set_main_page(self, main_page):
		self.main_page = main_page

	def set_pattern(self, pattern):
		# copies the defaults of the new pattern to the current values and sets the current pattern to pattern
		self.current_values = self.deepCopyValues(pattern["default"])
		self.current_pattern = pattern

	def send_current_pattern(self):
		self.socket.send(self.current_values)

	def make_current_pattern_pages(self):
		# makes the pages for the current patterns and sets them as active probably.
		pages = []
		for part in self.current_pattern["command"]:
			# make a new page depending on what type the page is
			if part["type"] in self.pageTypes:
				newPage = self.pageTypes[part["type"]](self.master, self, part, self.current_values[part["key"]])
				newPage.place(in_=self.page_container, x = 0, y = 0, relwidth = 1, relheight = 1)
				pages.append(newPage) # make the new page, and set the default value to the default value
			else:
				print("ERROR: UNABLE TO MAKE PAGE OF TYPE:", part["type"])

		for i in range(len(pages)):
			# set their neighboring pages:
			final_page = False
			left_page = None
			if (i > 0):
				left_page = pages[i-1]
			right_page = None
			if (i < len(pages)-1):
				right_page = pages[i+1]
			else:
				right_page = self.main_page
				final_page = True
			pages[i].set_neighbor_pages(self.main_page, left_page = left_page, right_page = right_page, final_page = final_page)

		return pages

	def deepCopyValues(self, values, base = {}):
		new = base
		if (type(base) == type([])):
			for v in values:
				if type(v) == type({}):
					new.append(self.deepCopyValues(v, {}))
				elif type(v) == type([]):
					new.append(self.deepCopyValues(v, []))
				else:
					new.append(v)
		elif (type(base) == type({})):
			for k, v in values.items():
				if type(v) == type({}):
					# add a dictionary
					new[k] = self.deepCopyValues(v, {})
				elif type(v) == type([]):
					# add a list
					new[k] = self.deepCopyValues(v, [])
				else:
					new[k] = v
		return new

# this is code just taken from Tristan to connect to the server
def connect(client):
    # logging.debug("Connecting...")
    client.connect(IP, PORT)
    # logging.debug("Authenticating...")
    client.authenticate(USER, TOKEN)
    # logging.debug("Verifying...")
    client.verifyConnected()
    # logging.info("Connected to server")
    return

def quit(root, client):
	# this gets called upon application closing
	print("Disconnecting")
	client.send({"mode":"disconnect"})
	root.destroy()


if __name__ == "__main__":
	socket = clientSocket.ClientSocket()
	connect(socket)

	root = tk.Tk()
	main = MainView(root, socket)
	main.pack(side="top", fill="both", expand=True)
	root.protocol("WM_DELETE_WINDOW", lambda : quit(root, socket))
	root.wm_geometry("400x400")
	if(len(sys.argv) == 2):
		# then make it full screen I guess
		root.attributes('-zoomed', True)  # This just maximizes it so we can see the window. It's nothing to do with fullscreen.
		root.attributes("-fullscreen", True)
		print("Launched in fullscreen")
	else:
		print("Give an arbitrary argument to launch in fullscreen on the RPI")
	root.mainloop()
