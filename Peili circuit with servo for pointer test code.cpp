// Circuit with servo for Fab Group 29 project Peili
// https://www.tinkercad.com/things/5qztOXME2p2-circuit-with-servo-for-pointer-fab-group-29-peili?sharecode=2j30A-xW1icCbDGnhbdYOuYkLmizfJhmE5WhmY5GOIw
//
#include <Servo.h>

//Servo servoBase;

const int switchpin = 7;
const int led = 13;
const int buzzer = 10;

void setup()
{
  pinMode(switchpin, INPUT);
  pinMode(led, OUTPUT);
  pinMode(buzzer, OUTPUT);
  //servoBase.attach(A1);
  //servoBase.write(0);

void loop()
{
  if(digitalRead(switchpin)) {
    //int timer = rand() % 1500 + 500; //501-2000 ms
    int timer1 = rand() % 1500 + 500; //501-2000 ms
    digitalWrite(led, HIGH);
    tone(buzzer, 200, timer1); // Send 100 Hz sound signal
  	delay(timer1);
    int timer2 = rand() % 1500 + 500; //501-2000 ms
    digitalWrite(led, LOW);
    servoBase.write(90);
    delay(timer2);
  }else {
     digitalWrite(led, LOW);
  }
}