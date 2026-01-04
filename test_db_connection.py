import psycopg2
import sys

db_params = {
    'database': 'db_finanzas',
    'user': 'db_finanzas_user',
    'password': 'JE7cOl0Y6UDwM1y4kyKDDpD8QOU5afRM',
    'host': 'dpg-d11ejpje5dus738mccng-a.oregon-postgres.render.com',
    'port': '5432',
}


print(f"Psycopg2 version: {psycopg2.__version__}")

modes = ['require']
# Try to find a cert bundle
cert_path = "/etc/ssl/certs/ca-certificates.crt"

for mode in modes:
    print(f"\n--- Testing sslmode='{mode}' with sslrootcert='{cert_path}' ---")
    current_params = db_params.copy()
    current_params['sslmode'] = mode
    current_params['sslrootcert'] = cert_path
    try:
        print("Attempting to connect...")
        conn = psycopg2.connect(**current_params)
        print("Connection successful!")
        conn.close()
        break
    except Exception as e:
        print(f"Connection failed: {e}")

