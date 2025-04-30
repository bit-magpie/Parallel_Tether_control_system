#include <DynamixelWorkbench.h>

#define BAUDRATE  57600
#define DXL_ID    1

DynamixelWorkbench dxl_wb;
uint8_t dxl_id = DXL_ID;

byte pin_state[8];
byte input_pin[] = {2,3,4,5,6,7,8,9};
int dec_position = 0;

int current_revs = 0;
int prev_enc_value = -1;
int stop_at = 0;

struct RevsAngle{
  int revs;
  int angle;
};

String serial_data;

RevsAngle to_rotate;

int readEncoder(){
  for(int i=7; i>=0; i--){
    pin_state[i] = !digitalRead(input_pin[i]);
  }

  dec_position = pin_state[7];
  for( int i = 6; i >= 0; i = i -1){
    dec_position = (dec_position << 1) | (pin_state[i] ^ (dec_position&0x1));
  }
  
//  Serial.println(dec_position, DEC); 
  return dec_position;
}

void coutRevs(){
  int current_value = readEncoder();
  
  if (prev_enc_value == -1){
    prev_enc_value = current_value;
  }

  if ((current_value - prev_enc_value)>0 and abs(current_value - prev_enc_value)>200){
    current_revs--;
  } else if ((current_value - prev_enc_value)<0 and abs(current_value - prev_enc_value)>200) {
    current_revs++;
  }
  
  prev_enc_value = current_value;
}

void calcRevsAngle(float thet_len){
  float circ_len = thet_len / (2 * M_PI * 6);
  int num_revs = 0;
  if (circ_len > 0){
    num_revs = floor(circ_len);
  } else {
    num_revs = ceil(circ_len);
  }

  float frac = 0.0;
  if (num_revs != 0){
    frac = fmod(abs(circ_len), num_revs);
  } else {
    frac = abs(circ_len);
  }

  to_rotate = {num_revs, ceil(frac*256)};
}

void moveThether(){
  stop_at = current_revs + to_rotate.revs - 200;
  if (to_rotate.revs > 0){
    Serial.println("starting cw");    
    dxlRotate(true, 100);    
  } else {
    Serial.println("starting ccw");
    dxlRotate(false, 100);    
  }  
}

void checkMotorRevs(){
  int cur_angle = readEncoder();
  if (to_rotate.revs > 0){
    if (current_revs >= stop_at){
      if (to_rotate.angle >= cur_angle){
          dxlRotate(true, 0);
      }
    }
  } else {
    if (current_revs <= stop_at){
      if (to_rotate.angle <= cur_angle){
        dxlRotate(true, 0);
      }
    }
  }
}

void dxlRotate(bool dir, int rot_speed)
{
  if (dir)
  {
    dxl_wb.goalVelocity(dxl_id, (int32_t)rot_speed);
  } else
  {
    dxl_wb.goalVelocity(dxl_id, (int32_t)-rot_speed);
  }
}

void setup(){
  Serial.begin(115200);

  for(byte i = 0; i <8; i = i +1 ){ 
    pinMode(input_pin[i], INPUT_PULLUP);
  }
  
  const char *log;
  bool result = false;

  uint16_t model_number = 0;

  result = dxl_wb.init("", BAUDRATE, &log);
  if (result == false)
  {
    Serial.println(log);
    Serial.println("Failed to init");
  }
  else
  {
    Serial.print("Succeeded to init : ");
    Serial.println(BAUDRATE);  
  }

  result = dxl_wb.ping(dxl_id, &model_number, &log);
  if (result == false)
  {
    Serial.println(log);
    Serial.println("Failed to ping");
  }
  else
  {
    Serial.println("Succeeded to ping");
    Serial.print("id : ");
    Serial.print(dxl_id);
    Serial.print(" model_number : ");
    Serial.println(model_number);
  }

  result = dxl_wb.wheelMode(dxl_id, 0, &log);
  if (result == false)
  {
    Serial.println(log);
    Serial.println("Failed to change wheel mode");
  }
  else
  {
    Serial.println("Succeed to change wheel mode");
    Serial.println("Dynamixel is moving...");
  }
}

void loop(){
//  Serial.print("Enc value: ");
//  Serial.print(readEncoder());
  
  coutRevs();
  Serial.print(" - Rev value: ");
  Serial.println(current_revs);
  checkMotorRevs();
//  float serial_float = serial_data.toFloat(); 
  
  
  if (Serial.available() > 0) {
    serial_data = Serial.parseFloat();
    float serial_float = serial_data.toFloat(); 
    calcRevsAngle(serial_float);
    moveThether();
//    Serial.println(serial_float);
//    if (serial_data == "1")
//    {
//      Serial.println(serial_data);
//      dxlRotate(true, 100);
//    }else if (serial_data == "2")
//    {
//      Serial.println(serial_data);
//      dxlRotate(false, 50);
//    } else if (serial_data == "0")
//    {
//      dxlRotate(true, 0);
//    }
  }
//  Serial.println("");
  delay(100);
}
