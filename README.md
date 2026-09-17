# BIONEXO — Monitoreo de calidad de aire con MQ-135

> ⚠️ **Prototipo funcional (v2.0).** Proyecto en desarrollo activo: el hardware,
> los umbrales de clasificación y el dashboard pueden cambiar. Se comparte para
> revisión técnica y retroalimentación.

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
frontend/config.example.js              # Ejemplo de config window.__ENV__
netlify.toml                            # Configuración de despliegue
RECOMENDACIONES.txt                     # Notas de mantenimiento (español)
```

## Puesta en marcha

**1. Backend local:**
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env   # en Windows: copy .env.example .env — y llena tus valores
python bionexo_bridge.py
```

**2. Backend con Podman:**
```bash
podman machine start
podman build -f backend/Containerfile -t bionexo-bridge .
podman run --env-file backend/.env bionexo-bridge
```

**3. Frontend (Netlify):**
- Publish directory: `frontend`
- Variables de entorno: `SUPABASE_URL`, `SUPABASE_KEY`
- Genera `frontend/env.js` en el build:
  `window.__ENV__ = { SUPABASE_URL: '...', SUPABASE_KEY: '...' }`

## Seguridad

- **Ningún secreto vive en el código.** La API key solo existe en `backend/.env`
  (local, ignorado por git) y en las Environment Variables de Netlify.
- `backend/.env`, `frontend/env.js`, `.venv/` y `__pycache__/` están en `.gitignore`.
- Recomendado en Supabase: activar RLS en `mediciones_aire` — `SELECT` público,
  `INSERT` restringido (solo escribe el backend).

## Datos

- Tabla `mediciones_aire(valor_ppm, estado, created_at)`: **no renombrar**.
- Intervalo del sensor: 30 s fijos. Umbrales: Óptimo <200, Moderado <400, Alerta ≥400.
- El dashboard normaliza valores históricos (`Optimo`, `Elevado`, `Peligro`)
  a los estados actuales sin modificar la base de datos.
