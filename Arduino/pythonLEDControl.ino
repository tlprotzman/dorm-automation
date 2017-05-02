#include "FastLED.h"

bool listen(String& command);
void setColor();
void setBrightness();
bool setPixel();
void setStrip();
void getBrightness();
CRGB getColors();
unsigned getAudioMagnitude();

FASTLED_USING_NAMESPACE

#define LED_TYPE    WS2811
#define COLOR_ORDER GRB
#define DATA_PIN    6
#define NUM_LEDS    300
#define MAX_BRIGHTNESS  255
CRGB leds[NUM_LEDS];

const int sampleWindow = 50; // Sample window width in mS (50 mS = 20Hz)


void setup() {
    FastLED.addLeds<LED_TYPE,DATA_PIN,COLOR_ORDER>(leds, NUM_LEDS).setCorrection(TypicalLEDStrip);
    Serial.begin(9600);
    Serial.println("Serial port open, listening...");
}

void loop() {
    String command;
    while (!listen(command)) {}
    if (command == "SETCOLOR")
        setColor();
    else if (command == "SETBRIGHTNESS")
        setBrightness();
    else if (command == "SETPIXELSHOW") {
        setPixel();
        FastLED.show();
    }
    else if (command == "SETSTRIP") {
        // unsigned avg[5];
        while (true) {
            FastLED.setBrightness(getAudioMagnitude());
            FastLED.show();
        //  for (unsigned i = 0; i < 5; i++) {
        //      avg[i] = getAudioMagnitude();
        //      unsigned sum;
        //      for (unsigned j = 0; j < 5; j++) {
        //          sum += avg[j];
        //      }
        //      FastLED.setBrightness(sum / 5);
        //      FastLED.show();
        //  }
        }
    }
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

bool setPixel() {
    String command;
    while (!listen(command)) {}
    if (command == "SHOW")
        return true;
    unsigned pixle = atoi(command.c_str());
    // Serial.println("Got pixel:");
    // while(!listen(command)) {}
    // unsigned h = atoi(command.substring(0, 3).c_str());
    // unsigned s = atoi(command.substring(3, 6).c_str());
    // unsigned v = atoi(command.substring(6, 9).c_str());
    // Serial.println('!');
    // Serial.println(h);
    // Serial.println(s);
    // Serial.println(v);
    CRGB color = getColors();
    
    leds[pixle] = color;
    return false;
}

void setStrip() {
    String command;
    while (!setPixel()) {}
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
    // Serial.println(str("Got color ")+str(colors[0])+str(colors[1])+str(colors[2]));
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

unsigned getAudioMagnitude() {
    unsigned long startMillis= millis();  // Start of sample window
    unsigned int peakToPeak = 0;   // peak-to-peak level
    
    unsigned int signalMax = 0;
    unsigned int signalMin = 1024;
    unsigned int sample;
    
    // collect data for 50 mS
    while (millis() - startMillis < sampleWindow) {
        sample = analogRead(0);
        if (sample < 1024) { // toss out spurious readings 
            if (sample > signalMax) {
                signalMax = sample;  // save just the max levels
            }
            else if (sample < signalMin) {
                signalMin = sample;  // save just the min levels
            }
        }
    }
    peakToPeak = signalMax - signalMin;  // max - min = peak-peak amplitude
    int value = map(peakToPeak, 0, 1023, 0, 255);  // convert to value
    Serial.println(value);
    value -= 30;
    if (value < 0)
        return 0;
    return value * 2;
}
