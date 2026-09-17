# YU'AM — BIONEXO (prototipo v1.0)

> ⚠️ **Prototipo funcional v1.0.** Este repositorio contiene el prototipo de
> monitoreo de calidad de aire desarrollado bajo el nombre de código
> **BIONEXO**, como primera iteración del programa **YU'AM v2.0**
> (fotobiorreactores). El hardware, los umbrales de clasificación y el
> dashboard pueden cambiar. Se comparte para revisión técnica y
> retroalimentación de evaluadores externos.

Red de bio-monitoreo ambiental: un nodo sensor (Snapino + MQ-135) mide la
calidad del aire cada 30 segundos, un puente en Python publica las lecturas en
Supabase y un dashboard web las visualiza en tiempo casi real.

## Arquitectura

```
MQ-135 → Snapino/Arduino (serial 9600) → backend/bionexo_bridge.py
    → Supabase (tabla mediciones_aire) → frontend/index.html (Netlify)
```

## Estructura del repositorio

```
firmware/bionexo_node/bionexo_node.ino  # Firmware Arduino (lectura cada 30 s)
backend/bionexo_bridge.py               # Puente serial → Supabase (oficial)
backend/requirements.txt                # Dependencias Python fijadas
backend/Containerfile                   # Imagen Podman/Docker
backend/.env.example                    # Plantilla (copiar como .env, no subir)
frontend/index.html                     # Dashboard oficial (publish = frontend)
frontend/config.example.js              # Plantilla de window.__ENV__ (copiar como env.js)
netlify.toml                            # Despliegue: genera frontend/env.js en el build
RECOMENDACIONES.txt                     # Notas de mantenimiento (español)
```

## 1. Firmware (Arduino IDE)

1. Abre `firmware/bionexo_node/bionexo_node.ino` en Arduino IDE.
   (La carpeta debe llamarse igual que el `.ino`; no la renombres.)
2. Placa: la correspondiente a tu módulo **Snapino** (compatible Arduino).
   Si usas ESP32, selecciona tu modelo exacto en *Herramientas → Placa*.
3. Puerto: selecciona el puerto serial del módulo
   (*Herramientas → Puerto*, ej. `COM4` en Windows).
4. Velocidad: el firmware usa **9600 baudios**; no requiere librerías externas.
5. Sube el sketch y abre el *Monitor Serie* a 9600 para verificar que emite
   un entero por línea cada ~30 segundos. **Cierra el Monitor Serie** antes de
   arrancar el backend (el puerto no puede estar abierto dos veces).

## 2. Backend

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env   # en Windows: copy .env.example .env — y llena tus valores
python bionexo_bridge.py
```

Con Podman:

```bash
podman machine start
podman build -f backend/Containerfile -t bionexo-bridge .
podman run --env-file backend/.env bionexo-bridge
```

Sin `SUPABASE_URL`/`SUPABASE_KEY` el programa termina de inmediato
(fail-fast) indicando cómo crear el `.env`. Nunca pegues la key en el código.

## 3. Frontend

**Despliegue (Netlify):** publish directory `frontend`. Define las variables
`SUPABASE_URL` y `SUPABASE_KEY` en *Site settings → Environment variables*;
el `command` de `netlify.toml` genera `frontend/env.js` automáticamente
inyectándolas en `window.__ENV__`.

**Local:** el dashboard lee `window.__ENV__`, así que genera el archivo antes
de abrirlo:

```bash
cp frontend/config.example.js frontend/env.js  # y llena tus valores
# luego abre frontend/index.html en el navegador
```

Sin `frontend/env.js` verás el aviso "Sin config" en lugar de datos.
(`frontend/env.js` está en `.gitignore`: nunca se sube al repo.)

## 4. Base de datos (Supabase)

- Tabla `mediciones_aire(valor_ppm, estado, created_at)`: **no renombrar**.
- Intervalo del sensor: 30 s fijos. Umbrales: Óptimo <200, Moderado <400, Alerta ≥400.
- El dashboard normaliza valores históricos (`Optimo`, `Elevado`, `Peligro`)
  a los estados actuales sin modificar la base de datos.
- **RLS recomendado** (la key publishable es visible en el navegador, esta es
  la verdadera defensa: lectura pública, escritura solo del backend):

```sql
ALTER TABLE mediciones_aire ENABLE ROW LEVEL SECURITY;
CREATE POLICY "lectura publica" ON mediciones_aire
  FOR SELECT USING (true);
-- No crees policy de INSERT para el rol anon: solo el backend escribe,
-- usando una key con permiso de inserción desde el servidor.
```

## Seguridad

- **Ningún secreto vive en el código.** La API key solo existe en
  `backend/.env` (local, ignorado por git) y en las Environment Variables
  de Netlify.
- `backend/.env`, `frontend/env.js`, `.venv/`, `node_modules/`, `dist/` y
  `__pycache__/` están en `.gitignore`.
