
String m;
const int CurrentIn = A0;
const int VoltageIn = A3;
double RawValue = 0;
double V_out = 0;
double Current = 0;
double current_max = 0;
double startTime = 0;
double CurTime = 0;
float supplyVoltage =0;
#include "EmonLib.h"   
#define VOLT_CAL 234.26
EnergyMonitor emon1;             // Create an instance

void setup() {
  Serial.begin(9600);
  pinMode(2,OUTPUT);
  pinMode(A1, INPUT);
  pinMode(5,INPUT);

  emon1.voltage(A3, VOLT_CAL, 1.7);  // Voltage: input pin, calibration, phase_shift
  startTime = millis();
}

void loop() {
  //See what the last time was 
  //Update var with time now
  //Difference between time now and last time
  //SAVE millis() to time; (millis() returns the number of seconds since the program started 
  // put your main code here, to run repeatedly:


  RawValue = analogRead(CurrentIn);
  CurTime = millis();
  V_out = (RawValue/1024)*5;
  Current = 40*(V_out - 2.5)-.8;
  if (Current > current_max)  
    current_max =Current;
  
  emon1.calcVI(20,2000);         // Calculate all. No.of half wavelengths (crossings), time-out
  supplyVoltage = emon1.Vrms;             //extract Vrms into Variable
  
  /*Serial.print("Raw Value = " ); // shows pre-scaled value 
  Serial.print(RawValue); 
  Serial.print("\t V = "); // shows the voltage measured 
  Serial.print(V_out,3); // the '3' after voltage allows you to display 3 digits after decimal point
  */
  Serial.print("\t Current = "); // shows the voltage measured 
  Serial.println(Current,3);
  
  Serial.print("\t Time = ");
  Serial.print(CurTime);
  delay(1000);
  Serial.print("\t Vrms In = ");
  Serial.println(supplyVoltage);

 
  
/*
  digitalWrite(4,HIGH);
  Serial.println(digitalRead(5));
  delay(1000);
  digitalWrite(4,LOW);
Serial.println(digitalRead(5));
  delay(1000);
  */

    while(Serial.available() > 0) // While there is a message on the serial port
{
char recv = Serial.read(); // log the current message
if(recv == '\n') // If it's the end of the message
{
//Print the message
Serial.print("Received: ");
Serial.println(m);

if(m == "CLOSE" || m=="C") {
digitalWrite(2,LOW);
}
else if(m == "OPEN" || m=="O"){
  digitalWrite(2,HIGH);
}
m = ""; // Clear the message
break;

}
else // Not at the end of the message
{
m += recv; // Append the next character onto the message string
}
}
}
