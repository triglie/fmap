///
/// \file ScanRadio.ino
/// \brief This sketch implements a scanner that lists all availabe radio stations including some information.
///
/// \author Matthias Hertel, http://www.mathertel.de
/// \copyright Copyright (c) by Matthias Hertel.\n
/// This work is licensed under a BSD 3-Clause license.\n
/// See http://www.mathertel.de/License.aspx
///
/// \details
/// This is a Arduino sketch that uses a state machine to scan through all radio stations the radio chip can detect
/// and outputs them on the Serial interface.\n
/// Open the Serial console with 115200 baud to see current radio information and change various settings.
///
/// Wiring
/// ------
/// The necessary wiring of the various chips are described in the Testxxx example sketches.
/// No additional components are required because all is done through the serial interface.
///
/// More documentation and source code is available at http://www.mathertel.de/Arduino
///
/// History:
/// --------
/// * 17.05.2015 created.
/// * 27.05.2015 first version is working (beta with SI4705).
/// * 04.07.2015 2 scan algorithms working with good results with SI4705.
/// * 18.09.2020 more RDS output, better command handling.

#include <Arduino.h>
#include <Wire.h>
#include <radio.h>
#include <SI4703.h>
#include <RDSParser.h>

SI4703 radio(52, 20);    ///< Create an instance of a SI4703 chip radio.

/// get a RDS parser
RDSParser rds;

uint16_t g_block1;
bool lowLevelDebug = false;
RADIO_FREQ frequency;
char province[128] = "Catania\0";
char coords[128] = "(37,5013; 15,0742)\0";


// - - - - - - - - - - - - - - - - - - - - - - - - - -


// use a function in between the radio chip and the RDS parser
// to catch the block1 value (used for sender identification)
void RDS_process(uint16_t block1, uint16_t block2, uint16_t block3, uint16_t block4) {
  g_block1 = block1;
  rds.processData(block1, block2, block3, block4);
}

/// Update the Time
void DisplayTime(uint8_t hour, uint8_t minute) {
  Serial.print("Time: ");
  if (hour < 10)
    Serial.print('0');
  Serial.print(hour);
  Serial.print(':');
  if (minute < 10)
    Serial.print('0');
  Serial.println(minute);
} // DisplayTime()


/// Update the ServiceName text on the LCD display.
void DisplayServiceName(char *name) {
  bool found = false;

  for (uint8_t n = 0; n < 8; n++)
    if (name[n] != ' ')
      found = true;

  if (found) {
    Serial.print("<SENDER>:");
    Serial.print(name);
    Serial.print('\n');
  }
} // DisplayServiceName()


/// Update the ServiceName text.
void DisplayText(char *txt) {
  Serial.print("<TEXT>:");
  Serial.print(txt);
  Serial.print('\n');
} // DisplayText()


/// Set the new frequency.
void setFrequency(RADIO_FREQ f) {
  radio.setFrequency(f);
  radio.resetRegisters();
  rds.init();
  delay(80);
} // setFrequency() 


/// Print frequency information.
char* printInfo() {
  char* info = (char *) malloc(sizeof(char) * 1024);
  char s[12];
  radio.formatFrequency(s, sizeof(s));
  sprintf(info, "province=%s coords=%s FM=%s RSSI=%s\0", province, coords, s, radio.debugRadioInfo());
  delay(1000);
  return info;
} // printInfo()


/// Check for RDS packet.
void checkRDS() {
  unsigned long startSeek;
  startSeek = millis(); // the time the delay started
  bool delayRunning = true; // true if still waiting for delay to finish
  while(true) {
    if (delayRunning && ((millis() - startSeek) >= 20000)) {
      delayRunning = false; // prevent this code being run more then once
      break;
    }
    radio.checkRDS();
  }
} // checkRDS()


/// Print Programme Identifier.
void printPICode(char* info) {
  sprintf(info, "%s PI=%x", info, g_block1);
  g_block1 = 0;
  Serial.println(info);
} // printPICode()


/// Scanning all frequency and get information about them.
void runScanning() {
  RADIO_FREQ fSave;
  RADIO_FREQ f = radio.getMinFrequency();
  RADIO_FREQ fMax = radio.getMaxFrequency();

  // ----- control the frequency -----
  fSave = radio.getFrequency();
  
  // start Simple Scan: all channels
  while (f <= fMax) {
    setFrequency(f);
    char* info = printInfo();
    checkRDS();
    f += radio.getFrequencyStep();
    printPICode(info);
    free(info);
  } // while
  radio.setFrequency(fSave);
  Serial.println();
} // runScanning()


/// Setup a FM only radio configuration with I/O.
void setup() {
  // open the Serial port
  Serial.begin(115200);
  delay(500);

#ifdef ESP8266
  // For ESP8266 boards (like NodeMCU) the I2C GPIO pins in use
  // need to be specified.
  Wire.begin(D2, D1); // a common GPIO pin setting for I2C
#endif

  // Enable information to the Serial port
  radio.debugEnable(false);
  radio._wireDebug(lowLevelDebug);

  // Initialize the Radio
  radio.init();

  frequency = 105100;
  radio.setBandFrequency(RADIO_BAND_FM, frequency);
  delay(100);

  radio.setMono(false);
  radio.setMute(false);
  radio.setVolume(10);

  delay(5000);

  // setup the information chain for RDS data.
  radio.attachReceiveRDS(RDS_process);
} // Setup


/// Constantly check for radio frequency.
void loop() {
  runScanning();
} // loop

// End.