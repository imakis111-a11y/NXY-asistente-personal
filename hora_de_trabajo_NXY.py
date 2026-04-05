#!/usr/bin/env python3
"""
NXY — Sistema de asistencia personal · Windows Edition.

Disparadores:
  • Voz: di «es hora de trabajar»
  • Desbloqueo del PC (automático)

Comportamiento:
  • Se ejecuta invisible en segundo plano
  • Si en 20 minutos no se activa, se cierra solo
  • Después de ejecutar la secuencia, se cierra solo
  • El Programador de tareas lo relanza al iniciar/despertar/desbloquear

Dependencias:
    pip install sounddevice numpy pyttsx3 pywin32 vosk
"""

import os
import sys
import time
import threading
import subprocess
import webbrowser
import ctypes
import ctypes.wintypes
import logging

import numpy as np
import sounddevice as sd
import pyttsx3

try:
    import win32gui
    import win32con
    WIN32_AVAILABLE = True
except ImportError:
    WIN32_AVAILABLE = False

# ── Log silencioso a archivo (sin ventana CMD) ────────────────────────────────
LOG_PATH = os.path.join(os.path.expanduser("~"), "Desktop", "nxy_log.txt")
logging.basicConfig(
    filename=LOG_PATH,
    level=logging.INFO,
    format="%(asctime)s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    encoding="utf-8",
)
log = logging.info


# ══════════════════════════════════════════════════════════════════════════════
#  ★ CONFIGURACIÓN
# ══════════════════════════════════════════════════════════════════════════════

SAMPLE_RATE     = 44100
NXY_NAME        = "Nxy"
YOUTUBE_URL     = "https://www.youtube.com/watch?v=pAgnJDJN4VA"
MENSAJE         = f"Bienvenido a casa, señor Fer. {NXY_NAME} en línea y lista para asistirle."
NEW_PROJECT     = os.path.expanduser(r"~\Desktop\nuevo_proyecto")

CLAUDE_URL      = "https://claude.ai"                                  # Claude en navegador
CURSOR_PATH     = r"C:\Users\imaki\AppData\Local\Programs\cursor\Cursor.exe"  # ← ajusta si es diferente
OPERA_PATH      = r"C:\Users\imaki\AppData\Local\Programs\Opera GX\launcher.exe"  # ← Opera GX

VOSK_MODEL      = r"C:\Users\imaki\Downloads\vosk-model-small-es-0.42"
FRASE_CLAVE     = "es hora de trabajar"

VOLUMEN_NXY     = 0.55
VOZ_ID          = "HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech\\Voices\\Tokens\\TTS_MS_ES-MX_SABINA_11.0"
TIMEOUT_MIN     = 20        # minutos sin activación → cierre automático
DEVICE_MIC      = 1         # dispositivo de micrófono (Intel Smart Sound)


# ══════════════════════════════════════════════════════════════════════════════
#  Estado global
# ══════════════════════════════════════════════════════════════════════════════

triggered  = False
was_locked = False
state_lock = threading.Lock()
inicio     = time.time()    # para el timeout de 20 min


def salir(motivo: str = ""):
    log(f"[NXY] Cerrando — {motivo}")
    os._exit(0)


# ══════════════════════════════════════════════════════════════════════════════
#  🔊  MOTOR DE SONIDO NXY
# ══════════════════════════════════════════════════════════════════════════════

def _play(audio: np.ndarray):
    sd.play(audio.astype(np.float32), samplerate=SAMPLE_RATE)
    sd.wait()

def _envelope(audio, attack=0.01, release=0.04):
    n = len(audio)
    att = min(int(SAMPLE_RATE * attack), n // 4)
    rel = min(int(SAMPLE_RATE * release), n // 4)
    env = np.ones(n)
    env[:att]  = np.linspace(0, 1, att)
    env[-rel:] = np.linspace(1, 0, rel)
    return audio * env

def _tono(freq, dur, vol=None):
    vol = vol or VOLUMEN_NXY
    t   = np.linspace(0, dur, int(SAMPLE_RATE * dur), endpoint=False)
    return _envelope(np.sin(2 * np.pi * freq * t) * vol)

def _sweep(f0, f1, dur, vol=None):
    vol = vol or VOLUMEN_NXY
    t   = np.linspace(0, dur, int(SAMPLE_RATE * dur), endpoint=False)
    k   = (f1 - f0) / dur
    return _envelope(np.sin(2 * np.pi * (f0 * t + 0.5 * k * t**2)) * vol)

def _sil(dur):
    return np.zeros(int(SAMPLE_RATE * dur))

def _cat(*p):
    return np.concatenate(p)


def sonido_boot_nxy():
    log("[NXY] Sonido de arranque")
    _play(_cat(_sweep(40,80,.18,VOLUMEN_NXY*.6), _sweep(80,200,.22,VOLUMEN_NXY*.8), _sweep(200,120,.15,VOLUMEN_NXY*.5)))
    time.sleep(0.05)
    _play(_cat(_sil(.05), _sweep(300,1800,.55), _sil(.08), _sweep(900,2400,.30,VOLUMEN_NXY*.75), _sil(.05)))
    for f in (1047, 1319, 1568):
        _play(_cat(_tono(f,.09), _sil(.04)))
    time.sleep(0.06)
    dur = 0.55
    t   = np.linspace(0, dur, int(SAMPLE_RATE * dur), endpoint=False)
    _play(_envelope((np.sin(2*np.pi*880*t)+np.sin(2*np.pi*1100*t)+np.sin(2*np.pi*1320*t))/3*VOLUMEN_NXY, .02, .20))
    time.sleep(0.1)

def sonido_cierre():
    _play(_cat(_sweep(1400,600,.35,VOLUMEN_NXY*.5), _sil(.05), _tono(500,.12,VOLUMEN_NXY*.35)))


# ══════════════════════════════════════════════════════════════════════════════
#  🔐  Monitor de bloqueo / desbloqueo
# ══════════════════════════════════════════════════════════════════════════════

def is_workstation_locked() -> bool:
    user32 = ctypes.windll.user32
    hDesk  = user32.OpenInputDesktop(0, False, ctypes.wintypes.DWORD(0x0100))
    if hDesk:
        user32.CloseDesktop(hDesk)
        return False
    return True


def monitor_lock_state():
    global triggered, was_locked
    was_locked = is_workstation_locked()
    log(f"[NXY] Estado inicial: {'bloqueado' if was_locked else 'desbloqueado'}")
    while True:
        time.sleep(0.5)
        ahora_bloqueado = is_workstation_locked()
        if was_locked and not ahora_bloqueado:
            with state_lock:
                if not triggered:
                    log("[NXY] PC desbloqueado — disparando secuencia")
                    triggered = True
                    threading.Thread(target=secuencia_bienvenida, daemon=True).start()
        was_locked = ahora_bloqueado


# ══════════════════════════════════════════════════════════════════════════════
#  🎙️  Escucha de voz (Vosk, sin internet)
# ══════════════════════════════════════════════════════════════════════════════

def escuchar_frase():
    from vosk import Model, KaldiRecognizer
    import json

    log("[NXY] Cargando modelo Vosk…")
    model = Model(VOSK_MODEL)
    rec   = KaldiRecognizer(model, SAMPLE_RATE)
    log(f"[NXY] Escuchando — frase clave: «{FRASE_CLAVE}»")

    with sd.RawInputStream(device=DEVICE_MIC, samplerate=SAMPLE_RATE,
                           blocksize=8000, dtype="int16", channels=1) as mic:
        while True:
            # ── Timeout de 20 minutos ────────────────────────────────────────
            if (time.time() - inicio) > TIMEOUT_MIN * 60:
                salir("timeout de 20 minutos sin activación")

            data = mic.read(4000)[0]
            if rec.AcceptWaveform(bytes(data)):
                texto = json.loads(rec.Result()).get("text", "").lower()
                if texto:
                    log(f"[NXY] Escuché: «{texto}»")
                if FRASE_CLAVE in texto:
                    global triggered
                    with state_lock:
                        if not triggered:
                            log("[NXY] Frase detectada — iniciando secuencia")
                            triggered = True
                            threading.Thread(target=secuencia_bienvenida, daemon=True).start()


# ══════════════════════════════════════════════════════════════════════════════
#  🚀  Secuencia de bienvenida
# ══════════════════════════════════════════════════════════════════════════════

def secuencia_bienvenida():
    log("[NXY] ── SECUENCIA INICIADA ──")
    sonido_boot_nxy()
    hablar(MENSAJE)
    abrir_youtube()
    abrir_apps_lado_a_lado()
    sonido_cierre()
    log("[NXY] ── SECUENCIA COMPLETADA — cerrando ──")
    time.sleep(1)
    salir("secuencia completada")


def hablar(texto: str):
    log(f"[NXY] Voz: «{texto}»")
    try:
        engine = pyttsx3.init()
        engine.setProperty("voice", VOZ_ID)   # Microsoft Sabina — español México
        engine.setProperty("rate", 148)
        engine.say(texto)
        engine.runAndWait()
    except Exception as e:
        log(f"[NXY] Error TTS: {e}")


def abrir_youtube():
    log("[NXY] Abriendo YouTube")
    # Abre en Opera GX si está disponible, si no usa el navegador por defecto
    if os.path.isfile(OPERA_PATH):
        subprocess.Popen([OPERA_PATH, YOUTUBE_URL])
    else:
        webbrowser.open(YOUTUBE_URL)
    time.sleep(1.5)


def abrir_apps_lado_a_lado():
    sw, sh = obtener_resolucion_pantalla()
    mitad  = sw // 2
    os.makedirs(NEW_PROJECT, exist_ok=True)

    # ── Claude en Opera GX ───────────────────────────────────────────────────
    log("[NXY] Abriendo Claude en Opera GX")
    if os.path.isfile(OPERA_PATH):
        subprocess.Popen([OPERA_PATH, CLAUDE_URL])
    else:
        webbrowser.open(CLAUDE_URL)
    time.sleep(2.5)

    # ── Cursor ───────────────────────────────────────────────────────────────
    log("[NXY] Abriendo Cursor")
    if os.path.isfile(CURSOR_PATH):
        subprocess.Popen([CURSOR_PATH, NEW_PROJECT])
    else:
        log("[NXY] ⚠️  Cursor no encontrado — ajusta CURSOR_PATH")
    time.sleep(2.5)

    if not WIN32_AVAILABLE:
        return

    # ── Organiza ventanas lado a lado ────────────────────────────────────────
    log("[NXY] Organizando ventanas")
    time.sleep(1.0)
    colocar_ventana("Opera",  x=0,     y=0, ancho=mitad, alto=sh)
    colocar_ventana("Cursor", x=mitad, y=0, ancho=mitad, alto=sh)


# ══════════════════════════════════════════════════════════════════════════════
#  🛠️  Utilidades Windows
# ══════════════════════════════════════════════════════════════════════════════

def obtener_resolucion_pantalla():
    try:
        u = ctypes.windll.user32
        return u.GetSystemMetrics(0), u.GetSystemMetrics(1)
    except Exception:
        return 1920, 1080


def colocar_ventana(titulo, x, y, ancho, alto):
    if not WIN32_AVAILABLE:
        return
    hwnd = None
    def cb(h, _):
        nonlocal hwnd
        if hwnd:
            return
        try:
            if titulo.lower() in win32gui.GetWindowText(h).lower() and win32gui.IsWindowVisible(h):
                hwnd = h
        except Exception:
            pass
    win32gui.EnumWindows(cb, None)
    if hwnd:
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        win32gui.SetWindowPos(hwnd, win32con.HWND_TOP, x, y, ancho, alto, win32con.SWP_SHOWWINDOW)
        log(f"[NXY] Ventana '{titulo}' → ({x},{y}) {ancho}×{alto}")
    else:
        log(f"[NXY] ⚠️  Ventana '{titulo}' no encontrada")


# ══════════════════════════════════════════════════════════════════════════════
#  ▶  MAIN
# ══════════════════════════════════════════════════════════════════════════════

def main():
    log("=" * 50)
    log(f"[NXY] Iniciando — timeout {TIMEOUT_MIN} min")

    threading.Thread(target=monitor_lock_state, daemon=True).start()

    try:
        escuchar_frase()
    except KeyboardInterrupt:
        salir("interrupción manual")


if __name__ == "__main__":
    main()