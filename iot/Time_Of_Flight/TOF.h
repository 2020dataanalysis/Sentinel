//  Time Of Flight
//  Arduino VL53L1X distance & PIR Motion Sensors
//  https://raw.githubusercontent.com/sparkfun/SparkFun_VL53L1X_Arduino_Library/master/examples/Example1_ReadDistance/Example1_ReadDistance.ino
//  https://www.l33t.uk/wp-content/uploads/2020/05/vl53l1X_Circuit.png
//  https://www.l33t.uk/ebay/vl53l1x/
#include <ComponentObject.h>
#include <RangeSensor.h>
#include <SparkFun_VL53L1X.h>
#include <vl53l1x_class.h>
#include <vl53l1_error_codes.h>
//#define BH1750a 0x23

SFEVL53L1X distanceSensor;
String sv = "Sonic=";
int ld = 0;

void setup_TOF()
{
  Wire.begin();
  if (distanceSensor.begin() != 0) //Begin returns 0 on a good init
  {
    Serial.println("Sensor failed to begin. Please check wiring. Freezing...");
    while (1);
  }
  Serial.println("Sensor online!");
}

//    int d = get_TOF();

int get_TOF()
{
  distanceSensor.startRanging(); //Write configuration bytes to initiate measurement
  while (!distanceSensor.checkForDataReady())
  {
    delay(1);
  }
  int distance = distanceSensor.getDistance(); //Get the result of the measurement from the sensor
  distanceSensor.clearInterrupt();
  distanceSensor.stopRanging();

  float distanceInches = distance * 0.0393701;
  float distanceFeet = distanceInches / 12.0;

  return (int) distanceInches;
}
