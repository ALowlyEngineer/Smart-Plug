#include "EmonLib.h"
#define VOLT_CAL 234.26
#define RATE 1000
#define RELAY 2
#define CURRENTPIN A0
#define VOLTAGEPIN A3
#define BAUDRATE 9600
#define LENGTHO 9
#define LENGTHI 2


String m_in;
String currPart, timePart, voltPart;
String send2pi;
float rawValue = 0;
double v_out = 0;
double current = 0;
double current_max = 0;
double startTime = 0;
double curTime = 0;
double supplyVoltage = 0;
int r = 1; 
int relayOn = 0;
int index = 0;


EnergyMonitor emon1;             // Create an instance

void setup() {

  Serial.begin(BAUDRATE);
  pinMode(RELAY, OUTPUT);
  pinMode(CURRENTPIN, INPUT);

  emon1.voltage(VOLTAGEPIN, VOLT_CAL, 1.7);  // Voltage: input pin, calibration, phase_shift

  startTime = millis();

}

void loop() {

  //See what the last time was 
  //Update var with time now
  //Difference between time now and last time
  //SAVE millis() to time; (millis() returns the number of seconds since the program started 
  // put your main code here, to run repeatedly:

  if (millis() - curTime > RATE){
        
          curTime = millis();
          timePart = String(curTime);
          rawValue = analogRead(CURRENTPIN);
          v_out = (rawValue/1024)*5;
          //Serial.println(v_out);

          current = (40 * (v_out - 2.5)-.8);
          currPart = String(current);
          //Serial.println(current);
          //if (current > current_max)  current_max = current;

          emon1.calcVI(20,2000);         // Calculate all. No.of half wavelengths (crossings), time-out
          supplyVoltage = emon1.Vrms;           //extract Vrms into Variable
          voltPart = String(supplyVoltage);
           
          send2pi = timePart + " " + currPart + " " + voltPart; 

          Serial.println(send2pi);

  }

  
  if(Serial.available()){ // While there is a message on the serial port
    relayOn = r * (Serial.read() - '0');
    
    if(relayOn == 0) {
      digitalWrite(RELAY, LOW);

          /*Serial.print("Raw Value = " ); // shows pre-scaled value 

          Serial.print(RawValue); 

          Serial.print("\t V = "); // shows the voltage measured 

          Serial.print(V_out,3); // the '3' after voltage allows you to display 3 digits after decimal point

          */

   

          //Serial.print("\t Time = ");

          /*Serial.print(curTime,3);

     

          Serial.print(" "); // shows the voltage measured 

          Serial.print(current,3);

     

          Serial.print(" ");

          Serial.print(supplyVoltage,3);

          */  

    }
    else if(relayOn == 1){

      digitalWrite(RELAY, HIGH);



        

      

    

    //relayOn = ' '; // Clear the message- leave the message so don't have to click on 2000 times

    // break;

  }

 

 } //end of for loop

  

} //end of void loop
