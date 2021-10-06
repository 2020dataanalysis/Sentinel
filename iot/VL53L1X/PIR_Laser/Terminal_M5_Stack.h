//  Arduino MQTT Terminal class
//  Sam Portillo
//  05/01/2021
//  05/28/2021  M5 Stack

#include <M5Stack.h>
//print=20,40,4,0,Sammy


class Terminal_M5_Stack
{
  public:
    // Add your MQTT Broker IP address, example:
    //    const char* mqtt_server;      // Not used
    String s;
    bool flash        = false;
    int flash_color1  = 1600;
    int flash_color2  = 31;
    bool flash_on     = false;
    bool lcd          = true;
    int x = 20;
    int y = 150;
    int font_size = 4;
    String publish_string;

    Terminal_M5_Stack( const char * c )
    {
      M5.begin();
      M5.Lcd.setTextSize( font_size );
//      M5.Lcd.println("Hello");
      Serial.println("M5Stack");
    }

    void command( String topic, String s )
    {
        String c  = getNext( s, '=' );
        if ( c.equals("print") )
        {
          int x = getNext( s, ',' ).toInt();
          int y = getNext( s, ',' ).toInt();
          int fontsize = getNext( s, ',' ).toInt();
          int d = getNext( s, ',' ).toInt();
          s = getNext( s, ',' );
          lcd_display( x, y, fontsize, d, s );
        }
    
        if ( c.equals("clear") )
        {
          flash = false;
          
          //          tft.setTextColor( TFT_WHITE, TFT_BLACK );
          //          tft.fillScreen( TFT_BLACK );
          fill_screen( 0 );
        }
    
    
        if ( c.equals("flash") )
        {
          flash_color1 = getNext( s, ',' ).toInt();
          flash_color2 = s.toInt();
          Serial.println( flash_color1 );
          Serial.println( flash_color2 );
          flash = true;
        }
    }

    void checkFlash()
    {
     if ( flash )
     {
      if ( flash_on )
        {
          flash_on = false;
          fill_screen( flash_color1 );
          Serial.println( flash_color1 );
        }
      else
      {
        flash_on = true;
        fill_screen( flash_color2 );
        Serial.println( flash_color2 );
      }
      delay( 1000 );
     }
    }

  void lcd_display(int x2, int y2, int font_size2, int d2, String s2)
  {
    if (lcd)
    {
              M5.Lcd.setCursor( x2, y2 );
              M5.Lcd.setTextSize( font_size2 );
              M5.Lcd.println( s2 );
    }
    else
      Serial.println(s2);

    delay(d2);
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


  void fill_screen(int color)
  {
      M5.Lcd.fillScreen( color );
      //            M5.Lcd.clear();
  }

  void TFT_setTextColor( int font_color, int back_font_color )
  {
//    tft.setTextColor( font_color, back_font_color );
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

  void string_to_charArray( String s, char* c )
  {
      int i = 0;
      for (; i < s.length(); i++)
      {
          c[i] = s.charAt(i);
      }
      c[i] = '\0';
  }

};
