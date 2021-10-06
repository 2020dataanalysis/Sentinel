//  Arduino MQTT Terminal class
//  Sam Portillo
//  05/01/2021

//References:
//https://www.youtube.com/watch?v=UE1mtlsxfKM


//#include "Free_Fonts.h" // Include the header file attached to this sketch
#include <TFT_eSPI.h> // Graphics and font library for ST7735 driver chip
#include <SPI.h>

TFT_eSPI tft = TFT_eSPI();  // Tools  → Manage Libraries  → Search TFT_eSPI   by Bodmer
//, pins defined in User_Setup.h

#define TFT_GREY 0x5AEB // New colour

//Odd font sizes do not work.
//Works up to size 4.
//print=20,40,4,0,Sammy
//print=100,200,1,0,Sammy     // Max
//print=0,80,2,0,door/1/1


class Terminal_TTGO
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

    Terminal_TTGO( const char * c )
    {
      //        mqtt_server = c;
      tft.init();
      tft.setRotation(1);
      tft.fillScreen(TFT_GREY);

      // Set "cursor" at top left corner of display (0,0) and select font 2
      // (cursor will move to next line automatically during printing with 'tft.println'
      //  or stay on the line is there is room for the text with tft.print)
      tft.setCursor(0, 0);
      // Set the font colour to be white with a black background, set text size multiplier to 1
      tft.setTextColor(TFT_WHITE,TFT_BLACK);
      tft.setTextSize( font_size );
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
          //      M5.Lcd.clear();
          tft.setTextColor( TFT_WHITE, TFT_BLACK );
          tft.fillScreen( TFT_BLACK );
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
          tft.fillScreen( flash_color1 );
          Serial.println( flash_color1 );
        }
      else
      {
        flash_on = true;
        tft.fillScreen( flash_color2 );
        Serial.println( flash_color2 );
      }
      delay( 1000 );
     }
    }

  void lcd_display(int x2, int y2, int font_size2, int d2, String s2)
  {
    if (lcd)
    {
        //      M5.Lcd.setCursor( x2, y2 );
        //      M5.Lcd.setTextSize( font_size2 );
        //      M5.Lcd.println( s2 );
        //        tft.setFreeFont(TT1);     // Select the orginal small TomThumb font
        tft.setCursor( x2, y2, font_size2 );
        tft.println( s2 );
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
      tft.fillScreen( color );
  }

  void TFT_setTextColor( int font_color, int back_font_color )
  {
    tft.setTextColor( font_color, back_font_color );
  }

//  void stdString_to_charArray(std::string s, char* c)
//  {
//      //    char c[50];
//      int i = 0;
//      for (; i < s.length(); i++)
//      {
//          c[i] = s.at(i);
//      }
//      c[i] = '\0';
//      Serial.print("c=");
//      Serial.println( c );
//  }

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






// Default color definitions
//#define TFT_BLACK       0x0000      /*   0,   0,   0 */         0
//#define TFT_NAVY        0x000F      /*   0,   0, 128 */         15
//#define TFT_DARKGREEN   0x03E0      /*   0, 128,   0 */
//#define TFT_DARKCYAN    0x03EF      /*   0, 128, 128 */
//#define TFT_MAROON      0x7800      /* 128,   0,   0 */
//#define TFT_PURPLE      0x780F      /* 128,   0, 128 */
//#define TFT_OLIVE       0x7BE0      /* 128, 128,   0 */
//#define TFT_LIGHTGREY   0xD69A      /* 211, 211, 211 */
//#define TFT_DARKGREY    0x7BEF      /* 128, 128, 128 */
//#define TFT_BLUE        0x001F      /*   0,   0, 255 */
//#define TFT_GREEN       0x07E0      /*   0, 255,   0 */
//#define TFT_CYAN        0x07FF      /*   0, 255, 255 */
//#define TFT_RED         0xF800      /* 255,   0,   0 */         63488
//#define TFT_MAGENTA     0xF81F      /* 255,   0, 255 */
//#define TFT_YELLOW      0xFFE0      /* 255, 255,   0 */
//#define TFT_WHITE       0xFFFF      /* 255, 255, 255 */         65535
//#define TFT_ORANGE      0xFDA0      /* 255, 180,   0 */
//#define TFT_GREENYELLOW 0xB7E0      /* 180, 255,   0 */
//#define TFT_PINK        0xFE19      /* 255, 192, 203 */ //Lighter pink, was 0xFC9F      65049
//#define TFT_BROWN       0x9A60      /* 150,  75,   0 */
//#define TFT_GOLD        0xFEA0      /* 255, 215,   0 */
//#define TFT_SILVER      0xC618      /* 192, 192, 192 */
//#define TFT_SKYBLUE     0x867D      /* 135, 206, 235 */         34429
//#define TFT_VIOLET      0x915C      /* 180,  46, 226 */
