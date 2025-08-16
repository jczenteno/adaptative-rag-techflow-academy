from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse, urlunparse

from dotenv import load_dotenv


def _build_admin_dsn(host: str, port: str, user: str, password: str, sslmode: str = "require") -> str:
    """Construye DSN para conectarse a la base de datos admin 'postgres'.
    
    Esta función crea una conexión a la base de datos 'postgres' que existe
    por defecto, para poder crear la base de datos objetivo.
    """
    return f"host={host} port={port} user={user} password={password} dbname=postgres sslmode={sslmode}"


def _dsn_with_postgres_db(dsn: str) -> str:
    """Force DSN to connect to an existing admin DB ('postgres').

    This ensures the script can create the target DB and then `\\connect` to it
    inside the SQL file. Works for URL-style DSNs. If the DSN is not a URL,
    it is returned unchanged.
    """
    try:
        parsed = urlparse(dsn)
    except Exception:
        return dsn

    if parsed.scheme not in ("postgresql", "postgres"):
        return dsn

    # Preserve existing query/params but force path to /postgres
    new_path = "/postgres"
    return urlunparse(
        (
            parsed.scheme,
            parsed.netloc,
            new_path,
            parsed.params,
            parsed.query,
            parsed.fragment,
        )
    )


def main() -> int:
    load_dotenv()

    # Leer credenciales individuales de variables de entorno
    host = os.getenv("POSTGRES_HOST")
    port = os.getenv("POSTGRES_PORT", "5432")
    user = os.getenv("POSTGRES_USER")
    password = os.getenv("POSTGRES_PASSWORD")
    database = os.getenv("POSTGRES_NEON_DATABASE")
    sslmode = os.getenv("POSTGRES_SSLMODE", "require")
    
    # Validar que tenemos las credenciales necesarias
    if not all([host, user, password, database]):
        missing = []
        if not host: missing.append("POSTGRES_HOST")
        if not user: missing.append("POSTGRES_USER")
        if not password: missing.append("POSTGRES_PASSWORD")
        if not database: missing.append("POSTGRES_NEON_DATABASE")
        print(f"ERROR: Faltan variables de entorno: {', '.join(missing)}", file=sys.stderr)
        return 1
    
    # Construir DSN usando credenciales individuales
    dsn = f"host={host} port={port} user={user} password={password} dbname={database} sslmode={sslmode}"
    print(f"Conectando a la base de datos: {database}")

    sql_file = Path(__file__).with_name("tabla_programas.sql")
    if not sql_file.exists():
        print(f"ERROR: No se encontró el archivo SQL: {sql_file}", file=sys.stderr)
        return 1

    # Conectarse primero a 'postgres' para poder crear la BD objetivo y luego \connect
    admin_dsn = _build_admin_dsn(host, port, user, password, sslmode)

    cmd = [
        "psql",
        admin_dsn,
        "-v",
        "ON_ERROR_STOP=1",
        "-f",
        str(sql_file),
    ]

    print(f"Ejecutando: {' '.join(cmd[:-1])} {sql_file}")
    try:
        subprocess.run(cmd, check=True)
    except FileNotFoundError:
        print(
            "ERROR: No se encontró 'psql'. Instala el cliente de PostgreSQL y asegúrate de que esté en el PATH.",
            file=sys.stderr,
        )
        return 1
    except subprocess.CalledProcessError as exc:
        print(f"ERROR: Falló la ejecución del script SQL (código {exc.returncode}).", file=sys.stderr)
        return exc.returncode or 1

    print("OK: Script SQL ejecutado correctamente.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


