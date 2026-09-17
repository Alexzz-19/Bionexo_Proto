// BIONEXO - Nodo sensor de calidad de aire v2.0
// Hardware: Snapino + MQ-135 en A0, LED estado en D13
// Protocolo: envia un entero por linea a 9600 baudios cada 30 segundos.
// El backend (bionexo_bridge.py) lo publica en Supabase mediciones_aire.

const int SENSOR_PIN = A0;
const int LED_STATUS = 13;
const unsigned long INTERVALO_MS = 30000; // 30 segundos fijos

void setup() {
  Serial.begin(9600);
  pinMode(LED_STATUS, OUTPUT);
}

void loop() {
  // Promedio de 5 lecturas para filtrar ruido electrico
  long sumaLecturas = 0;
  for (int i = 0; i < 5; i++) {
    sumaLecturas += analogRead(SENSOR_PIN);
    delay(50);
  }
  int valorPromedio = sumaLecturas / 5;

  digitalWrite(LED_STATUS, HIGH);
  delay(100);
  digitalWrite(LED_STATUS, LOW);

  Serial.println(valorPromedio);

  delay(INTERVALO_MS - 350); // 250ms de muestreo + 100ms LED = ~30s exactos
}
