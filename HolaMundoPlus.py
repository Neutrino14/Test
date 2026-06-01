#!/usr/bin/env python3
"""
Hola mundo + info del sistema (pensado para Jetson Orin Nano, pero sirve en general)
"""

import os
import sys
import platform
import shutil
import subprocess
from datetime import datetime

def leer_archivo_si_existe(ruta):
    try:
        with open(ruta, "r", encoding="utf-8", errors="ignore") as f:
            return f.read().strip()
    except FileNotFoundError:
        return None
    except PermissionError:
        return "Permiso denegado"
    except Exception as e:
        return f"Error: {e}"

def ejecutar_cmd(cmd):
    try:
        out = subprocess.check_output(cmd, shell=True, text=True, stderr=subprocess.STDOUT)
        return out.strip()
    except subprocess.CalledProcessError as e:
        return f"Error ejecutando '{cmd}': {e.output.strip()}"
    except FileNotFoundError:
        return "Comando no encontrado"
    except Exception as e:
        return f"Error: {e}"

def info_python():
    print("=== PYTHON ===")
    print(f"Versión: {sys.version}")
    print(f"Ejecutable: {sys.executable}")
    print(f"Plataforma: {sys.platform}")
    print(f"Rutas de búsqueda (sys.path):")
    for p in sys.path:
        print(f"  - {p}")
    print()

def info_sistema_basica():
    print("=== SISTEMA BÁSICO ===")
    print(f"Sistema operativo: {platform.system()}")
    print(f"Nombre del nodo: {platform.node()}")
    print(f"Release: {platform.release()}")
    print(f"Versión: {platform.version()}")
    print(f"Arquitectura: {platform.machine()}")
    print(f"Procesador (platform.processor): {platform.processor()}")
    print(f"Información completa: {platform.platform()}")
    print()

def info_cpu_mem():
    print("=== CPU Y MEMORIA (aprox) ===")
    # CPU
    cpuinfo = leer_archivo_si_existe("/proc/cpuinfo")
    if cpuinfo:
        print("Contenido de /proc/cpuinfo (recortado a 40 líneas):")
        lineas = cpuinfo.splitlines()
        for linea in lineas[:40]:
            print("  " + linea)
        if len(lineas) > 40:
            print("  ... (recortado)")
    else:
        print("No se pudo leer /proc/cpuinfo")

    print()
    # Memoria
    meminfo = leer_archivo_si_existe("/proc/meminfo")
    if meminfo:
        print("Contenido de /proc/meminfo (recortado a 25 líneas):")
        lineas = meminfo.splitlines()
        for linea in lineas[:25]:
            print("  " + linea)
        if len(lineas) > 25:
            print("  ... (recortado)")
    else:
        print("No se pudo leer /proc/meminfo")
    print()

def info_gpu_jetson():
    print("=== INFO JETSON / GPU (si aplica) ===")
    # En Jetson suele existir /etc/nv_tegra_release
    nv_tegra = leer_archivo_si_existe("/etc/nv_tegra_release")
    if nv_tegra:
        print("Contenido de /etc/nv_tegra_release:")
        print("  " + nv_tegra.replace("\n", "\n  "))
    else:
        print("No se encontró /etc/nv_tegra_release (puede no ser un Jetson o falta el archivo).")

    # L4T version
    l4t = leer_archivo_si_existe("/etc/nv_tegra_release") or leer_archivo_si_existe("/etc/lsb-release")
    if l4t:
        print("\nPosible info de L4T / distribución:")
        print("  " + l4t.replace("\n", "\n  "))

    # tegrastats (si existe)
    ruta_tegrastats = shutil.which("tegrastats")
    if ruta_tegrastats:
        print("\nSalida rápida de 'tegrastats' (1 muestra):")
        print("  (Esto puede tardar un segundo...)")
        salida = ejecutar_cmd("tegrastats --interval 1000 --count 1")
        print("  " + salida.replace("\n", "\n  "))
    else:
        print("\nNo se encontró el comando 'tegrastats' en el PATH.")

    print()

def info_disco():
    print("=== DISCO ===")
    try:
        statvfs = os.statvfs("/")
        total = statvfs.f_frsize * statvfs.f_blocks
        libre = statvfs.f_frsize * statvfs.f_bfree
        usado = total - libre

        def fmt_bytes(b):
            for unidad in ["B", "KB", "MB", "GB", "TB"]:
                if b < 1024:
                    return f"{b:.2f} {unidad}"
                b /= 1024
            return f"{b:.2f} PB"

        print(f"Total: {fmt_bytes(total)}")
        print(f"Usado: {fmt_bytes(usado)}")
        print(f"Libre: {fmt_bytes(libre)}")
    except Exception as e:
        print(f"No se pudo obtener info de disco: {e}")
    print()

def info_red():
    print("=== RED (básico) ===")
    # IPs rápidas con 'ip addr' o 'ifconfig'
    salida_ip = ejecutar_cmd("ip addr")
    if "Comando no encontrado" in salida_ip:
        salida_ip = ejecutar_cmd("ifconfig")
        print("Salida de 'ifconfig' (recortada a 40 líneas):")
    else:
        print("Salida de 'ip addr' (recortada a 40 líneas):")

    lineas = salida_ip.splitlines()
    for linea in lineas[:40]:
        print("  " + linea)
    if len(lineas) > 40:
        print("  ... (recortado)")
    print()

def info_paquetes_basicos():
    print("=== VERSIONES DE COSAS COMUNES (si están instaladas) ===")
    comandos = {
        "python3": "python3 --version",
        "pip3": "pip3 --version",
        "gcc": "gcc --version",
        "g++": "g++ --version",
        "cmake": "cmake --version",
        "docker": "docker --version",
        "nvidia-smi": "nvidia-smi",
    }

    for nombre, cmd in comandos.items():
        print(f"- {nombre}:")
        salida = ejecutar_cmd(cmd)
        lineas = salida.splitlines()
        for linea in lineas[:5]:
            print("  " + linea)
        if len(lineas) > 5:
            print("  ... (recortado)")
        print()
    print()

def info_entorno():
    print("=== VARIABLES DE ENTORNO (recortadas) ===")
    for i, (k, v) in enumerate(sorted(os.environ.items())):
        if i >= 40:
            print("  ... (recortado)")
            break
        print(f"  {k}={v}")
    print()

def main():
    print("========================================")
    print("           HOLA MUNDO EN PYTHON         ")
    print("========================================")
    print(f"Fecha y hora: {datetime.now().isoformat()}")
    print()

    info_python()
    info_sistema_basica()
    info_cpu_mem()
    info_gpu_jetson()
    info_disco()
    info_red()
    info_paquetes_basicos()
    info_entorno()

    print("Fin. 😄")

if __name__ == "__main__":
    main()
