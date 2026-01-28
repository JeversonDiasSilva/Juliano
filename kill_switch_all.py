#!/usr/bin/env python3
# Curitiba – 28 de Janeiro de 2026
# Editor: Jeverson Dias da Silva /// @JCGAMESCLASSICOS
# Hotkey SELECT + START para matar processos switch

import os
import time
import sys
import subprocess
import xml.etree.ElementTree as ET
import pygame
import fcntl

# =====================================================
# CONFIGURAÇÕES
# =====================================================

ES_INPUT_CFG = "/userdata/system/configs/emulationstation/es_input.cfg"
LOCK_FILE = "/tmp/select_start_kill.lock"

PROCESSOS_PARA_MATAR = [
    "retroarch",
    "flycast",
    "dolphin-emu",
    "ppsspp",
    "sudachi",
    "eden",
    "yuzu",
    "suyu",
    "Ryujinx-Avalonia.AppImage",
    "Ryujinx.AppImage",
    "Ryujinx-LDN.AppImage",
    "firefox",
    
]

APPIMAGES_PARA_MATAR = [
    "/userdata/system/switch/Ryujinx.AppImage",
    "/userdata/system/switch/Ryujinx-Avalonia.AppImage",
    "/userdata/system/switch/Ryujinx-LDN.AppImage",
    "/userdata/system/switch/yuzu.AppImage",
    "/userdata/system/switch/yuzuEA.AppImage",
]

DELAY_LOOP = 0.01  # Delay do loop principal

# =====================================================
# FUNÇÕES AUXILIARES
# =====================================================

def garantir_instancia_unica():
    try:
        global lock_handle
        lock_handle = open(LOCK_FILE, "w")
        fcntl.lockf(lock_handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except IOError:
        print("[ERRO] Script já está rodando.")
        sys.exit(0)

def matar_processos():
    print("[HOTKEY] SELECT + START detectado!")

    # Processos padrão
    for proc in PROCESSOS_PARA_MATAR:
        subprocess.run(
            ["killall", "-9", proc],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

    # AppImages (Ryujinx / Yuzu)
    for app in APPIMAGES_PARA_MATAR:
        subprocess.run(
            ["pkill", "-9", "-f", app],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

    print("[HOTKEY] Todos os processos finalizados.")

def carregar_ids():
    select_ids = {}
    start_ids = {}

    if not os.path.exists(ES_INPUT_CFG):
        print("[ERRO] es_input.cfg não encontrado!")
        return select_ids, start_ids

    try:
        tree = ET.parse(ES_INPUT_CFG)
        root = tree.getroot()

        for inputConfig in root.findall("inputConfig"):
            name = inputConfig.attrib.get("deviceName", "").strip().lower()

            for inp in inputConfig.findall("input"):
                nome = inp.attrib.get("name", "").lower()
                id_btn = int(inp.attrib.get("id", -1))

                if nome == "select":
                    select_ids[name] = id_btn
                elif nome == "start":
                    start_ids[name] = id_btn

    except Exception as e:
        print(f"[ERRO] Falha ao ler XML: {e}")

    return select_ids, start_ids

# =====================================================
# MAIN
# =====================================================

def main():
    garantir_instancia_unica()

    pygame.init()
    pygame.joystick.init()

    select_ids, start_ids = carregar_ids()

    joysticks = {}
    last_joy_count = -1

    print("[INIT] Script SELECT + START iniciado.")

    while True:
        # Detecta conexão / desconexão de controles
        joy_count = pygame.joystick.get_count()
        if joy_count != last_joy_count:
            joysticks.clear()

            for i in range(joy_count):
                js = pygame.joystick.Joystick(i)
                js.init()
                name = js.get_name().strip().lower()

                if name in select_ids and name in start_ids:
                    joysticks[i] = {
                        "obj": js,
                        "name": name,
                        "select_id": select_ids[name],
                        "start_id": start_ids[name],
                        "combo_executado": False
                    }
                    print(f"[JOY] Detectado: {name}")
                else:
                    print(f"[JOY] Ignorado (sem mapeamento): {name}")

            last_joy_count = joy_count

        # Atualiza estado do joystick
        pygame.event.pump()

        # Verifica combo SELECT + START
        for js_data in joysticks.values():
            try:
                js = js_data["obj"]
                sel = js_data["select_id"]
                sta = js_data["start_id"]

                if js.get_button(sel) and js.get_button(sta):
                    if not js_data["combo_executado"]:
                        matar_processos()
                        js_data["combo_executado"] = True
                else:
                    js_data["combo_executado"] = False

            except pygame.error:
                pass

        time.sleep(DELAY_LOOP)

# =====================================================
# START
# =====================================================

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[SAÍDA] Encerrando script.")
    finally:
        pygame.quit()
