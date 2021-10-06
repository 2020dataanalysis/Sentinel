//  Arduino VL53L1X distance & PIR Motion Sensors
//  Sam Portillo

//  Features:
//    Terminal & MQTT
//  05/01/2021
//  05/26/2021  - TTGO T-Display
//  Board → TTGO T1 → ic2 does not work.
//  Board → ESP32 Arduino  → TTGO LoRa32-OLED V1
//                          → M5Stack-Core-ESP32

//  https://raw.githubusercontent.com/sparkfun/SparkFun_VL53L1X_Arduino_Library/master/examples/Example1_ReadDistance/Example1_ReadDistance.ino
//  https://www.l33t.uk/wp-content/uploads/2020/05/vl53l1X_Circuit.png
//  https://www.l33t.uk/ebay/vl53l1x/
#include <ComponentObject.h>
#include <RangeSensor.h>
#include <SparkFun_VL53L1X.h>
#include <vl53l1x_class.h>
#include <vl53l1_error_codes.h>

#include <WiFi.h>
#include <PubSubClient.h>
#include <Wire.h>
#define BH1750a 0x23

SFEVL53L1X distanceSensor;
bool is_espTTGO = true;

// Replace the next variables with your SSID/Password combination
//const char* ssid = "BEAR-2.4";
//const char* password = "3393bear";
//const char* mqtt_server   = "10.1.10.183";

//const char* ssid          = "X50";
//const char* password      = "996summerfun";
const char* ssid          = "Victorious";
const char* password      = "2019summerfun";
const char* mqtt_server   = "10.0.0.12";


//  TTGO
#include "Terminal_TTGO.h"
Terminal_TTGO t( mqtt_server );
int PIR = 12;   // TTGO T-Display Works
//int fontsize = 1;     //  ttgo

//  M5Stack
//#include "Terminal_M5_Stack.h"
//Terminal_M5_Stack t( mqtt_server );    // M5 Stack
//int PIR = 2;      // BEAR M5Stack
//int fontsize = 4;


//    OFFICE
const char* client_name           = "Office_sensors_TTGO";
//const char* client_name           = "Office_sensors_M5Stack";
const char* publish_topic         = "office";
const char* publish_topic_sonic         = "office/sonic";
const char* publish_topic_pir         = "office/pir";
const char* publish_topic_lux         = "office/lux";

const char* subscription_terminal = "command/office/terminal";
const char* subscription_sensor   = "command/office";


//    SHOP
//const char* client_name           = "Shop";
//const char* publish_topic         = "shop";
//const char* subscription_terminal = "command/shop/terminal";
//const char* subscription_sensor   = "command/shop";


WiFiClient espClient;
PubSubClient client(espClient);

String s;
String mv = "motion=";
String lv = "lux=";
String sv = "sonic=";
uint16_t lux;
uint16_t llux = 0;
int ld = 0;
int shade = 20;
bool motion;
unsigned long start_time = 0;
unsigned long last_time = 0;
int motion_count = 0;
//unsigned long previousMillis = 0;
unsigned long interval = 1000;      //  Allowed time to pass with no motion.
int motion_threshold = 1;

void setup_WiFi()
{
  t.fill_screen( TFT_RED );
  t.TFT_setTextColor( TFT_BLACK, TFT_RED );
  t.lcd_display( 30, 0, fontsize, 0, "No WiFi" );
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);
  
  int c = 0;
  while ( WiFi.status() != WL_CONNECTED )
  {
    t.lcd_display( 30, 50, fontsize, 0, String( c++ ) );
    WiFi.begin(ssid, password);         //  07/08/2021  WiFi crashed, may have been stuck in a loop.
    delay( 5000 );                      //  2000 is not enough but 3000 is.
    Serial.print(".");
  }
  
  if ( WiFi.status() == WL_CONNECTED )
  {
    Serial.println("");
    Serial.println("WiFi connected");
    Serial.println("IP address: ");
    Serial.println(WiFi.localIP());
    IPAddress broadCast = WiFi.localIP();
    Serial.println( broadCast );
  
    t.TFT_setTextColor( TFT_WHITE, TFT_BLACK );
    t.fill_screen( TFT_GREEN );
    t.lcd_display( 60, 0, fontsize, 1000, "WiFi" );
    t.lcd_display( 0, 50, fontsize, 3000, IpAddress2String( broadCast ) );
  }
}


String IpAddress2String(const IPAddress& ipAddress)
{
  return String(ipAddress[0]) + String(".") +\
  String(ipAddress[1]) + String(".") +\
  String(ipAddress[2]) + String(".") +\
  String(ipAddress[3])  ; 
}

//void wifi_connect()
//{
//  unsigned long currentMillis = millis();
//  // if WiFi is down, try reconnecting
//  if ((WiFi.status() != WL_CONNECTED) && (currentMillis - previousMillis >=interval)) {
//
////      setup_wifi();
////  client.setServer(mqtt_server, 1883);
////  client.setCallback(callback);
//
//    Serial.print(millis());
//    Serial.println("Reconnecting to WiFi...");
//    WiFi.disconnect();
//    WiFi.reconnect();
//    previousMillis = currentMillis;
//  }
//}
//
void publish_message( const char* topic, String s )
{
  Serial.println( s );
  char message[ 50 ];
  //  s.toCharArray(message, s.length() );
  t.string_to_charArray( s, message );
  client.publish( topic, message );
}

void callback(char* topicc, byte* message_b, unsigned int length)
{
  String topic = String( topicc );
  Serial.print("Message arrived on topic: ");
  Serial.println(topic);
  Serial.print("Message: ");
  String message;

  for (int i = 0; i < length; i++)
  {
    Serial.print((char)message_b[i]);
    message += (char)message_b[i];
  }
  Serial.println();
  Serial.print( message );

  t.fill_screen( TFT_BLACK );
  t.lcd_display( 0, 50, 1, 0, topic );
  t.lcd_display( 0, 85, 1, 3000, message );
  t.fill_screen( TFT_BLACK );

  if ( topic.equals( subscription_terminal ) )
  {
      t.command( topic, message );
  }

  if ( topic.equals( subscription_sensor ) )
  {
        String c  = t.getNext( message, '=' );

        if ( c.equals("motion") )
        {
            String p = mv + motion;
            Serial.println( p );
            publish_message( publish_topic_pir, p );
            t.lcd_display( 10, 80, fontsize, 3000, p );
        }

        if ( c.equals("light") )
        {
            String p = lv + lux;
            Serial.println( p );
            publish_message( publish_topic_lux, p );
            t.lcd_display( 10, 80, fontsize, 1000, p );
        }

        if ( c.equals("shade") )
        {
            shade = message.toInt();
            //            shade = s.substring(6, s.length() ).toInt();
            String shv = "shade=" + String( shade );
            //            String shv = "set shade=";    // Works
            Serial.println( shv );
            t.lcd_display( 1, 80, fontsize, 5000, shv );
            publish_message( publish_topic, shv );
        }


        if ( c.equals("motion_threshold") )
        {
            motion_threshold = message.toInt();
            String mt = "mt=" + String( motion_threshold );
            String p = "motion_threshold=" + String( motion_threshold );
            Serial.println( mt );
            t.lcd_display( 1, 80, fontsize, 5000, mt );
            publish_message( publish_topic_pir, p );
        }

  }

}

void setup_sensors()
{
  Wire.begin();
  //  Wire.setClock( 400000L );
  //  Wire.beginTransmission( BH1750a );
  //  Wire.write( 0x10 );
  //  Wire.endTransmission();
  //  delay( 1800 );

  pinMode(PIR, INPUT);

  if (distanceSensor.begin() != 0) //Begin returns 0 on a good init
  {
    Serial.println("Sensor failed to begin. Please check wiring. Freezing...");
    while (1)
      ;
  }
  Serial.println("Sensor online!");

}

  //uint16_t luminosite(){
  //  uint16_t lux;
  //  Wire.requestFrom( BH1750a, 2 );
  //  while( Wire.available() )
  //  {
  //    lux = Wire.read();
  //    lux<<=8;
  //    lux = lux + Wire.read();
  //  }
  //
  //  Wire.endTransmission();
  //  lux = lux / 1.2;
  //  return lux;
  //}

void setup()
{
  //  Serial.begin( 115200 );         // Need to comment out for M5Stack !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
  Serial.println("Starting...");
  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);
  setup_sensors();
  Serial.println("end setup");
}



void reconnect()
{
    Serial.print("Attempting MQTT connection...");
    if (client.connect( client_name ))
    {
      Serial.println("connected");
      client.subscribe( subscription_terminal );
      client.subscribe( subscription_sensor );
    } else
    {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      delay(5000);
    }
    
    if (!client.connected())
    {
        t.fill_screen( TFT_RED );
        t.TFT_setTextColor( TFT_BLACK, TFT_RED );
        t.lcd_display( 30, 0, fontsize, 0, "No MQTT" );
      
        checkConnections();
    }

      t.TFT_setTextColor( TFT_WHITE, TFT_BLACK );
      t.lcd_display( 0, 100, fontsize, 3000, "MQTT Conne" );
      t.fill_screen( TFT_BLACK );
}


void checkConnections()
{
  if ( WiFi.status() != WL_CONNECTED )
  {
    setup_WiFi();
  }

  if ( !client.connected() )
  {
    reconnect();
  }
  client.loop();
}


void loop()
{
  checkConnections();
  t.checkFlash();
  read_sensors();

  if ( motion_count > 0 )
  {
    int lapse = millis() - last_time;
    if ( lapse > interval )
    {    
      motion_count = 0;
      t.fill_screen( TFT_BLACK );
    }
  }
  
  //  Serial.println(".");
  delay( 100 );
}

void read_sensors()
{
  motion = digitalRead(PIR);
  if( motion )
  {
    if ( motion_count == 0 )
    {
        start_time = millis();
        t.fill_screen( TFT_BLACK );
    }
    last_time = millis();
    motion_count++;

    String pmotion = mv + motion_count;
    t.lcd_display( 1, 0, fontsize, 0, "         " );
    t.lcd_display( 1, 0, fontsize, 0, pmotion );

    if ( motion_count >= motion_threshold )
    {
        String p = mv + motion_count;
        Serial.println( p );
        publish_message( publish_topic_pir, String( motion_count) );
    }
  }
  

    int d = get_laser();
    String p = sv + d;
    t.lcd_display( 1, 40, fontsize, 0, "         " );
    t.lcd_display( 1, 40, fontsize, 0, p );

    if ( d > 2 * ld || d < ld / 2)
      {
          ld = d;
          publish_message( publish_topic_sonic, String( d ) );
      }
}


int get_laser()
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
