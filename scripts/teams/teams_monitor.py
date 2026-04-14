#!/usr/bin/env python3
"""
Teams Monitor — polling de canales y chats de Microsoft Teams via m365 CLI.

Uso:
  python teams_monitor.py                     # Monitorear (polling)
  python teams_monitor.py --setup             # Guia de configuracion inicial
  python teams_monitor.py --list-teams        # Listar equipos disponibles
  python teams_monitor.py --list-channels <teamId>  # Listar canales de un equipo
  python teams_monitor.py --list-chats        # Listar chats disponibles
  python teams_monitor.py --post "mensaje"    # Postear al destino default
  python teams_monitor.py --post "mensaje" --to-channel <teamId> <channelId>
  python teams_monitor.py --post "mensaje" --to-chat <chatId>
"""

import json
import subprocess
import sys
import os
import time
import datetime
import argparse
from pathlib import Path

CONFIG_FILE = Path(__file__).parent / "config.json"
STATE_FILE  = Path(__file__).parent / ".monitor_state.json"


# ─── Colores (sin dependencias) ───────────────────────────────────────────────
RESET   = "\033[0m"
BOLD    = "\033[1m"
RED     = "\033[91m"
YELLOW  = "\033[93m"
GREEN   = "\033[92m"
CYAN    = "\033[96m"
MAGENTA = "\033[95m"
DIM     = "\033[2m"


def c(text, color):
    return f"{color}{text}{RESET}"


# ─── Helpers m365 CLI ─────────────────────────────────────────────────────────

def m365(args: list, silent=False) -> list | dict | str | None:
    """Ejecuta un comando m365 y retorna el resultado parseado como JSON."""
    cmd = ["m365"] + args + ["--output", "json"]
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, encoding="utf-8", errors="replace"
        )
        if result.returncode != 0:
            if not silent:
                print(c(f"[m365 error] {result.stderr.strip()}", RED))
            return None
        text = result.stdout.strip()
        if not text:
            return None
        return json.loads(text)
    except FileNotFoundError:
        print(c("ERROR: 'm365' no encontrado. Instalar con: npm install -g @pnp/cli-microsoft365", RED))
        sys.exit(1)
    except json.JSONDecodeError:
        return result.stdout.strip()


def check_login() -> bool:
    status = m365(["status"], silent=True)
    if not status:
        return False
    if isinstance(status, dict):
        return status.get("connectedAs") is not None
    return False


def ensure_login():
    if not check_login():
        print(c("\nNo hay sesion activa en m365. Iniciando login...", YELLOW))
        print("Se abrira el navegador. Inicia sesion con tu cuenta corporativa.\n")
        subprocess.run(["m365", "login"])
        if not check_login():
            print(c("Login fallido. Intentar con: m365 login", RED))
            sys.exit(1)
        print(c("Login exitoso!\n", GREEN))


# ─── Estado de ultima lectura ─────────────────────────────────────────────────

def load_state() -> dict:
    if STATE_FILE.exists():
        with open(STATE_FILE, encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_state(state: dict):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)


# ─── Config ───────────────────────────────────────────────────────────────────

def load_config() -> dict:
    if not CONFIG_FILE.exists():
        print(c(f"No se encontro config.json en {CONFIG_FILE}", RED))
        sys.exit(1)
    with open(CONFIG_FILE, encoding="utf-8") as f:
        return json.load(f)


# ─── Importancia de un mensaje ────────────────────────────────────────────────

def is_important(msg: dict, rules: dict, my_name: str) -> tuple[bool, str]:
    """Retorna (es_importante, razon)."""
    body = (msg.get("body", {}).get("content") or "").lower()
    sender = (msg.get("from", {}).get("user", {}).get("displayName") or "").lower()

    # Mention al usuario
    if rules.get("always_important_if_mentioned", True):
        mentions = msg.get("mentions", []) or []
        for m in mentions:
            name = (m.get("mentioned", {}).get("user", {}).get("displayName") or "")
            if my_name.lower() in name.lower():
                return True, f"@mencion a {my_name}"

    # Keywords
    for kw in rules.get("keywords", []):
        if kw.lower() in body:
            return True, f'keyword: "{kw}"'

    return False, ""


# ─── Formateo de mensaje ──────────────────────────────────────────────────────

def format_msg(msg: dict, source_label: str, reason: str) -> str:
    sender = (msg.get("from", {}).get("user", {}).get("displayName") or "Sistema")
    ts_raw = msg.get("createdDateTime", "")
    try:
        ts = datetime.datetime.fromisoformat(ts_raw.replace("Z", "+00:00"))
        ts_str = ts.strftime("%H:%M:%S")
    except Exception:
        ts_str = ts_raw[:19]

    body = (msg.get("body", {}).get("content") or "").strip()
    # Limpiar HTML basico
    import re
    body = re.sub(r"<[^>]+>", "", body).strip()
    if len(body) > 300:
        body = body[:300] + "..."

    lines = [
        f"\n{c('━' * 60, CYAN)}",
        f" {c('★ IMPORTANTE', YELLOW+BOLD)} — {c(source_label, MAGENTA)} — {c(ts_str, DIM)}",
        f" {c('Por:', DIM)} {c(sender, BOLD)}",
        f" {c('Razon:', DIM)} {reason}",
        f" {c('Mensaje:', DIM)}",
        f"   {body}",
    ]
    return "\n".join(lines)


# ─── Poll canales ─────────────────────────────────────────────────────────────

def poll_channel(cfg_channel: dict, rules: dict, my_name: str, state: dict) -> list[str]:
    team_id    = cfg_channel["team_id"]
    channel_id = cfg_channel["channel_id"]
    label      = f"{cfg_channel.get('team_name','?')} > #{cfg_channel.get('channel_name','?')}"
    state_key  = f"channel_{channel_id}"

    messages = m365([
        "teams", "channel", "message", "list",
        "--teamId", team_id,
        "--channelId", channel_id,
    ], silent=True)

    if not messages or not isinstance(messages, list):
        return []

    last_seen = state.get(state_key)
    updates = []

    for msg in reversed(messages):  # del mas viejo al mas nuevo
        msg_id = msg.get("id", "")
        msg_ts = msg.get("createdDateTime", "")

        if last_seen and msg_ts <= last_seen:
            continue

        important, reason = is_important(msg, rules, my_name)
        if important:
            updates.append(format_msg(msg, label, reason))

    # Actualizar last_seen al mensaje mas reciente
    if messages:
        newest_ts = max(m.get("createdDateTime", "") for m in messages)
        state[state_key] = newest_ts

    return updates


# ─── Poll chats ───────────────────────────────────────────────────────────────

def poll_chat(cfg_chat: dict, rules: dict, my_name: str, state: dict) -> list[str]:
    chat_id = cfg_chat["chat_id"]
    label   = f"Chat: {cfg_chat.get('chat_name', chat_id[:20])}"
    state_key = f"chat_{chat_id}"

    messages = m365([
        "teams", "chat", "message", "list",
        "--chatId", chat_id,
    ], silent=True)

    if not messages or not isinstance(messages, list):
        return []

    last_seen = state.get(state_key)
    updates = []

    for msg in reversed(messages):
        msg_id = msg.get("id", "")
        msg_ts = msg.get("createdDateTime", "")

        if last_seen and msg_ts <= last_seen:
            continue

        important, reason = is_important(msg, rules, my_name)
        if important:
            updates.append(format_msg(msg, label, reason))

    if messages:
        newest_ts = max(m.get("createdDateTime", "") for m in messages)
        state[state_key] = newest_ts

    return updates


# ─── Acciones CLI ─────────────────────────────────────────────────────────────

def cmd_list_teams():
    ensure_login()
    print(c("\nEquipos disponibles:\n", CYAN + BOLD))
    teams = m365(["teams", "team", "list"])
    if not teams:
        print(c("No se encontraron equipos o error al obtener.", YELLOW))
        return
    for t in teams:
        print(f"  {c(t.get('id',''), DIM)}  {c(t.get('displayName',''), BOLD)}")
    print()


def cmd_list_channels(team_id: str):
    ensure_login()
    print(c(f"\nCanales del equipo {team_id}:\n", CYAN + BOLD))
    channels = m365(["teams", "channel", "list", "--teamId", team_id])
    if not channels:
        print(c("No se encontraron canales.", YELLOW))
        return
    for ch in channels:
        print(f"  {c(ch.get('id',''), DIM)}  {c(ch.get('displayName',''), BOLD)}")
    print()


def cmd_list_chats():
    ensure_login()
    print(c("\nChats disponibles:\n", CYAN + BOLD))
    chats = m365(["teams", "chat", "list"])
    if not chats:
        print(c("No se encontraron chats.", YELLOW))
        return
    for ch in chats:
        members = ", ".join(
            m.get("displayName", "") for m in (ch.get("members") or [])
        )
        print(f"  {c(ch.get('id',''), DIM)}")
        print(f"    {c(ch.get('topic') or members or '(sin nombre)', BOLD)}")
    print()


def cmd_post(message: str, to_type: str, team_id: str | None, channel_id: str | None, chat_id: str | None):
    ensure_login()
    cfg = load_config()

    if to_type == "channel" or (to_type is None and cfg["post_targets"]["default_type"] == "channel"):
        tid = team_id or cfg["post_targets"].get("default_team_id")
        cid = channel_id or cfg["post_targets"].get("default_channel_id")
        if not tid or not cid:
            print(c("Falta teamId o channelId. Configura post_targets en config.json o pasa --to-channel.", RED))
            return
        result = m365(["teams", "channel", "message", "send",
                        "--teamId", tid,
                        "--channelId", cid,
                        "--message", message])
        if result is not None:
            print(c(f"\nMensaje enviado al canal.", GREEN))
    else:
        cid = chat_id or cfg["post_targets"].get("default_chat_id")
        if not cid:
            print(c("Falta chatId. Configura post_targets en config.json o pasa --to-chat.", RED))
            return
        result = m365(["teams", "chat", "message", "send",
                        "--chatId", cid,
                        "--message", message])
        if result is not None:
            print(c(f"\nMensaje enviado al chat.", GREEN))


def cmd_setup():
    print(c("\n=== SETUP DEL TEAMS MONITOR ===\n", CYAN + BOLD))
    print("Pasos:")
    print(f"  1. Login:           {c('m365 login', YELLOW)}")
    print(f"  2. Listar equipos:  {c('python teams_monitor.py --list-teams', YELLOW)}")
    print(f"  3. Listar canales:  {c('python teams_monitor.py --list-channels <teamId>', YELLOW)}")
    print(f"  4. Listar chats:    {c('python teams_monitor.py --list-chats', YELLOW)}")
    print(f"  5. Editar:          {c('scripts/teams/config.json', YELLOW)} con los IDs obtenidos")
    print(f"  6. Monitorear:      {c('python teams_monitor.py', YELLOW)}\n")
    print(f"Para postear:")
    print(f"  {c('python teams_monitor.py --post \"Hola desde el script\"', YELLOW)}")
    print(f"  {c('python teams_monitor.py --post \"mensaje\" --to-channel <teamId> <channelId>', YELLOW)}")
    print(f"  {c('python teams_monitor.py --post \"mensaje\" --to-chat <chatId>', YELLOW)}\n")


# ─── Loop principal ───────────────────────────────────────────────────────────

def run_monitor():
    ensure_login()
    cfg = load_config()
    rules   = cfg["importance_rules"]
    my_name = cfg.get("my_display_name", "")
    interval = cfg.get("poll_interval_seconds", 30)

    channels = [c for c in cfg.get("channels", []) if c.get("enabled", True)]
    chats    = [c for c in cfg.get("chats", []) if c.get("enabled", True)]

    if not channels and not chats:
        print(c("\nNo hay canales ni chats habilitados en config.json.", YELLOW))
        print(f"Ejecuta {c('python teams_monitor.py --setup', CYAN)} para ver las instrucciones.\n")
        return

    print(c(f"\n=== TEAMS MONITOR iniciado ===", GREEN + BOLD))
    print(f"  Canales: {len(channels)}  |  Chats: {len(chats)}  |  Intervalo: {interval}s")
    print(f"  Mostrar solo mensajes importantes (keywords + @menciones)")
    print(f"  {c('Ctrl+C para detener', DIM)}\n")

    state = load_state()

    # Primera corrida: solo marcar posicion actual, no mostrar backlog
    first_run = not bool(state)
    if first_run:
        print(c("Primera ejecucion: marcando posicion actual (no se muestran mensajes viejos)...", DIM))
        for ch in channels:
            if ch.get("enabled", True):
                poll_channel(ch, rules, my_name, state)
        for cht in chats:
            if cht.get("enabled", True):
                poll_chat(cht, rules, my_name, state)
        save_state(state)
        print(c(f"Listo. Esperando nuevos mensajes cada {interval}s...\n", GREEN))

    try:
        while True:
            updates = []
            for ch in channels:
                updates += poll_channel(ch, rules, my_name, state)
            for cht in chats:
                updates += poll_chat(cht, rules, my_name, state)

            save_state(state)

            if updates:
                for u in updates:
                    print(u)
                print()
            else:
                now = datetime.datetime.now().strftime("%H:%M:%S")
                print(c(f"[{now}] Sin novedades importantes...", DIM), end="\r")

            time.sleep(interval)

    except KeyboardInterrupt:
        print(c("\n\nMonitor detenido.\n", YELLOW))
        save_state(state)


# ─── Entry point ──────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Teams Monitor via m365 CLI")
    parser.add_argument("--setup",         action="store_true", help="Guia de configuracion inicial")
    parser.add_argument("--list-teams",    action="store_true", help="Listar equipos")
    parser.add_argument("--list-channels", metavar="TEAM_ID",   help="Listar canales de un equipo")
    parser.add_argument("--list-chats",    action="store_true", help="Listar chats")
    parser.add_argument("--post",          metavar="MENSAJE",   help="Postear mensaje")
    parser.add_argument("--to-channel",    nargs=2, metavar=("TEAM_ID", "CHANNEL_ID"), help="Destino canal")
    parser.add_argument("--to-chat",       metavar="CHAT_ID",   help="Destino chat")

    args = parser.parse_args()

    if args.setup:
        cmd_setup()
    elif args.list_teams:
        cmd_list_teams()
    elif args.list_channels:
        cmd_list_channels(args.list_channels)
    elif args.list_chats:
        cmd_list_chats()
    elif args.post:
        to_type    = None
        team_id    = args.to_channel[0] if args.to_channel else None
        channel_id = args.to_channel[1] if args.to_channel else None
        chat_id    = args.to_chat
        if args.to_chat:
            to_type = "chat"
        elif args.to_channel:
            to_type = "channel"
        cmd_post(args.post, to_type, team_id, channel_id, chat_id)
    else:
        run_monitor()


if __name__ == "__main__":
    main()
