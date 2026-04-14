"""
Outlook Auth — Device Code Flow
Uso: python outlook_auth.py  (primera vez hace login, luego usa cache)
"""
import os, json
from pathlib import Path
import msal
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / '.env')

CLIENT_ID  = os.getenv('OUTLOOK_CLIENT_ID')
TENANT_ID  = os.getenv('OUTLOOK_TENANT_ID', 'common')
CACHE_FILE = Path(__file__).parent / 'token_cache.json'

SCOPES = [
    'Mail.Read',
    'Mail.Send',
    'Mail.ReadWrite',
    'User.Read',
]

def _load_cache():
    cache = msal.SerializableTokenCache()
    if CACHE_FILE.exists():
        cache.deserialize(CACHE_FILE.read_text())
    return cache

def _save_cache(cache):
    if cache.has_state_changed:
        CACHE_FILE.write_text(cache.serialize())

def get_token() -> str:
    """Devuelve un access token válido. Hace login interactivo si no hay cache."""
    if not CLIENT_ID:
        raise ValueError("Falta OUTLOOK_CLIENT_ID en .env")

    cache = _load_cache()
    app = msal.PublicClientApplication(
        client_id=CLIENT_ID,
        authority=f'https://login.microsoftonline.com/{TENANT_ID}',
        token_cache=cache,
    )

    # Intentar token silencioso desde cache
    accounts = app.get_accounts()
    if accounts:
        result = app.acquire_token_silent(SCOPES, account=accounts[0])
        if result and 'access_token' in result:
            _save_cache(cache)
            return result['access_token']

    # Login interactivo — Device Code Flow
    flow = app.initiate_device_flow(scopes=SCOPES)
    if 'user_code' not in flow:
        raise RuntimeError(f"No se pudo iniciar Device Flow: {flow}")

    print("\n" + "="*60)
    print("LOGIN REQUERIDO (solo una vez)")
    print(f"  1. Abre: {flow['verification_uri']}")
    print(f"  2. Ingresa el código: {flow['user_code']}")
    print("="*60 + "\n")

    result = app.acquire_token_by_device_flow(flow)
    if 'access_token' not in result:
        raise RuntimeError(f"Login fallido: {result.get('error_description')}")

    _save_cache(cache)
    print("Login exitoso. Token guardado en cache.")
    return result['access_token']


if __name__ == '__main__':
    token = get_token()
    print(f"\nToken obtenido correctamente (primeros 20 chars): {token[:20]}...")
