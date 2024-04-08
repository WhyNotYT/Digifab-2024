// Starter circuit for Fab Group 29 project Peili
// https://www.tinkercad.com/things/hb4XdCg2vdT-starter-circuit-fab-group-29-peili?sharecode=9KsRuAXjwTjm4bpIeXeTeTzwctn5diQfqF12yQzYIZo
// Laptop is capturing images from laptop's camera/external webcam, doing image processing to it using YOLOv5 and sending signal to Pi Pico whether player is moving or stationary

const int switchpin = 7;
const int led = 13;
const int buzzer = 10;

void setup()
{
  pinMode(switchpin, INPUT);
  pinMode(led, OUTPUT);
  pinMode(buzzer, OUTPUT);
  
}

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
    delay(timer2);
  }else {
     digitalWrite(led, LOW);
  }
}
