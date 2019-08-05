#include "EmonLib.h"
#define VOLT_CAL 234.26
#define RATE 1
#define RELAY 2
#define CURRENTPIN A0
#define VOLTAGEPIN A3
#define BAUDRATE 115200

String m_in;
String currPart, timePart, voltPart;
String send2pi;
float rawValue = 0.000;
double v_out = 0.000;
double current = 0.000;
double current_max = 0.000;
double startTime = 0000;
double curTime = 0.000;
double endTime = 0.0000;
double supplyVoltage = 0.000;
int r = 1; 
int relayOn = 0;
int index = 0;


EnergyMonitor emon1;             // Create an instance

void setup() {

  analogReference(EXTERNAL);
  Serial.begin(BAUDRATE);
  pinMode(RELAY, OUTPUT);
  pinMode(CURRENTPIN, INPUT);

  //emon1.voltage(VOLTAGEPIN, VOLT_CAL, 1.7);  // Voltage: input pin, calibration, phase_shift

  startTime = millis();

}

void loop() {

  //See what the last time was 
  //Update var with time now
  //Difference between time now and last time
  //SAVE millis() to time; (millis() returns the number of seconds since the program started 
  // put your main code here, to run repeatedly:

        
          curTime = millis();
          rawValue = analogRead(CURRENTPIN);
          
          //Serial.print("Analog: ");
          //Serial.print(rawValue);
          v_out = (rawValue/1024.0000000)*4.80000;
          //Serial.print("    volt: ");
          //Serial.print(v_out);
          //Serial.print("     current: ");
          current = 40.00000 * (v_out - 2.4800000);
          currPart = String(current);
          timePart = String(curTime);
          //Serial.print(current);
          //Serial.print("\n");
          //if (current > current_max)  current_max = current;
          
          
          //emon1.calcVI(20,2000);         // Calculate all. No.of half wavelengths (crossings), time-out
          //supplyVoltage = emon1.Vrms;           //extract Vrms into Variable
          //voltPart = String(supplyVoltage);
        
          send2pi = timePart + " " + currPart + " " + startTime; 
          endTime = millis();
          Serial.println(send2pi);

          //Serial.println(curTime);
          //Serial.println(endTime);
          

  
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
