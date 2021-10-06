//  door_monitor.cpp
//  Wireless Door security system.
//  ESP32 Microcontroller code that responds with status of a door sensor.
//  Devices:
//    Panasonic Hall Effect Sensor
//
//  Sam Portillo
//  06/01/2020
//  09/25/2020  Live Version 2  - No polling, just notify when open.
//  04/27/2021  Remove LoRa for Bluetooth & Terminal capabilities
//  04/29/2021  Send 1 transmission when status changes:
//        Send 1 transmission when door opens.
//        Send 1 transmission when door closes.
//  05/01/2021  MQTT
//  05/26/2021  - TTGO T-Display
//  06/01/2021  Integrated door_monitor with class.


//  References:
//    http://reyax.com/products/rylr896/
//    https://us.amazon.com/Anmbest-KY-003-Effect-Magnetic-Arduino/dp/B07NWFX53H
//    https://www.youtube.com/watch?v=gnlDHDFDqQ8
//    https://www.youtube.com/watch?v=uozq47oxfwE



//  Arduino Light & PIR Motion Sensors
//  Sam Portillo

//  PIR & Light Sensor
//  Features:
//    Terminal & MQTT
//  Board → TTGO T1 → ic2 does not work.
//  Board → TTGO LoRa32-OLED V1

#include <WiFi.h>
#include <PubSubClient.h>
#include <Wire.h>
#define BH1750a 0x23

#include "Terminal_M5_Stack.h"
//#include "Terminal_TTGO.h"

// Replace the next variables with your SSID/Password combination
const char* ssid          = "BEAR-2.4";
const char* password      = "3393bear";
const char* mqtt_server   = "10.1.10.183";

//const char* ssid          = "X50";
//const char* password      = "996summerfun";
//const char* ssid          = "Victorious";
//const char* password      = "2019summerfun";
//const char* mqtt_server   = "10.0.0.12";


//    OFFICE DOORS
const char* client_name           = "Office_Doors";
const char* publish_topic1         = "office/door1";
const char* publish_topic2         = "office/door2";
const char* subscription_terminal = "command/office/doors/terminal";
const char* subscription_sensor   = "command/office/doors";


bool    door_status = false;
String  door_status$ = "Closed";
void monitor_doors();
bool is_door1_open();
bool is_door2_open();
void alert_door_open(int i);
bool door1_closed = true;
bool door2_closed = true;


//M5Stack:
#define DOOR1 22
#define DOOR2 21
int x_door = 20;
int y_door = 150;
int s_door = 6;
int d1_x  = 0;
int d1_y  = 200;
int d2_x  = 280;
int d2_y  = 200;
int fsize  = 4;


//TTGO:
//#define DOOR1 0
//#define DOOR2 35
//int x_door = 20;
//int y_door = 70;
//int s_door = 1;
//int d1_x  = 0;
//int d1_y  = 100;
//int d2_x  = 200;
//int d2_y  = 100;
//int fsize  = 1;

WiFiClient espClient;
PubSubClient client(espClient);

String s;
String mv = "motion=";
String lv = "lux=";
uint16_t lux;
uint16_t llux = -11;
int shade = 20;
bool motion;

Terminal_M5_Stack t( mqtt_server );    // M5 Stack
//Terminal_TTGO t( mqtt_server );      //  TTGO

unsigned long previousMillis = 0;
unsigned long interval = 30000;

void setup_WiFi()
{
  t.fill_screen( TFT_RED );
  t.TFT_setTextColor( TFT_BLACK, TFT_RED );
  t.lcd_display( 30, 0, fsize, 0, "No WiFi" );
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED)
  {
    delay(500);
    Serial.print(".");
  }

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
  IPAddress broadCast = WiFi.localIP();
  Serial.println( broadCast );

  //  t.TFT_setTextColor( TFT_WHITE, TFT_BLACK );
  t.TFT_setTextColor( TFT_BLUE, TFT_BLACK );
  t.fill_screen( TFT_GREEN );
  t.lcd_display( 60, 0, fsize, 1000, "WiFi" );
  t.lcd_display( 0, 50, fsize, 3000, IpAddress2String( broadCast ) );
}


String IpAddress2String(const IPAddress& ipAddress)
{
  return String(ipAddress[0]) + String(".") +\
  String(ipAddress[1]) + String(".") +\
  String(ipAddress[2]) + String(".") +\
  String(ipAddress[3])  ;
}

void publish_message( const char* topic, String s )
{
  Serial.println( topic );
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
  Serial.print(topic);
  Serial.print(". Message: ");
  String message;

  for (int i = 0; i < length; i++)
  {
    Serial.print((char)message_b[i]);
    message += (char)message_b[i];
  }
  Serial.println();
  Serial.print( message );

  t.fill_screen( TFT_BLACK );
  t.lcd_display( 0, 50, fsize, 0, topic );
  t.lcd_display( 0, 85, fsize, 3000, message );
  t.fill_screen( TFT_BLACK );

  if ( topic.equals( subscription_terminal ) )
  {
      t.command( topic, message );
  }

  if ( topic.equals( subscription_sensor ) )
  {
        String c  = t.getNext( message, '=' );

        if ( c.equals("status") )
        {
            String p1 = String( is_door1_open() );
            String p2 = String( is_door2_open() );
            publish_message( publish_topic1, p1 );
            publish_message( publish_topic2, p2 );
            Serial.println( p1 );
            Serial.println( p2 );
            //            t.lcd_display( 10, 80, 2, 3000, p1 );
            //            t.lcd_display( 10, 80, 2, 3000, p2 );
              t.fill_screen( 0 );
              t.lcd_display( d1_x, d1_y, fsize, 0, String( digitalRead(DOOR1) ) );
              t.lcd_display( d2_x, d2_y, fsize, 0, String( digitalRead(DOOR2) ) );
        }
  }

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
        t.lcd_display( 30, 0, fsize, 0, "No MQTT" );

        checkConnections();
    }

      t.lcd_display( 0, 100, fsize, 3000, "MQTT Conne" );
      t.fill_screen( TFT_BLACK );
}

void setup_sensors()
{
  Wire.begin();
  Wire.setClock( 400000L );
  Wire.beginTransmission( BH1750a );
  Wire.write( 0x10 );
  Wire.endTransmission();
  delay( 1800 );

  pinMode(DOOR1, INPUT);
  pinMode(DOOR2, INPUT);
}

uint16_t luminosite(){
  uint16_t lux;
  Wire.requestFrom( BH1750a, 2 );
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

void setup()
{
//  Serial.begin( 115200 );               Comment out for M5Stack !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);
  setup_sensors();
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

  delay( 10 );
}

void read_sensors()
{
  monitor_doors();
}


void monitor_doors()
{
  if ( door1_closed )
  {
    if( is_door1_open() )
    {
      door1_closed = false;
      alert_door_open(1);
    }
  }
  else
  {
    if( !is_door1_open() )
    {
      door1_closed = true;
      alert_door_closed(1);
    }
  }

  if ( door2_closed )
  {
    if( is_door2_open() )
    {
      door2_closed = false;
      alert_door_open(2);
    }
  }
  else
  {
    if( !is_door2_open() )
    {
      door2_closed = true;
      alert_door_closed(2);
    }
  }
}


bool is_door1_open()
{
    return digitalRead(DOOR1);
}


bool is_door2_open()
{
    return digitalRead(DOOR2);
}


void alert_door_open(int i)
{
    if ( i == 1 )
      publish_message( publish_topic1, "1" );

    if ( i == 2 )
      publish_message( publish_topic2, "1" );

    t.lcd_display( x_door + 20, y_door, s_door, 3000, "Open " + String(i) );
    t.fill_screen( 0 );
    t.lcd_display( d1_x, d1_y, fsize, 0, String( digitalRead(DOOR1) ) );
    t.lcd_display( d2_x, d2_y, fsize, 0, String( digitalRead(DOOR2) ) );
}

void alert_door_closed(int i)
{
    if ( i == 1 )
      publish_message( publish_topic1, "0" );

    if ( i == 2 )
      publish_message( publish_topic2, "0" );

    t.lcd_display( x_door, y_door, s_door, 3000, "Closed " + String(i) );
    t.fill_screen( 0 );
    t.lcd_display( d1_x, d1_y, fsize, 0, String( digitalRead(DOOR1) ) );
    t.lcd_display( d2_x, d2_y, fsize, 0, String( digitalRead(DOOR2) ) );
}
