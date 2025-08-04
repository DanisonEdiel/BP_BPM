import requests

KEYCLOAK_TOKEN_URL = "http://localhost:18080/auth/realms/camunda-platform/protocol/openid-connect/token"
OPERATE_API_BASE = "http://localhost:8081"

CLIENT_ID = "operate"
CLIENT_SECRET = "XALaRPl5qwTEItdwCMiPS62nVpKs7dL7"

def get_access_token():
    """
    Genera un token de acceso con client_credentials.
    """
    data = {
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    }
    response = requests.post(KEYCLOAK_TOKEN_URL, data=data)
    response.raise_for_status()
    return response.json()["access_token"]

def search_process_definitions():
    """
    Busca las definiciones de procesos en Operate.
    """
    token = get_access_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    response = requests.post(f"{OPERATE_API_BASE}/v1/process-definitions/search", headers=headers, json={})
    response.raise_for_status()
    return response.json()

if __name__ == "__main__":
    procesos = search_process_definitions()
    print(procesos)
