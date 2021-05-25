//  notify.cpp
//  Wireless Door security system.
//  ESP32 Microcontroller code that responds with status of a door sensor.
//  Devices:
//    Panasonic PIR Sensor
//
//  Sam Portillo
//  06/01/2020
//  09/25/2020  Live Version 2  - No polling, just notify when open.
//  04/27/2021  Remove LoRa for Bluetooth & Terminal capabilities
//  04/29/2021  Send 1 transmission when status changes:
//        Send 1 transmission when door opens.
//        Send 1 transmission when door closes.
//  05/01/2021  MQTT


//  References:
//    http://reyax.com/products/rylr896/
//    https://us.amazon.com/Anmbest-KY-003-Effect-Magnetic-Arduino/dp/B07NWFX53H
//    https://www.youtube.com/watch?v=gnlDHDFDqQ8
//    https://www.youtube.com/watch?v=uozq47oxfwE


#include <Arduino.h>
#include <M5Stack.h>

//    ************************************    MQTT  *********************
//    *************************************************************************
#include <WiFi.h>
#include <PubSubClient.h>
// Replace the next variables with your SSID/Password combination
const char* ssid = "X";
const char* password = "x";

// Add your MQTT Broker IP address, example:
const char* mqtt_server = "10.0.0.12";
const char* client_name = "Office_Doors";
WiFiClient espClient;
PubSubClient client(espClient);

String s;

String getNext( String &s, char d );
void print(int, int, int, int, String);
bool flash      = false;
int flash_color1 = 0;
int flash_color2 = 0;
bool flash_on   = false;

#define DOOR1 22
#define DOOR2 21

bool    lcd         = true;
bool    door_status = false;
String  door_status$ = "Closed";

void monitor_doors();
bool is_door1_open();
bool is_door2_open();
void alert_door_open(int i);
bool door1_closed = true;
bool door2_closed = true;
int x_door = 20;
int y_door = 150;
int s_door = 6;

void setup()
{
  if (lcd)
  {
    M5.begin();
    M5.Lcd.setTextSize(5);
    print( x_door, y_door, s_door, 0, " Closed" );
    print(   0, 200, 5, 0, "0" );          // 0 → Closed, 1 → Open
    print( 280, 200, 5, 0, "0" );
  }
  else
  {
    Serial.begin(115200);
  }

  setup_wifi();
  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);

  pinMode(DOOR1, INPUT);
  pinMode(DOOR2, INPUT);
}


void setup_wifi()
{
  delay(10);
  // We start by connecting to a WiFi network
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



void callback(char* topic, byte* message, unsigned int length)
{
  Serial.print("Message arrived on topic: ");
  Serial.print(topic);
  Serial.print(". Message: ");
  String messageTemp;

  for (int i = 0; i < length; i++)
  {
    Serial.print((char)message[i]);
    messageTemp += (char)message[i];
  }
  Serial.println();
  String top = String( topic );
  Serial.print( top );
  Serial.print( messageTemp );
  command( top, messageTemp );
}

void reconnect()
{
  // Loop until we're reconnected
  while (!client.connected())
  {
    Serial.print("Attempting MQTT connection...");
    // Attempt to connect
    if (client.connect( client_name ))
    {
      Serial.println("connected");
      client.subscribe("command/office/door");
    } else
    {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      // Wait 5 seconds before retrying
      delay(5000);
    }
  }
}


void command( String topic, String s )
{
	//	Not using topic

	String c  = getNext( s, '=' );
  if ( c.equals("print") )
  {
      int x = getNext( s, ',' ).toInt();
      int y = getNext( s, ',' ).toInt();
      int fontsize = getNext( s, ',' ).toInt();
      int d = getNext( s, ',' ).toInt();
      s = getNext( s, ',' );
      print( x, y, fontsize, d, s );
  }

  if ( c.equals("clear") )
  {
      flash = false;
      M5.Lcd.clear();
  }

  if ( c.equals("flash") )
    {
      flash_color1 = getNext( s, ',' ).toInt();
      flash_color2 = s.toInt();
      Serial.println( flash_color1 );
      Serial.println( flash_color2 );
      M5.Lcd.fillScreen( flash_color1 );
      flash = true;
    }

  if ( c.equals("status") )
  {
    publish_message( "door=1," + String( is_door1_open() ) );
    publish_message( "door=2," + String( is_door2_open() ) );
  }

}


void loop()
{
 if ( flash )
 {
    if ( flash_on )
      {
          flash_on = false;
          M5.Lcd.fillScreen( flash_color1 );
      }
    else
    {
      flash_on = true;
      M5.Lcd.fillScreen( flash_color2 );
    }
    delay( 1000 );
 }


  monitor_doors();

  if (!client.connected())
  {
    reconnect();
  }
  client.loop();
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
    String s = "door=" + String(i);
    String t = s + ",1";
    publish_message( t );
    M5.Lcd.clear();
    print( x_door + 20, y_door, s_door, 0, "Open " + String(i) );
    print(   0, 200, 5, 0, String( digitalRead(DOOR1) ) );
    print( 280, 200, 5, 0, String( digitalRead(DOOR2) ) );
}


void alert_door_closed(int i)
{
    String s = "door=" + String(i) + ",0";
    publish_message( s );
    print( x_door, y_door, s_door, 3000, "Closed " + String(i) );
    M5.Lcd.clear();
    print( x_door + 25, y_door, s_door, 0, "Closed" );
    print(   0, 200, 5, 0, String( digitalRead(DOOR1) ) );
    print( 280, 200, 5, 0, String( digitalRead(DOOR2) ) );
}


void stdString_to_charArray(std::string s, char* c)
{
		//    char c[50];
    int i = 0;
    for (; i < s.length(); i++)
    {
        c[i] = s.at(i);
    }
    c[i] = '\0';
    Serial.print("c=");
    Serial.println( c );
}


void print(int x, int y, int font_size, int d, String s)
{
		flash = false;
    if (lcd)
    {
      M5.Lcd.setCursor( x, y );
      M5.Lcd.setTextSize( font_size );
      M5.Lcd.println( s );
    }
    else
      Serial.println(s);

    delay(d);
}


String getNext( String &s, char d )
{
  int i   = s.indexOf( d );
  String x  = s.substring( 0, i );
  Serial.println( "x=" + x );
  Serial.println( s );
  s = s.substring( i + 1, s.length() );
  return x;
}


void publish_message( String s )
{
  if (!client.connected())
  {
    reconnect();
  }
  client.loop();

  Serial.println( s );
  char message[ 50 ];
  //  s.toCharArray(message, s.length() );
  string_to_charArray( s, message );
  client.publish( "door", message );
}


void string_to_charArray( String s, char* c )
{
    int i = 0;
    for (; i < s.length(); i++)
    {
        c[i] = s.charAt(i);
    }
    c[i] = '\0';
}
