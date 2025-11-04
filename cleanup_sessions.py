import os
import redis
import shutil

USER_FILES_DIR = '/tmp/rtt'
SESSION_PREFIX = 'rtt:'

r = redis.Redis(host='localhost', port=6379, db=0)

def cleanup_sessions():
    # 1. Obtener todas las claves activas en Redis con el prefijo configurado
    active_sessions = set()
    for key in r.scan_iter(f"{SESSION_PREFIX}*"):
        # Ejemplo: "rtt:be3b4c0f-86e1-4ad1-92ac-0b6f502c6b79"
        key_str = key.decode()
        session_id = key_str.replace(SESSION_PREFIX, '')
        active_sessions.add(session_id)

    print(f"Active sessions in Redis: {len(active_sessions)}")

    # 2. Recorrer los directorios locales
    for folder in os.listdir(USER_FILES_DIR):
        folder_path = os.path.join(USER_FILES_DIR, folder)

        if os.path.isdir(folder_path):
            if folder not in active_sessions:
                print(f"Deleting expired session dir: {folder_path}")
                shutil.rmtree(folder_path, ignore_errors=True)
            else:
                print(f"Keeping active session dir: {folder_path}")

if __name__ == "__main__":
    cleanup_sessions()
