//  Arduino Light & PIR Motion Sensors
//  Sam Portillo

//  PIR & Light Sensor
//  Features:
//    Terminal & MQTT
//  05/01/2021

#include <Arduino.h>
#include <M5Stack.h>
#include <WiFi.h>
#include <PubSubClient.h>
#include <Wire.h>
#define BH1750a 0x23
#include "Terminal.h"
// Replace the next variables with your SSID/Password combination
const char* ssid = "X";
const char* password = "xxxx
const char* mqtt_server   = "10.0.0.12";

//    OFFICE
const char* client_name           = "Office";
const char* publish_topic         = "office";
const char* subscription_terminal = "command/office/terminal";
const char* subscription_sensor   = "command/office";



////    SHOP
//const char* client_name           = "Shop";
//const char* publish_topic         = "shop";
//const char* subscription_terminal = "command/shop/terminal";
//const char* subscription_sensor   = "command/shop";


WiFiClient espClient;
PubSubClient client(espClient);

String s;
int PIR = 2;
//int PIR = 15;   // TTGO T-Display Works

String mv = "motion=";
String lv = "lux=";
uint16_t lux;
uint16_t llux = -11;
int shade = 20;
bool motion;

Terminal t( mqtt_server );

void setup_wifi()
{
  delay(10);
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
}



void publish_message( const char* topic, String s )
{
  if (!client.connected())
  {
    reconnect();
  }
  client.loop();

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
            publish_message( publish_topic, p );
        }

        if ( c.equals("light") )
        {
            String p = lv + lux;
            Serial.println( p );
            publish_message( publish_topic, p );
        }

        if ( c.equals("shade") )
        {
            shade = message.toInt();
            //            shade = s.substring(6, s.length() ).toInt();
            String shv = "set shade=" + String( shade );
            //            String shv = "set shade=";    // Works
            Serial.println( shv );
            t.lcd_display( 5, 140, 6, 5000, shv );
            publish_message( "topic", shv );
        }
  }

}

void reconnect()
{
  // Loop until we're reconnected
  while (!client.connected())
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
  }
}

void setup_sensors()
{
  Wire.begin();
  Wire.setClock( 400000L );
  Wire.beginTransmission( BH1750a );
  Wire.write( 0x10 );
  Wire.endTransmission();
  delay( 1800 );

  pinMode(PIR, INPUT);
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
  M5.begin();         //  Automatically sets up Serial.begin();
  M5.Lcd.setTextSize(5);
  setup_wifi();
  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);
  setup_sensors();
}

void loop() {
  t.checkFlash();
  read_sensors();

  if (!client.connected())
  {
    reconnect();
  }
  client.loop();

  //  Serial.println( shade );
  delay( 1000 );
}

void read_sensors()
{
  motion = digitalRead(PIR);
  if( motion )
  {
    Serial.println("Presence Detected");
    t.lcd_display( 5, 190, 10, 500, "Motion" );
    String p = mv + motion;
    Serial.println( p );
    publish_message( publish_topic, p );
    delay( 2000 );
    t.lcd_display( 5, 190, 10, 500, "      " );
  }
  

  lux = luminosite();
  int d = abs( lux - llux );
  llux = lux;

  if ( d > shade )
  {
      String p = lv + lux;
      Serial.println( p );
      t.lcd_display( 1, 190, 10, 0, "          " );
      t.lcd_display( 1, 190, 10, 500, p );
      publish_message( publish_topic, p );
  }
  s = String( lux );
  //String slux = s.substring(0, 4);
  //  t.lcd_display( 10, 50, 20, 500, s );
  Serial.println( s );
}
