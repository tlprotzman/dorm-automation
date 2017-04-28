#include "FastLED.h"

bool listen(String& command);
void setColor();
void setBrightness();
void getBrightness();
CRGB getColors();
void setPixel();

FASTLED_USING_NAMESPACE

#define LED_TYPE 	WS2811
#define COLOR_ORDER	GRB
#define DATA_PIN	6
#define NUM_LEDS	300
#define MAX_BRIGHTNESS	255
CRGB leds[NUM_LEDS];

void setup() {
	FastLED.addLeds<LED_TYPE,DATA_PIN,COLOR_ORDER>(leds, NUM_LEDS).setCorrection(TypicalLEDStrip);
	Serial.begin(1000000);
	Serial.println("Serial port open, listening...");
}

void loop() {
	String command;
	while (!listen(command)) {}
	if (command == "SETCOLOR")
		setColor();
	else if (command == "SETBRIGHTNESS")
		setBrightness();
	else if (command == "SETPIXEL")
		setPixel();
}

void setColor() {
	CRGB color = getColors();
	Serial.println(color);
	fill_solid(leds, NUM_LEDS, color);
	FastLED.show();
}

void setBrightness() {
	String brightness;
	while(!listen(brightness)) {}
	unsigned newBrightness = atoi(brightness.c_str());
	if (newBrightness > 255)
		newBrightness = 255;
	FastLED.setBrightness(newBrightness);
	FastLED.show();
}


CRGB getColors() {
	uint8_t colors[3];
	for (unsigned i = 0; i < 3; i++) {
		String color;
		while (!listen(color)) {}
		unsigned currentColor = atoi(color.c_str());
		if (currentColor > 255)
			currentColor = 255;
		colors[i] = currentColor;
	}
	return CHSV(colors[0], colors[1], colors[2]);
}

bool listen(String& message) {
	String command;
	while (true) {
		int inByte = Serial.read();
		if (inByte == -1)
			continue;
		char inChar = (char)inByte;
		if (inChar == '~') {
			message = command;	
			return true;
		}
		command += inChar;
	}
}

void setPixel() {
	String command;
	while (!listen(command)) {}
	unsigned pixle = atoi(command.c_str());
	CRGB color = getColors();
	leds[pixle] = color;
	FastLED.show();
}


