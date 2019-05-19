#include "EmonLib.h"

#define VOLT_CAL 234.26
#define RATE 1000
#define RELAY 2
#define CURRENTPIN A0
#define VOLTAGEPIN A3
#define BAUDRATE 9600
#define LENGTHO 9
#deinfe LENGTHI 2
#define STX 0x06

String m_in;
double rawValue = 0;
double v_out = 0;
double current = 0;
double current_max = 0;
double startTime = 0;
double curTime = 0;
bool relayOn = 0;
float supplyVoltage = 0;
  
EnergyMonitor emon1;             // Create an instance

byte msg_out[LENGTHO] =
{ STX,                 //STX Byte
  0x00,0x00,            //Voltage x 1000
  0x00,0x00,            //Current x 1000
  0x00,0x00,0x00, 0x00, //Time
};

byte msg_in[LENGTHI] = 
{ STX,
  0x00   // Relay Control Byte
};

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
    rawValue = analogRead(currentIn);
    v_out = (rawValue/1024)*5;
    current = 40*(v_out - 2.5)-.8;
    if (current > current_max)  current_max = current;

    emon1.calcVI(20,2000);         // Calculate all. No.of half wavelengths (crossings), time-out
    supplyVoltage = emon1.Vrms;             //extract Vrms into Variable

    /*Serial.print("Raw Value = " ); // shows pre-scaled value 
    Serial.print(RawValue); 
    Serial.print("\t V = "); // shows the voltage measured 
    Serial.print(V_out,3); // the '3' after voltage allows you to display 3 digits after decimal point
    */
   
    msg_out[LENGTHO - 8] = (byte)((supplyVoltage*1000) >> 8);
    msg_out[LENGTHO - 7] = (byte)(supplyVoltage*1000);
      
    msg_out[LENGTHO - 6] = (byte)((current*1000) >> 8);
    msg_out[LENGTHO - 5] = (byte)(current*1000);
   
   
    msg_out[LENGTHO - 4] = (byte)(curTime >> 24);
    msg_out[LENGTHO - 3] = (byte)(curTime >> 16);
    msg_out[LENGTHO - 2] = (byte)(curTime >> 8);
    msg_out[LENGTHO - 1] = (byte)(curTime);
   
   /*
    Serial.print("\t Time = ");
    Serial.print(curTime);
   
    Serial.print("\t Current = "); // shows the voltage measured 
    Serial.println(current,3);
   
    Serial.print("\t Vrms In = ");
    Serial.println(supplyVoltage);
*/
   Serial.write(msg_out, LENGTHO);
  }
  
/*
  digitalWrite(4,HIGH);
  Serial.println(digitalRead(5));
  delay(1000);
  digitalWrite(4,LOW);
Serial.println(digitalRead(5));
  delay(1000);
  */

if(Serial.available() > (LENGTHI - 1)){ // While there is a message on the serial port
  Serial.readBytes(msg_in, LENGTHI);
  
    relayOn = if (msg_in[LENGTHI-1] > 0);
  /*
  char recv = Serial.read(); // log the current message
  if(recv == '\n'){ // If it's the end of the message

    //Print the message
    Serial.print("Received: ");
    Serial.println(m_in);
  */
    if(relayOn) {
      digitalWrite(RELAY, LOW);
      }
    else if(!relayOn){
      digitalWrite(RELAY, HIGH);
      }
    relayOn = ""; // Clear the message
   // break;
  }
  
  /*
  else{ // Not at the end of the message
    m_in += recv; // Append the next character onto the message string
  }
  */
}
}
