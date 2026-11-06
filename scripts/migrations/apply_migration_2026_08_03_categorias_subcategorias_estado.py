"""Migra la tabla categoria para soportar subcategorías y estado de activación."""

import os
import mysql.connector
from mysql.connector import Error


def main() -> None:
    host = os.getenv('DB_HOST', 'localhost')
    port = int(os.getenv('DB_PORT', '3306'))
    database = os.getenv('DB_NAME', 'app_presupuesto')
    user = os.getenv('DB_USER', 'root')
    password = os.getenv('DB_PASSWORD', '')

    conn = None
    cursor = None
    try:
        conn = mysql.connector.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password,
            connection_timeout=10,
        )
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SHOW COLUMNS FROM categoria')
        columns = {row['Field'] for row in cursor.fetchall()}

        changes = []
        if 'parent_id' not in columns:
            changes.append("ALTER TABLE categoria ADD COLUMN parent_id INT(11) NULL AFTER nombre")
        if 'estado' not in columns:
            changes.append("ALTER TABLE categoria ADD COLUMN estado TINYINT(1) NOT NULL DEFAULT 1 AFTER parent_id")
        if 'icono' not in columns:
            changes.append("ALTER TABLE categoria ADD COLUMN icono VARCHAR(50) NULL DEFAULT 'fa-tag' AFTER estado")
        if 'color' not in columns:
            changes.append("ALTER TABLE categoria ADD COLUMN color VARCHAR(20) NULL DEFAULT '#6c757d' AFTER icono")

        if changes:
            for statement in changes:
                cursor.execute(statement)
            cursor.execute("UPDATE categoria SET estado = 1 WHERE estado IS NULL")
            cursor.execute("UPDATE categoria SET icono = 'fa-tag' WHERE icono IS NULL")
            cursor.execute("UPDATE categoria SET color = '#6c757d' WHERE color IS NULL")
            conn.commit()
            print('Migración aplicada:')
            for statement in changes:
                print('-', statement)
        else:
            print('La tabla categoria ya tiene los campos de subcategorías y estado.')
    except Error as exc:
        if conn:
            conn.rollback()
        raise SystemExit(f'Error migrando categoria: {exc}') from exc
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


if __name__ == '__main__':
    main()
