from __future__ import annotations

import argparse
import calendar
from datetime import datetime


FORMATO_FECHA = "%d/%m/%Y"


def ajustar_fechas_al_mes(fechas: list[str], mes_destino: int) -> list[str]:
    if not 1 <= mes_destino <= 12:
        raise ValueError("El mes destino debe estar entre 1 y 12")

    resultado = []
    for fecha_str in fechas:
        fecha = datetime.strptime(fecha_str, FORMATO_FECHA)
        ultimo_dia = calendar.monthrange(fecha.year, mes_destino)[1]
        nuevo_dia = min(fecha.day, ultimo_dia)
        fecha_ajustada = fecha.replace(month=mes_destino, day=nuevo_dia)
        resultado.append(fecha_ajustada.strftime(FORMATO_FECHA))

    return resultado


def leer_fechas_desde_consola() -> list[str]:
    print("Ingresa una fecha por linea en formato dd/mm/yyyy.")
    print("Cuando termines, presiona Enter en una linea vacia.")

    fechas: list[str] = []
    while True:
        try:
            linea = input().strip()
        except EOFError:
            break
        if not linea:
            break
        fechas.append(linea)

    if not fechas:
        raise ValueError("Debes ingresar al menos una fecha")

    return fechas


def parsear_argumentos() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Ajusta una lista de fechas al mes indicado respetando el ultimo dia valido"
    )
    parser.add_argument(
        "--mes",
        type=int,
        help="Mes destino (1-12)",
    )
    parser.add_argument(
        "--fechas",
        nargs="+",
        help="Lista de fechas con formato dd/mm/yyyy",
    )
    return parser.parse_args()


def main() -> None:
    try:
        args = parsear_argumentos()

        if args.fechas and args.mes is not None:
            fechas = args.fechas
            mes_destino = args.mes
        else:
            fechas = leer_fechas_desde_consola()
            try:
                mes_destino = int(input("Mes destino (1-12): ").strip())
            except EOFError as exc:
                raise ValueError(
                    "No se pudo leer el mes desde consola. Usa --mes y --fechas"
                ) from exc

        resultado = ajustar_fechas_al_mes(fechas, mes_destino)

        print("\nSalida:")
        for fecha in resultado:
            print(fecha)

    except ValueError as exc:
        print(f"Error: {exc}")


if __name__ == "__main__":
    main()
