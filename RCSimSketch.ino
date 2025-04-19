
// -----------------------------------------------------------------------------
// Project Name: Racing Simulator-RC Controller
// Author: bitsbits [https://www.youtube.com/@bits-bits]
// License: Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0)
// 
// You are free to use, modify, and share this code for non-commercial purposes,
// provided you credit the original author. Commercial use of this code or any
// derivatives is not permitted without explicit permission.
// 
// For full license details, see: https://creativecommons.org/licenses/by-nc/4.0/
// -----------------------------------------------------------------------------

#include <Wire.h>
#include <Adafruit_MCP4728.h>

// Create the MCP4728 object
Adafruit_MCP4728 mcp;
Adafruit_MCP4728 mcp2;

void setup() {
  // Start serial communication
  Serial.begin(115200);

  // Start I2C communication at 400kHz
  Wire.begin();
  Wire.setClock(400000); // Set I2C clock to 400kHz

  // Initialize the MCP4728 DAC
  if (!mcp.begin(0x60)) {
    Serial.println("Failed to find MCP4728 chip");
    while (1);
  }

  // Initialize the second MCP4728 DAC (0x61)
  if (!mcp2.begin(0x61)) {
    Serial.println("Failed to find MCP4728 chip at 0x61");
    while (1);
  }

  // Set the reference voltage for all channels to the external reference (VDD)
  mcp.setChannelValue(MCP4728_CHANNEL_A, 0, MCP4728_VREF_VDD, MCP4728_GAIN_1X);
  mcp.setChannelValue(MCP4728_CHANNEL_B, 0, MCP4728_VREF_VDD, MCP4728_GAIN_1X);
  mcp.setChannelValue(MCP4728_CHANNEL_C, 0, MCP4728_VREF_VDD, MCP4728_GAIN_1X);
  mcp.setChannelValue(MCP4728_CHANNEL_D, 0, MCP4728_VREF_VDD, MCP4728_GAIN_1X);

  mcp2.setChannelValue(MCP4728_CHANNEL_A, 0, MCP4728_VREF_VDD, MCP4728_GAIN_1X);
  mcp2.setChannelValue(MCP4728_CHANNEL_B, 0, MCP4728_VREF_VDD, MCP4728_GAIN_1X);
  mcp2.setChannelValue(MCP4728_CHANNEL_C, 0, MCP4728_VREF_VDD, MCP4728_GAIN_1X);
  mcp2.setChannelValue(MCP4728_CHANNEL_D, 0, MCP4728_VREF_VDD, MCP4728_GAIN_1X); 

  // Set up switch pins
  pinMode(14, OUTPUT); // swE
  pinMode(15, OUTPUT);
  
  pinMode(10, OUTPUT); // swB
  pinMode(16, OUTPUT);

  pinMode(7, OUTPUT); // swF
  pinMode(6, OUTPUT);

  pinMode(5, OUTPUT); // swC
  pinMode(4, OUTPUT);
  
  pinMode(21, OUTPUT); // leftpaddle - Air brake
  pinMode(8, OUTPUT);  // rightpaddle - Launch Button

  Serial.println("MCP4728 initialized");
}

void loop() {
  // Check if data is available to read
  if (Serial.available() > 0) {
    // Read the serial input
    String input = Serial.readStringUntil('\n');

    // Split the input string by commas
    int commaIndex1 = input.indexOf(',');
    int commaIndex2 = input.indexOf(',', commaIndex1 + 1);
    int commaIndex3 = input.indexOf(',', commaIndex2 + 1);
    int commaIndex4 = input.indexOf(',', commaIndex3 + 1);
    int commaIndex5 = input.indexOf(',', commaIndex4 + 1);
    int commaIndex6 = input.indexOf(',', commaIndex5 + 1);
    int commaIndex7 = input.indexOf(',', commaIndex6 + 1);
    int commaIndex8 = input.indexOf(',', commaIndex7 + 1);
    int commaIndex9 = input.indexOf(',', commaIndex8 + 1);
    int commaIndex10 = input.indexOf(',', commaIndex9 + 1);
    int commaIndex11 = input.indexOf(',', commaIndex10 + 1);

    int xAxis = input.substring(0, commaIndex1).toInt();
    int yAxis = input.substring(commaIndex1 + 1, commaIndex2).toInt();
    int zAxis = input.substring(commaIndex2 + 1, commaIndex3).toInt();
    int cAxis = input.substring(commaIndex3 + 1, commaIndex4).toInt();
    int leftpaddle = input.substring(commaIndex4 + 1, commaIndex5).toInt();
    int rightpaddle = input.substring(commaIndex5 + 1, commaIndex6).toInt();
    int left_pot = input.substring(commaIndex6 + 1, commaIndex7).toInt();
    int right_pot = input.substring(commaIndex7 + 1).toInt();
    int swE_position = input.substring(commaIndex8 + 1, commaIndex9).toInt();
    int swB_position = input.substring(commaIndex9 + 1, commaIndex10).toInt();
    int swC_position = input.substring(commaIndex10 + 1, commaIndex11).toInt();
    int swF_position = input.substring(commaIndex11 + 1).toInt();

    // Map the axis values (-1000 to 1000) to DAC output values (0 to 4095)
    int xDacValue = map(xAxis, -1000, 1000, 0, 4095);
    int yDacValue = map(yAxis, -1000, 1000, 0, 4095);
    int zDacValue = map(zAxis, 1000, -1000, 0, 4095);
    int cDacValue = map(cAxis, -1000, 1000, 0, 4095);
    int leftDacValue = map(left_pot, -1000, 1000, 0, 4095);
    int rightDacValue = map(right_pot, -1000, 1000, 0, 4095);

    // Set the DAC output values for channels A, B, C, and D
    mcp.setChannelValue(MCP4728_CHANNEL_A, xDacValue, MCP4728_VREF_VDD, MCP4728_GAIN_1X);
    mcp.setChannelValue(MCP4728_CHANNEL_B, yDacValue, MCP4728_VREF_VDD, MCP4728_GAIN_1X);
    mcp.setChannelValue(MCP4728_CHANNEL_C, zDacValue, MCP4728_VREF_VDD, MCP4728_GAIN_1X);
    mcp.setChannelValue(MCP4728_CHANNEL_D, cDacValue, MCP4728_VREF_VDD, MCP4728_GAIN_1X);
    mcp2.setChannelValue(MCP4728_CHANNEL_A, rightDacValue, MCP4728_VREF_VDD, MCP4728_GAIN_1X);
    mcp2.setChannelValue(MCP4728_CHANNEL_B, leftDacValue, MCP4728_VREF_VDD, MCP4728_GAIN_1X);
    mcp2.setChannelValue(MCP4728_CHANNEL_C, 0, MCP4728_VREF_VDD, MCP4728_GAIN_1X);
    mcp2.setChannelValue(MCP4728_CHANNEL_D, 0, MCP4728_VREF_VDD, MCP4728_GAIN_1X);

    // Handle switches (swE, swB, swC, swF) and paddles
    if (swE_position == 1) {
    digitalWrite(14, HIGH); // UP
    digitalWrite(15, LOW);
} else if (swE_position == 0) {  // Explicitly check for neutral (0)
    digitalWrite(14, HIGH);  // NEUTRAL state
    digitalWrite(15, HIGH);
} else if (swE_position == -1) {
    digitalWrite(14, LOW);
    digitalWrite(15, HIGH); // DOWN

}
    if (swB_position == 1) {
    digitalWrite(10, LOW); // UP
    digitalWrite(16, HIGH);
} else if (swB_position == 0) {  // Explicitly check for neutral (0)
    digitalWrite(10, HIGH);  // NEUTRAL state
    digitalWrite(16, HIGH);
} else if (swB_position == -1) {
    digitalWrite(10, HIGH);
    digitalWrite(16, LOW); // DOWN

}
    if (swF_position == 1) {
    digitalWrite(7, LOW); // UP
    digitalWrite(6, HIGH);
} else if (swF_position == 0) {  // Explicitly check for neutral (0)
    digitalWrite(7, HIGH);  // NEUTRAL state
    digitalWrite(6, HIGH);
} else if (swF_position == -1) {
    digitalWrite(7, HIGH);
    digitalWrite(6, LOW); // DOWN

}

    if (swC_position == 1) {
    digitalWrite(4, LOW); // UP
    digitalWrite(5, HIGH);
} else if (swC_position == 0) {  // Explicitly check for neutral (0)
    digitalWrite(4, HIGH);  // NEUTRAL state
    digitalWrite(5, HIGH);
} else if (swC_position == -1) {
    digitalWrite(4, HIGH);
    digitalWrite(5, LOW); // DOWN

}

    // Handle momentary switches (paddles)
    digitalWrite(21, (leftpaddle == 1) ? LOW : HIGH); // left paddle - Air brake
    digitalWrite(8, (rightpaddle == 1) ? LOW : HIGH);  // rightpaddle - Launch button
  }
}
