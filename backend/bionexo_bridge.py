"""BIONEXO - Puente serial -> Supabase (oficial).
Lee el sensor MQ-135 desde Arduino/Snapino por serial y publica
en la tabla mediciones_aire(valor_ppm, estado).

Configuracion por variables de entorno (.env). Mantiene fallback
a los valores historicos para no romper instalaciones existentes.
Intervalo del sensor: 30 segundos. Tabla Supabase: no renombrar.
"""
import os
import time
import serial
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

# Sin fallbacks con secretos: todo sale del entorno (backend/.env local,
# --env-file en Podman). Asi el repo puede publicarse sin filtrar keys.
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

PUERTO_SERIAL = os.getenv("SERIAL_PORT", "COM4")
BAUD_RATE = int(os.getenv("BAUD_RATE", "9600"))

if not SUPABASE_URL or not SUPABASE_KEY:
    raise SystemExit(
        "Falta configuracion: copia backend/.env.example como backend/.env "
        "y llena SUPABASE_URL y SUPABASE_KEY. Nunca pegues la key en el codigo."
    )

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def clasificar_calidad(valor):
    # Umbrales historicos: <200 Optimo, <400 Moderado, else Elevado/Alerta
    # Nombres normalizados para el dashboard: Óptimo / Moderado / Alerta
    if valor < 200:
        return "Óptimo"
    elif valor < 400:
        return "Moderado"
    else:
        return "Alerta"


def iniciar_puente():
    while True:
        try:
            print(f"Conectando al puerto {PUERTO_SERIAL} a {BAUD_RATE} baudios...")
            arduino = serial.Serial(PUERTO_SERIAL, BAUD_RATE, timeout=2)
            time.sleep(2)
            print("Conectado al Arduino exitosamente!")

            while True:
                if arduino.in_waiting > 0:
                    linea = arduino.readline().decode('utf-8', errors='ignore').strip()
                    if linea.isdigit():
                        valor = int(linea)
                        estado = clasificar_calidad(valor)

                        try:
                            supabase.table("mediciones_aire").insert(
                                {"valor_ppm": valor, "estado": estado}
                            ).execute()
                            print(f"Muestra recibida: {valor} | Estado: {estado}")
                            print("Guardado con exito en la nube!")
                            print("-" * 40)
                        except Exception as e_db:
                            print(f"Error de red/Supabase (reintentando en siguiente ciclo): {e_db}")

                    time.sleep(1)

        except (serial.SerialException, OSError):
            print("El Arduino se desconecto o el puerto no esta disponible. Reintentando en 5 segundos...")
            print("Asegurate de haber CERRADO el Monitor Serie en Arduino IDE.")
            time.sleep(5)
        except Exception as e:
            print(f"Error inesperado de red o sistema: {e}")
            print("Reiniciando bucle de conexion en 5 segundos...")
            time.sleep(5)


if __name__ == "__main__":
    iniciar_puente()
