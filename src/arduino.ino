#include <Servo.h> // biblioteca para controlar os servos motores

Servo servos[5]; //vetor servos para guarda 
int angles[5]; // vetor para guarda os angulos dos servos(dedos) que sao recebidos pela ponta serial

void setup() {
  // aqui atraves de .attach conectar cada servo a um pino digital 
  Serial.begin(9600);
  servos[0].attach(3);  // polegar
  servos[1].attach(5);  // indicador
  servos[2].attach(6);  // médio
  servos[3].attach(9);  // anelar
  servos[4].attach(10); // mínimo
}

void loop() {
  if (Serial.available()) {//so executa ser algo for enviado
    String data = Serial.readStringUntil('\n');//pega tudo até encontrar um Enter
    int i = 0;
    char *token = strtok((char*)data.c_str(), ","); //separa a string em pedaços usando a vírgula como delimitador.
    while (token != NULL && i < 5) {
      angles[i] = atoi(token);// atoi transforma texto em número inteiro
      servos[i].write(angles[i]); //  move o servo para o ângulo correspondente
      token = strtok(NULL, ",");  // aqui ela vai pegando o próximo pedaço até não encontrar mais vírgulas (quando retorna NULL).
      i++;
    }
  }
}
