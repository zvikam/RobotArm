#define ENGINE_OFF      0
#define ENGINE_FORWARD  1
#define ENGINE_BACKWARD 2

#define ENGINA_MASK 0x03

#define ENGINE1  0
#define ENGINE2  2
#define ENGINE3  4
#define ENGINE4  6

#define OUT_ENGINE1_FORWARD  P2_0
#define OUT_ENGINE1_BACKWARD P2_1
#define OUT_ENGINE2_FORWARD  P2_2
#define OUT_ENGINE2_BACKWARD P2_3
#define OUT_ENGINE3_FORWARD  P2_4 
#define OUT_ENGINE3_BACKWARD P2_5
#define OUT_ENGINE4_FORWARD  P1_4
#define OUT_ENGINE4_BACKWARD P1_5

unsigned char inChar = 0;
boolean haveData = false;

void drive(int pin, int engine, int value) {
  int val = LOW;
  if ((inChar & (ENGINA_MASK << engine)) == (value << engine))
    val = HIGH;
  digitalWrite(pin, val);
}

void update() {
  drive(OUT_ENGINE1_FORWARD, ENGINE1, ENGINE_FORWARD);
  drive(OUT_ENGINE1_BACKWARD, ENGINE1, ENGINE_BACKWARD);
  
  drive(OUT_ENGINE2_FORWARD, ENGINE2, ENGINE_FORWARD);
  drive(OUT_ENGINE2_BACKWARD, ENGINE2, ENGINE_BACKWARD);
  
  drive(OUT_ENGINE3_FORWARD, ENGINE3, ENGINE_FORWARD);
  drive(OUT_ENGINE3_BACKWARD, ENGINE3, ENGINE_BACKWARD);
  
  drive(OUT_ENGINE4_FORWARD, ENGINE4, ENGINE_FORWARD);
  drive(OUT_ENGINE4_BACKWARD, ENGINE4, ENGINE_BACKWARD);
}

void setup()
{
  Serial.begin(9600);
  pinMode(RED_LED, OUTPUT);
  pinMode(OUT_ENGINE1_FORWARD, OUTPUT);
  pinMode(OUT_ENGINE1_BACKWARD, OUTPUT);
  pinMode(OUT_ENGINE2_FORWARD, OUTPUT);
  pinMode(OUT_ENGINE2_BACKWARD, OUTPUT);
  pinMode(OUT_ENGINE3_FORWARD, OUTPUT);
  pinMode(OUT_ENGINE3_BACKWARD, OUTPUT);
  pinMode(OUT_ENGINE4_FORWARD, OUTPUT);
  pinMode(OUT_ENGINE4_BACKWARD, OUTPUT);
  update();
}

void loop()
{
  if (haveData) {
    digitalWrite(RED_LED, HIGH);
    haveData = false;
    update();
  } else {
    digitalWrite(RED_LED, LOW);
  }
}

void serialEvent() {
  while (Serial.available()) {
    // get the new byte:
    inChar = Serial.read();
    haveData = true;
  }
}
