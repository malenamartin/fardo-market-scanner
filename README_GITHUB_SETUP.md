# Market Scanner – Setup en GitHub Actions

El script se ejecuta todos los días a las **8:00 AM** de forma automática en la nube de GitHub, sin necesidad de que tu computadora esté encendida.

---

## Requisitos previos

- Cuenta en [github.com](https://github.com) (gratuita)
- Git instalado en tu Mac ([descargar](https://git-scm.com/download/mac))

---

## Paso 1 — Crear el repositorio en GitHub

1. Ve a **github.com → New repository**
2. Ponle un nombre, por ejemplo: `market-scanner`
3. Márcalo como **Private** (para que tus reportes no sean públicos)
4. **No** marques "Add README" ni "Add .gitignore"
5. Haz clic en **Create repository**

---

## Paso 2 — Subir los archivos desde tu Mac

Abre la Terminal y ejecuta estos comandos **uno a uno**:

```bash
# Entrar a la carpeta del proyecto
cd /Users/malenamartin/Documents/Fardo_Scrip

# Inicializar Git
git init
git branch -M main

# Añadir todos los archivos
git add market_scanner.py requirements.txt .github/

# Primer commit
git commit -m "primer commit: market scanner con GitHub Actions"

# Conectar con tu repositorio (cambia TU_USUARIO y TU_REPO)
git remote add origin https://github.com/TU_USUARIO/TU_REPO.git

# Subir
git push -u origin main
```

> Si GitHub te pide usuario/contraseña, usa tu usuario de GitHub y como contraseña un **Personal Access Token** (ver Paso 3).

---

## Paso 3 — Crear un Personal Access Token (si te lo pide)

1. GitHub → **Settings → Developer settings → Personal access tokens → Tokens (classic)**
2. Clic en **Generate new token (classic)**
3. Marca el scope: **repo** (acceso completo al repositorio)
4. Copia el token y úsalo como contraseña en el paso anterior

---

## Paso 4 — Verificar que el workflow esté activo

1. Ve a tu repositorio en GitHub
2. Clic en la pestaña **Actions**
3. Deberías ver **"Daily Market Scanner"** en la lista de workflows
4. Para hacer una prueba inmediata: clic en el workflow → **Run workflow → Run workflow**

---

## Paso 5 — Activar notificaciones de fallo por email

GitHub envía un email automáticamente cuando un workflow falla.
Para asegurarte de que está activado:

1. GitHub → **Settings → Notifications**
2. En la sección **Actions** → marca **"Send notifications for failed workflows only"**
3. Guarda los cambios

Cuando el scanner falle recibirás un email con el asunto:
`[TU_REPO] Run failed: Daily Market Scanner`

---

## Ajustar la hora de ejecución

El archivo `.github/workflows/daily_scan.yml` usa cron en **UTC**.
Cambia la línea `cron:` según tu zona horaria:

| Ciudad            | Hora local | Cron (UTC)       |
|-------------------|------------|------------------|
| Madrid (invierno) | 8:00 AM    | `0 7 * * *`      |
| Madrid (verano)   | 8:00 AM    | `0 6 * * *`      |
| Ciudad de México  | 8:00 AM    | `0 14 * * *`     |
| Buenos Aires      | 8:00 AM    | `0 11 * * *`     |
| Bogotá / Lima     | 8:00 AM    | `0 13 * * *`     |

Edita el archivo, haz commit y push para que el cambio tome efecto.

---

## ¿Dónde están los reportes?

Después de cada ejecución el bot hace un commit automático con:

```
reportes/
  reporte_mercado_2026-03-17.txt
  reporte_mercado_2026-03-18.txt
  ...
reporte_mercado.txt   ← siempre el más reciente
```

Puedes verlos directamente en GitHub → pestaña **Code**.

---

## Estructura final del proyecto

```
Fardo_Scrip/
├── market_scanner.py               ← script principal
├── requirements.txt                ← dependencias Python
├── reporte_mercado.txt             ← último reporte generado
├── reportes/                       ← histórico de reportes
│   ├── reporte_mercado_2026-03-17.txt
│   └── ...
├── .github/
│   └── workflows/
│       └── daily_scan.yml          ← automatización GitHub Actions
└── README_GITHUB_SETUP.md          ← este archivo
```

---

## Preguntas frecuentes

**¿GitHub Actions es gratis?**
Sí. Los repositorios públicos tienen Actions ilimitado. Los privados tienen 2.000 minutos/mes gratis, y este workflow usa ~1-2 minutos al día (≈ 30-60 min/mes), bien dentro del límite.

**¿Puedo ejecutarlo manualmente?**
Sí. Ve a Actions → Daily Market Scanner → Run workflow.

**¿Qué pasa si el script falla?**
Recibirás un email de GitHub. El reporte del día anterior seguirá disponible en `reportes/`.
