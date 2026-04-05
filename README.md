# 🤖 NXY — Sistema de Asistencia Personal
> *Tu propia JARVIS personal para Windows. Dile "es hora de trabajar" y ella hace todo.*

---

## 📋 ¿Qué hace Nxy?

Cuando dices **"es hora de trabajar"** (o cuando desbloqueas tu PC), Nxy hace esto sola:

1. 🔊 Reproduce un sonido de arranque estilo Iron Man
2. 🗣️ Te da la bienvenida con voz femenina en español
3. 🎵 Abre YouTube con tu música favorita
4. 🤖 Abre Claude en tu navegador
5. 💻 Abre Cursor con tu carpeta de proyectos
6. 🪟 Acomoda las dos ventanas lado a lado automáticamente
7. ⏰ Si en 20 minutos no pasa nada, se cierra sola

Todo esto pasa **sin que abras nada**, corre invisible en segundo plano.

---

## 🗂️ Archivos que necesitas

```
📁 Tu carpeta (ejemplo: C:\Users\TuNombre\NXY\)
   ├── hora_de_trabajo_NXY.py   ← el cerebro de Nxy
   └── lanzar_nxy.vbs           ← el que la activa sin mostrar ventanas
```

> ⚠️ **MUY IMPORTANTE:** Los dos archivos deben estar en la misma carpeta siempre.

---

## 🛠️ INSTALACIÓN PASO A PASO

### PASO 1 — Instalar Python

1. Ve a 👉 [python.org/downloads](https://www.python.org/downloads/)
2. Descarga la versión más reciente
3. Ábrela y **MARCA** la casilla que dice **"Add Python to PATH"** antes de instalar
4. Clic en **Install Now**

> 💡 ¿Cómo sé si ya lo tengo? Abre CMD y escribe `python --version`. Si aparece un número, ya lo tienes.

---

### PASO 2 — Instalar las librerías

Abre **CMD** (busca "cmd" en el inicio de Windows) y copia esto exacto:

```
pip install sounddevice numpy pyttsx3 pywin32 vosk
```

Presiona Enter y espera a que termine. Puede tardar 1-2 minutos.

---

### PASO 3 — Descargar el modelo de voz (para que te entienda)

1. Ve a 👉 [alphacephei.com/vosk/models](https://alphacephei.com/vosk/models)
2. Busca **`vosk-model-small-es-0.42`** y descárgalo
3. Descomprímelo (clic derecho → Extraer aquí)
4. Mueve la carpeta a `C:\` para que quede así:

```
C:\vosk-model-small-es-0.42\
```

> ⚠️ Si al descomprimir quedó una carpeta dentro de otra (ej: `vosk-model-small-es-0.42\vosk-model-small-es-0.42\`) usa la ruta completa hasta donde están los archivos del modelo.

---

### PASO 4 — Poner tus datos en el script

Abre `hora_de_trabajo_NXY.py` con cualquier editor (Notepad, Cursor, VS Code) y busca la sección que dice `CONFIGURACIÓN`. Solo tienes que cambiar estas líneas:

```python
# ══════════════════════════════════════════════
#  ★ CONFIGURACIÓN — TODO LO QUE PUEDES CAMBIAR
# ══════════════════════════════════════════════

NXY_NAME    = "Nxy"          # ← El nombre de tu IA (puedes poner el que quieras)

MENSAJE     = "Bienvenido a casa, señor Fer. Nxy en línea y lista para asistirle."
# ↑ Lo que dice cuando arranca. Cambia "señor Fer" por tu nombre.

YOUTUBE_URL = "https://www.youtube.com/watch?v=pAgnJDJN4VA"
# ↑ El link de YouTube que quieres que abra. Copia el link de tu video/playlist.

CLAUDE_URL  = "https://claude.ai"
# ↑ Deja esto así a menos que quieras abrir otra página.

CURSOR_PATH = r"C:\Users\imaki\AppData\Local\Programs\cursor\Cursor.exe"
# ↑ La ruta donde está instalado Cursor en TU computadora.

OPERA_PATH  = r"C:\Users\imaki\AppData\Local\Programs\Opera GX\launcher.exe"
# ↑ La ruta donde está instalado Opera GX en TU computadora.

VOSK_MODEL  = r"C:\vosk-model-small-es-0.42"
# ↑ La ruta donde pusiste el modelo de voz.

FRASE_CLAVE = "es hora de trabajar"
# ↑ Lo que tienes que decir para activar a Nxy. Puedes cambiarlo.

TIMEOUT_MIN = 20
# ↑ Minutos de espera antes de cerrarse sola si no dices nada.

VOLUMEN_NXY = 0.55
# ↑ Volumen de los sonidos. Va de 0.0 (silencio) a 1.0 (máximo).

DEVICE_MIC  = 1
# ↑ El número de tu micrófono. Ver sección de solución de problemas si falla.
```

---

### PASO 5 — Encontrar las rutas de tus programas

**¿No sabes dónde está Cursor o Opera GX?** Abre CMD y escribe:

```
where cursor
```
```
where opera
```

Si no aparece nada, búscalo manualmente:
- Clic derecho en el ícono de Cursor → **Propiedades** → copia lo que dice en **Destino**
- Haz lo mismo con Opera GX

---

### PASO 6 — Configurar el Programador de tareas

Esto hace que Nxy arranque sola cada vez que inicias sesión.

1. Presiona `Win + R`, escribe `taskschd.msc`, presiona Enter
2. En el panel derecho clic en **"Create Basic Task"**
3. **Name:** `lanzador_nxy_trabajo` → Siguiente
4. **Trigger:** Selecciona **"When I log on"** → Siguiente
5. **Action:** Selecciona **"Start a program"** → Siguiente
6. Llena así:
   - **Program/script:** `wscript.exe`
   - **Add arguments:** `"C:\Users\TuNombre\NXY\lanzar_nxy.vbs"` ← pon tu ruta exacta
7. Clic en **Finish**
8. Busca la tarea en la lista → clic derecho → **Properties**
9. En la pestaña **General** marca **"Run with highest privileges"**
10. Clic **OK**

> ✅ Listo. Ahora cada vez que inicies sesión, Nxy arrancará sola en segundo plano.

---

## 🎨 PERSONALIZACIÓN — Hazla tuya

### Cambiar el nombre de la IA

```python
NXY_NAME = "Aria"      # o "JARVIS" o "Friday" o el que quieras
```

El nombre aparece en todos los mensajes del log y en la pantalla.

---

### Cambiar lo que dice al saludarte

```python
MENSAJE = "Buenos días, señor Fer. Todos los sistemas están operativos."
```

Puedes poner cualquier frase. Se la dirá en voz alta Sabina (voz española).

---

### Cambiar la frase de activación

```python
FRASE_CLAVE = "nxy despierta"   # o "buenos días" o lo que quieras
```

> 💡 Frases más cortas funcionan mejor. "nxy" sola también funciona.

---

### Cambiar el video de YouTube

1. Ve al video o playlist que quieras en YouTube
2. Copia el link de la barra del navegador
3. Pégalo aquí:

```python
YOUTUBE_URL = "https://www.youtube.com/watch?v=TU_VIDEO_AQUI"
```

---

### Cambiar el tiempo de espera antes de cerrarse

```python
TIMEOUT_MIN = 30    # espera 30 minutos antes de cerrarse
TIMEOUT_MIN = 5     # espera solo 5 minutos
```

---

### Cambiar el volumen de los sonidos

```python
VOLUMEN_NXY = 0.8   # más fuerte
VOLUMEN_NXY = 0.3   # más suave
VOLUMEN_NXY = 0.0   # sin sonido
```

---

### Cambiar la voz

Para ver qué voces tienes instaladas en tu PC, abre CMD y escribe:

```
python -c "import pyttsx3; e=pyttsx3.init(); [print(v.id, '|', v.name) for v in e.getProperty('voices')]"
```

Copia el texto largo que aparece antes del `|` de la voz que quieras y ponlo aquí:

```python
VOZ_ID = "HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech\\Voices\\Tokens\\TU_VOZ_AQUI"
```

**¿Quieres más voces en español?** Ve a:
`Configuración → Hora e idioma → Voz → Agregar voces` → busca Español México o España.

---

### Cambiar el proyecto que abre Cursor

```python
NEW_PROJECT = r"C:\Users\TuNombre\Desktop\mi_proyecto"
```

Cursor abrirá directamente esa carpeta cuando arranque.

---

## 🔍 VER QUÉ ESTÁ HACIENDO NXY

Nxy guarda un registro de todo lo que hace en un archivo de texto en tu escritorio:

```
C:\Users\TuNombre\Desktop\nxy_log.txt
```

Ábrelo si algo no funciona bien. Verás mensajes como:

```
2025-01-15 09:00:01  [Nxy] Iniciando — timeout 20 min
2025-01-15 09:00:03  [Nxy] Cargando modelo Vosk…
2025-01-15 09:00:08  [Nxy] Escuchando — frase clave: «es hora de trabajar»
2025-01-15 09:02:14  [Nxy] Escuché: «es hora de trabajar»
2025-01-15 09:02:14  [Nxy] Frase detectada — iniciando secuencia
2025-01-15 09:02:25  [Nxy] SECUENCIA COMPLETADA — cerrando
```

---

## ❓ SOLUCIÓN DE PROBLEMAS

### "No me entiende cuando hablo"

El modelo de voz puede tardar entre 15 y 40 segundos en cargar. Espera a ver en el log la línea:
```
[Nxy] Escuchando — frase clave: «es hora de trabajar»
```
Solo después de esa línea Nxy está lista para escucharte.

---

### "No detecta mi micrófono"

Abre CMD y ejecuta:
```
python -c "import sounddevice as sd; print(sd.query_devices())"
```
Busca en la lista el micrófono que quieres usar y anota su número (el que aparece al inicio). Luego cambia en el script:

```python
DEVICE_MIC = 1    # ← pon el número de tu micrófono aquí
```

---

### "Abre el navegador equivocado"

Cambia tu navegador por defecto en Windows:
`Configuración → Aplicaciones → Aplicaciones predeterminadas → Opera GX → Establecer como predeterminado`

---

### "Se abre dos veces"

Tienes Nxy configurada en dos lugares. Revisa:
1. `Win + R` → `shell:startup` → elimina cualquier acceso directo de Nxy
2. Deja solo la tarea en el Programador de tareas

---

### "No encuentro la ruta de mi programa"

Clic derecho en el ícono del programa → **Propiedades** → copia lo que dice en **Destino**.

---

### "El modelo Vosk no carga"

Revisa que la ruta en `VOSK_MODEL` sea exactamente donde están los archivos. Abre esa carpeta y verifica que adentro haya archivos como `am/`, `conf/`, `graph/`. Si hay otra carpeta adentro con el mismo nombre, usa esa ruta.

---

## 🚀 CÓMO FUNCIONA POR DENTRO (versión simple)

```
Nxy arranca sola al iniciar Windows
        ↓
Espera en silencio escuchando el micrófono
        ↓
¿Dijiste "es hora de trabajar"?  ──── NO ──→  ¿Pasaron 20 min? ──→ Se cierra
        │ SÍ
        ↓
Sonido de arranque Iron Man
        ↓
Voz de bienvenida (Sabina en español)
        ↓
Abre YouTube
        ↓
Abre Claude en Opera GX
        ↓
Abre Cursor con tu proyecto
        ↓
Acomoda las ventanas lado a lado
        ↓
Tono de cierre y se cierra sola
```

---

## 📦 DEPENDENCIAS

| Librería | Para qué sirve |
|---|---|
| `sounddevice` | Escucha el micrófono |
| `numpy` | Genera los sonidos de Iron Man |
| `pyttsx3` | La voz de Nxy |
| `pywin32` | Controla las ventanas de Windows |
| `vosk` | Entiende lo que dices (sin internet) |
| `vosk-model-small-es-0.42` | El cerebro del reconocimiento de voz en español |

Instala todo con un solo comando:
```
pip install sounddevice numpy pyttsx3 pywin32 vosk
```

---

---

## 💬 CONTACTO Y SOPORTE

¿Tienes dudas, encontraste un error o quieres una versión más personalizada de Nxy?

### 📸 Instagram
Escríbeme directo, estoy activo y respondo:

👉 **[@i_iron_fan](https://www.instagram.com/i_iron_fan)**

Puedo ayudarte con:
- 🛠️ Errores que no puedes resolver
- 🎨 Personalización avanzada (nuevos sonidos, frases, apps)
- 💡 Ideas para nuevas funciones
- 🤝 Colaboraciones o proyectos

---

### 🤖 Para dudas rápidas — usa Claude AI

Si tienes una duda simple sobre el código o un error que no entiendes, puedes resolverlo tú mismo en segundos:

👉 **[claude.ai](https://claude.ai)**

Copia el error que te aparece en pantalla, pégalo en Claude y pregunta:
> *"Tengo este error en mi script de Python, ¿qué significa y cómo lo soluciono?"*

Claude te lo explica paso a paso, en español, y gratis. 🚀

---

*Hecho con ❤️ — Nxy, tu asistente personal.*
