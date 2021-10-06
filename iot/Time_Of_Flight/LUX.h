//  LUX

//String lv = "lux=";
uint16_t lux;
uint16_t llux = 0;


void setup_TOF()
{
  Wire.begin();
  Wire.setClock( 400000L );
  Wire.beginTransmission( BH1750a );
  Wire.write( 0x10 );
  Wire.endTransmission();
  delay( 1800 );
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


void lux_action()
{
  //      int d = abs( lux - llux );
  //      int dd = 2 * d;
  //      double per = d / lux;
//  String p = lv + lux;
//  if ( lux > 2 * llux || lux < llux / 2)
//  {
//      llux = lux;
//      //          Serial.println( p );
//      publish_message( publish_topic_lux, String( lux ) );
//  }
//  t.lcd_display( 1, 80, fontsize, 0, "            " );
//  t.lcd_display( 1, 80, fontsize, 0, p );

    //  if ( motion_count == 0 )
    //  if ( motion_count == -1 )
    //  {
    //      lux = luminosite();
    //      lux_action();
    //  }

}
