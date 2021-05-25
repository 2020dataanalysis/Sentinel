//This project was a trip through insanity.
//When the PIR is not wired:
//  When not powered via USB the output is 0.
//  When powered via USB the output is 1.
//    Was only able to get this to function when not powered via USB.
//    Pins 1, 3, 15, 16, 25
//
//  Finally got this to work with pin 2 or 5.

//Sentinel Motion & Light Sensor
//Motion Sensor is a Panasonic EKMC7601111K
//https://www3.panasonic.biz/ac/e/control/sensor/human/cautions_use/index.jsp
//Light Sensor is a BH1750
//Signals upon triggers as well as upon command.
//  04/18/2021


#include <Arduino.h>
#include <M5Stack.h>
#include "BluetoothSerial.h"
#if !defined(CONFIG_BT_ENABLED) || !defined(CONFIG_BLUEDROID_ENABLED)
#error Bluetooth is not enabled! Please run `make menuconfig` to and enable it
#endif

#include <Wire.h>
#define Add_BH1750 0x23     // MOSI = pin 23

BluetoothSerial SerialBT;     //  Carriage return & linefeed is required.
String s;

void print(int, int, int, int, String);
boolean lcd = true;
boolean status;
String status$;
int PIR = 2;
String mv = "motion=";
String lv = "light=";

void setup() {
  if (lcd)
  {
    M5.begin();
    M5.Lcd.setTextSize(5);
    M5.Lcd.drawString("Hello", 10, 60, 4);
  }
  else
  {
    Serial.begin(115200);
    delay( 1000 );
  }

  Wire.begin();
  Wire.setClock( 400000L );
  SerialBT.begin("M5Stack Grey");

  Wire.beginTransmission( Add_BH1750 );
  Wire.write( 0x10 );
  Wire.endTransmission();
  delay( 1800 );

   pinMode(PIR, INPUT);
}


uint16_t lux;
uint16_t llux = -11;
int shade = 10;
bool motion;

void loop()
{
  if (SerialBT.available())
  {
    String s = SerialBT.readString();
    print( 5, 140, 6, 2000, s );

    if ( s.equals("motion") )
    {
        SerialBT.println( mv + motion );
    }

    if ( s.equals("light"))
    {
        SerialBT.println( lv + lux );
    }

    if ( s.equals("shade"))
    {
        String m = "shade=";
        SerialBT.println( m + shade );
    }

    if ( s.length() > 6 )
    {
        String m = s.substring(0, 6 );
        if ( m.equals("shade=") )
        {
            shade = s.substring(6, s.length() ).toInt();
            String shv = "set shade=" + String( shade );
//            String shv = "set shade=";    // Works
            Serial.println( shv );
            print( 5, 140, 6, 5000, shv );
        }
    }
  }


  motion = digitalRead(PIR);
  if( motion )
  {
    Serial.println("Presence Detected");
    print( 5, 5, 10, 500, "Motion" );
    SerialBT.println( mv + motion );
  }


  lux = luminosite();
  int d = abs( lux - llux );
  llux = lux;

  if ( d > shade )
  {
      SerialBT.println( lv + lux );
      Serial.println( lux );
  }
  s = String( lux );
  //String slux = s.substring(0, 4);
  print( 10, 50, 20, 500, s );
}



uint16_t luminosite(){
  uint16_t lux;
  Wire.requestFrom( Add_BH1750, 2 );
  while( Wire.available() )
  {
    lux = Wire.read();
    lux<<=8;
    lux = lux + Wire.read();
  }

  Wire.endTransmission();
  lux = lux / 1.2;
  return lux;
}



void print(int x, int y, int samsize, int d, String s)
{
    if (lcd)
    {
      M5.Lcd.clear();
      M5.Lcd.setCursor( x, y );
      M5.Lcd.setTextSize( samsize );
      M5.Lcd.println( s );
//      M5.Lcd.drawString( s, x, y, samsize );
    }
    else
      Serial.println(s);

    delay(d);
}
