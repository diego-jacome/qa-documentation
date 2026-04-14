"""
Outlook Attachments — Descargar adjuntos de un correo y gestionar limpieza automática

Política de retención:
  - Adjuntos con más de MAX_AGE_DAYS días se eliminan automáticamente
  - Si la carpeta supera MAX_FOLDER_MB MB, se eliminan los más antiguos primero

Uso:
  python outlook_attachments.py --id <entryID>             # descargar adjuntos
  python outlook_attachments.py --cleanup                  # solo limpiar sin descargar
  python outlook_attachments.py --id <entryID> --no-images # excluir imágenes inline
"""
import argparse, os, shutil
from pathlib import Path
from datetime import datetime, timedelta
import win32com.client

# ── Política de retención ──────────────────────────────────────────────────────
MAX_AGE_DAYS   = 7     # días máximos que se conservan los adjuntos
MAX_FOLDER_MB  = 50    # tamaño máximo de la carpeta en MB
# ──────────────────────────────────────────────────────────────────────────────

BASE_DIR = Path(__file__).parent / 'attachments'

# Extensiones que se consideran imágenes inline (no adjuntos reales)
INLINE_EXTENSIONS = {'.gif', '.bmp'}


def get_outlook():
    try:
        return win32com.client.GetActiveObject("Outlook.Application")
    except Exception:
        raise RuntimeError("Outlook no está abierto. Ábrelo e intenta de nuevo.")


def cleanup(verbose=True):
    """Elimina adjuntos según la política de retención."""
    if not BASE_DIR.exists():
        return

    now      = datetime.now()
    cutoff   = now - timedelta(days=MAX_AGE_DAYS)
    deleted  = []

    # 1. Eliminar carpetas con más de MAX_AGE_DAYS días
    for folder in sorted(BASE_DIR.iterdir()):
        if not folder.is_dir():
            continue
        mtime = datetime.fromtimestamp(folder.stat().st_mtime)
        if mtime < cutoff:
            shutil.rmtree(folder)
            deleted.append(folder.name)

    # 2. Si aún supera el límite de tamaño, eliminar las más antiguas
    while _folder_size_mb(BASE_DIR) > MAX_FOLDER_MB:
        folders = sorted(BASE_DIR.iterdir(), key=lambda f: f.stat().st_mtime)
        if not folders:
            break
        oldest = folders[0]
        shutil.rmtree(oldest)
        deleted.append(oldest.name)

    if verbose:
        if deleted:
            print(f"Limpieza: {len(deleted)} carpeta(s) eliminada(s): {', '.join(deleted)}")
        else:
            size = _folder_size_mb(BASE_DIR)
            print(f"Limpieza: nada que eliminar. Carpeta: {size:.1f} MB / {MAX_FOLDER_MB} MB")


def _folder_size_mb(path: Path) -> float:
    if not path.exists():
        return 0.0
    total = sum(f.stat().st_size for f in path.rglob('*') if f.is_file())
    return total / (1024 * 1024)


def download_attachments(entry_id: str, no_images=False) -> list[Path]:
    """Descarga los adjuntos de un correo al disco."""
    outlook = get_outlook()
    ns      = outlook.GetNamespace("MAPI")
    item    = ns.GetItemFromID(entry_id)

    # Crear carpeta con nombre del remitente + fecha
    sender  = item.SenderName.split()[0].lower()  # primer nombre
    date_str = item.ReceivedTime.strftime('%Y%m%d')
    out_dir  = BASE_DIR / f"{sender}-{date_str}"
    out_dir.mkdir(parents=True, exist_ok=True)

    saved = []
    for att in item.Attachments:
        filename = att.FileName
        if not filename:
            continue
        ext = Path(filename).suffix.lower()
        if no_images and ext in INLINE_EXTENSIONS:
            continue

        dest = out_dir / filename
        # Evitar sobreescribir — agregar sufijo numérico si ya existe
        counter = 1
        while dest.exists():
            dest = out_dir / f"{Path(filename).stem}_{counter}{ext}"
            counter += 1

        att.SaveAsFile(str(dest))
        saved.append(dest)
        print(f"  Guardado: {dest.relative_to(BASE_DIR.parent.parent.parent)}")

    if not saved:
        print("  No hay adjuntos en este correo.")
    else:
        size = _folder_size_mb(BASE_DIR)
        print(f"\nCarpeta attachments: {size:.1f} MB / {MAX_FOLDER_MB} MB")

    return saved


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Descargar adjuntos de Outlook')
    parser.add_argument('--id',        type=str, help='EntryID del mensaje')
    parser.add_argument('--no-images', action='store_true', help='Excluir imágenes inline')
    parser.add_argument('--cleanup',   action='store_true', help='Solo ejecutar limpieza')
    args = parser.parse_args()

    # Limpieza automática siempre al correr
    cleanup(verbose=args.cleanup)

    if args.id:
        print(f"\nDescargando adjuntos...")
        download_attachments(args.id, no_images=args.no_images)
    elif not args.cleanup:
        parser.error("Especifica --id <entryID> o --cleanup")
