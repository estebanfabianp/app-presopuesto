"""
ETL para carga masiva de transacciones de tarjeta de crédito desde Excel.

Procesa archivos Excel validando estructura, transformando datos y cargando
en las tablas movimiento y movimiento_tarjeta con control transaccional completo.
"""

from __future__ import annotations

import datetime
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    import pandas as pd
except ImportError:
    pd = None

try:
    from ...database.db_connector import DatabaseConnector
except ImportError:
    try:
        from src.database.db_connector import DatabaseConnector
    except ImportError:
        from database.db_connector import DatabaseConnector


@dataclass
class ValidationResult:
    """Resultado de validación de fila de Excel."""
    is_valid: bool = True
    errors: List[str] = field(default_factory=list)
    row_number: int = 0
    data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TransformResult:
    """Resultado de transformación de datos."""
    is_valid: bool = True
    errors: List[str] = field(default_factory=list)
    insert_movimiento: Dict[str, Any] = field(default_factory=dict)
    insert_movimiento_tarjeta: Dict[str, Any] = field(default_factory=dict)


class ETLTarjetaCredito:
    """
    ETL para procesamiento de transacciones de tarjeta de crédito desde Excel.
    
    Flujo:
    1. Validar archivo Excel
    2. Extraer y validar datos
    3. Transformar a formato de base de datos
    4. Cargar en transacción
    5. Reportar errores
    """
    
    # Columnas esperadas en Excel (case-insensitive)
    EXPECTED_COLUMNS = {
        'fecha': ['fecha', 'date', 'date_transaction'],
        'concepto': ['concepto', 'description', 'descripcion', 'transaccion'],
        'monto': ['monto', 'amount', 'valor', 'quantity'],
        'cuotas': ['cuotas', 'quotas', 'installments', 'nro_cuotas'],
        'categoria': ['categoria', 'category', 'categoría'],
        'referencia': ['referencia', 'reference', 'ref', 'numero_referencia']
    }
    
    def __init__(self, db: Optional[DatabaseConnector] = None):
        """
        Inicializa el ETL.
        
        Args:
            db: Conexión a base de datos. Si no se proporciona, se crea una nueva.
        """
        self.db = db or DatabaseConnector()
        self.logger = logging.getLogger(__name__)
        self.validation_errors: List[Dict[str, Any]] = []
        self.processed_count = 0
        self.error_count = 0
    
    def process_file(
        self, 
        file_path: str,
        id_persona: int,
        id_tarjeta: int,
    ) -> Tuple[int, List[Dict[str, Any]]]:
        """
        Procesa archivo Excel completo.
        
        Args:
            file_path: Ruta del archivo Excel
            id_persona: ID de la persona propietaria
            id_tarjeta: ID de la tarjeta de crédito
        
        Returns:
            Tupla (cantidad_insertada, lista_de_errores)
        """
        if not pd:
            raise ImportError("pandas es requerido para procesar archivos Excel")
        
        try:
            # Leer archivo
            df = pd.read_excel(file_path)
            if df.empty:
                return 0, [{"error": "Archivo Excel vacío"}]
            
            # Normalizar nombres de columnas
            df.columns = [str(col).lower().strip() for col in df.columns]
            
            # Validar estructura
            self._validate_excel_structure(df.columns)
            
            # Mapear columnas
            col_map = self._map_columns(df.columns)
            
            # Procesar filas
            rows_to_insert: List[Tuple[Dict, Dict]] = []
            
            for idx, (_, row) in enumerate(df.iterrows(), start=2):  # start=2 para fila de header
                validation = self._validate_row(row, col_map, idx)
                
                if not validation.is_valid:
                    self.validation_errors.append({
                        "row": idx,
                        "errors": validation.errors,
                        "data": validation.data
                    })
                    self.error_count += 1
                    continue
                
                # Transformar datos
                transform = self._transform_row(
                    validation.data,
                    id_persona,
                    id_tarjeta,
                    idx
                )
                
                if not transform.is_valid:
                    self.validation_errors.append({
                        "row": idx,
                        "errors": transform.errors,
                        "data": validation.data
                    })
                    self.error_count += 1
                    continue
                
                rows_to_insert.append((
                    transform.insert_movimiento,
                    transform.insert_movimiento_tarjeta
                ))
            
            # Insertar en base de datos (transacción)
            if rows_to_insert:
                self._load_data(rows_to_insert)
                self.processed_count = len(rows_to_insert)
            
            return self.processed_count, self.validation_errors
            
        except Exception as e:
            self.logger.error(f"Error procesando archivo: {e}")
            return 0, [{"error": f"Error de procesamiento: {str(e)}"}]
    
    def _validate_excel_structure(self, columns: List[str]) -> None:
        """Valida que el Excel tenga las columnas requeridas."""
        required_found = {k: False for k in self.EXPECTED_COLUMNS}
        
        for col in columns:
            col_lower = str(col).lower().strip()
            for key, aliases in self.EXPECTED_COLUMNS.items():
                if col_lower in aliases:
                    required_found[key] = True
                    break
        
        missing = [k for k, v in required_found.items() if not v]
        if missing:
            raise ValueError(f"Columnas faltantes en Excel: {', '.join(missing)}")
    
    def _map_columns(self, columns: List[str]) -> Dict[str, str]:
        """
        Mapea las columnas del Excel a nombres estándar.
        
        Returns:
            Dict con mapeo: {'fecha': 'columna_encontrada', ...}
        """
        col_map = {}
        col_lower_list = [str(c).lower().strip() for c in columns]
        
        for standard_name, aliases in self.EXPECTED_COLUMNS.items():
            for i, col_lower in enumerate(col_lower_list):
                if col_lower in aliases:
                    col_map[standard_name] = columns[i]
                    break
        
        return col_map
    
    def _validate_row(
        self,
        row: Any,
        col_map: Dict[str, str],
        row_number: int
    ) -> ValidationResult:
        """Valida una fila individual del Excel."""
        result = ValidationResult(row_number=row_number)
        
        # Extraer valores
        fecha_str = str(row.get(col_map.get('fecha', ''), '')).strip()
        concepto = str(row.get(col_map.get('concepto', ''), '')).strip()
        monto_str = str(row.get(col_map.get('monto', ''), '')).strip()
        cuotas_str = str(row.get(col_map.get('cuotas', '1'), '1')).strip()
        categoria = str(row.get(col_map.get('categoria', ''), '')).strip()
        referencia = str(row.get(col_map.get('referencia', ''), '')).strip()
        
        # Validar campos obligatorios
        if not concepto or concepto.lower() == 'nan':
            result.is_valid = False
            result.errors.append("Concepto es obligatorio")
        
        if not monto_str or monto_str.lower() == 'nan':
            result.is_valid = False
            result.errors.append("Monto es obligatorio")
        else:
            try:
                monto = float(monto_str.replace(',', '.'))
                if monto <= 0:
                    result.is_valid = False
                    result.errors.append("Monto debe ser mayor a cero")
            except ValueError:
                result.is_valid = False
                result.errors.append(f"Monto inválido: '{monto_str}'")
        
        # Validar fecha
        fecha = None
        if fecha_str and fecha_str.lower() != 'nan':
            try:
                # Intentar parseo
                if isinstance(row.get(col_map.get('fecha', '')), pd.Timestamp):
                    fecha = pd.Timestamp(row.get(col_map.get('fecha', ''))).date()
                else:
                    fecha = pd.to_datetime(fecha_str).date()
            except Exception:
                result.is_valid = False
                result.errors.append(f"Fecha inválida: '{fecha_str}'")
        else:
            fecha = datetime.date.today()
        
        # Validar cuotas
        try:
            cuotas = int(float(cuotas_str)) if cuotas_str and cuotas_str.lower() != 'nan' else 1
            if cuotas < 1 or cuotas > 36:
                result.is_valid = False
                result.errors.append("Cuotas debe estar entre 1 y 36")
        except ValueError:
            result.is_valid = False
            result.errors.append(f"Cuotas inválida: '{cuotas_str}'")
            cuotas = 1
        
        # Validar categoría
        if not categoria or categoria.lower() == 'nan':
            categoria = "Compras"  # Categoría por defecto
        
        if result.is_valid:
            result.data = {
                'fecha': fecha,
                'concepto': concepto,
                'monto': float(monto_str.replace(',', '.')),
                'cuotas': cuotas,
                'categoria': categoria,
                'referencia': referencia if referencia and referencia.lower() != 'nan' else ''
            }
        
        return result
    
    def _transform_row(
        self,
        validated_data: Dict[str, Any],
        id_persona: int,
        id_tarjeta: int,
        row_number: int
    ) -> TransformResult:
        """Transforma datos validados a formato de base de datos."""
        result = TransformResult()
        
        try:
            cursor = self.db.conn.cursor(dictionary=True)
            
            # Obtener ID de categoría
            categoria_key = validated_data['categoria'].strip().lower()
            cursor.execute(
                "SELECT id_categoria FROM categoria WHERE LOWER(nombre) = %s LIMIT 1",
                (categoria_key,)
            )
            cat_row = cursor.fetchone()
            
            id_categoria = None
            if cat_row:
                id_categoria = int(cat_row['id_categoria'])
            else:
                # Crear nueva categoría si no existe
                cursor.execute(
                    "INSERT INTO categoria (nombre) VALUES (%s)",
                    (validated_data['categoria'],)
                )
                id_categoria = int(cursor.lastrowid)
            
            # Obtener id_tipo de movimiento (gasto para tarjeta de crédito)
            cursor.execute(
                "SELECT id_tipo FROM tipo_movimiento WHERE LOWER(nombre) = 'gasto' LIMIT 1"
            )
            tipo_row = cursor.fetchone()
            id_tipo_gasto = int(tipo_row['id_tipo']) if tipo_row else 1
            
            # Obtener id_estado de movimiento
            cursor.execute(
                "SELECT id_estado FROM estado_movimiento ORDER BY id_estado LIMIT 1"
            )
            estado_row = cursor.fetchone()
            id_estado_mov = int(estado_row['id_estado']) if estado_row else 1
            
            # Obtener id_cuenta del usuario (si no existe, usar la primera)
            cursor.execute(
                "SELECT id_cuenta FROM cuenta WHERE id_persona = %s LIMIT 1",
                (id_persona,)
            )
            cuenta_row = cursor.fetchone()
            id_cuenta = int(cuenta_row['id_cuenta']) if cuenta_row else 1
            
            cursor.close()
            
            # Generar códigos únicos
            timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
            codigo_movimiento = f"MOV-{timestamp}-{row_number}"
            numero_transaccion = f"TRX-{timestamp}-{row_number}"
            
            # Preparar INSERT para tabla movimiento
            result.insert_movimiento = {
                'codigo': codigo_movimiento,
                'monto': validated_data['monto'],
                'id_tipo': id_tipo_gasto,
                'id_estado': id_estado_mov,
                'id_producto': id_tarjeta,  # ID de tarjeta como producto
                'id_categoria': id_categoria,
                'id_beneficiario': None,
                'numero_transaccion': numero_transaccion,
                'nota': f"{validated_data['concepto']} - {validated_data['referencia']}".strip(),
                'fecha_creacion': datetime.datetime.now(),
                'id_cuenta': id_cuenta
            }
            
            # Preparar INSERT para tabla movimiento_tarjeta
            result.insert_movimiento_tarjeta = {
                'id_tarjeta': id_tarjeta,
                'id_persona': id_persona,
                'fecha': validated_data['fecha'],
                'valor': validated_data['monto'],
                'estado': 'compra',
                'nota': validated_data['concepto'],
                'numero_transaccion': numero_transaccion,
                'id_categoria': id_categoria,
                'id_beneficiario': None,
                'saldo': validated_data['monto'],
                'cuotas': validated_data['cuotas']
            }
            
        except Exception as e:
            result.is_valid = False
            result.errors.append(f"Error transformando datos: {str(e)}")
        
        return result
    
    def _load_data(self, rows: List[Tuple[Dict, Dict]]) -> None:
        """
        Carga datos en base de datos con transacción.
        
        Args:
            rows: Lista de tuplas (movimiento_data, movimiento_tarjeta_data)
        """
        cursor = None
        try:
            cursor = self.db.conn.cursor()
            
            for mov_data, mov_tarjeta_data in rows:
                # INSERT en movimiento
                mov_columns = ', '.join(mov_data.keys())
                mov_placeholders = ', '.join(['%s'] * len(mov_data))
                mov_values = list(mov_data.values())
                
                cursor.execute(
                    f"INSERT INTO movimiento ({mov_columns}) VALUES ({mov_placeholders})",
                    mov_values
                )
                id_movimiento = int(cursor.lastrowid)
                
                # INSERT en movimiento_tarjeta
                tarjeta_columns = ', '.join(mov_tarjeta_data.keys())
                tarjeta_placeholders = ', '.join(['%s'] * len(mov_tarjeta_data))
                tarjeta_values = list(mov_tarjeta_data.values())
                
                cursor.execute(
                    f"INSERT INTO movimiento_tarjeta ({tarjeta_columns}) VALUES ({tarjeta_placeholders})",
                    tarjeta_values
                )
            
            self.db.conn.commit()
            self.logger.info(f"Cargados {len(rows)} registros exitosamente")
            
        except Exception as e:
            self.db.conn.rollback()
            self.logger.error(f"Error durante carga de datos: {e}")
            raise
        finally:
            if cursor:
                cursor.close()


def validate_excel_file(file_path: str) -> Tuple[bool, List[str]]:
    """
    Validación rápida de archivo Excel.
    
    Returns:
        Tupla (is_valid, list_of_errors)
    """
    if not pd:
        return False, ["pandas es requerido"]
    
    errors = []
    
    try:
        df = pd.read_excel(file_path)
        
        if df.empty:
            errors.append("Archivo Excel vacío")
            return False, errors
        
        # Verificar columnas
        etl = ETLTarjetaCredito()
        try:
            etl._validate_excel_structure(df.columns)
        except ValueError as e:
            errors.append(str(e))
            return False, errors
        
        return True, []
        
    except Exception as e:
        return False, [f"Error leyendo archivo: {str(e)}"]
