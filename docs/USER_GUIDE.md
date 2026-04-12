# Guía de Usuario

El proyecto dispone actualmente de dos experiencias de uso: escritorio Flet y versión web Flask en progreso.

## 1. Elegir modo de uso

### Escritorio

```powershell
python main.py
```

### Web

```powershell
python app.py
```

## 2. Acceso web

Abre el navegador en:

```text
http://127.0.0.1:5000/
```

La aplicación redirige a login.

## 3. Login

La autenticación usa usuarios almacenados en la tabla `persona`.

Pasos:

1. ingresar correo o usuario,
2. ingresar contraseña,
3. iniciar sesión,
4. si las credenciales son válidas se emite un JWT.

## 4. Módulos web disponibles

### Dashboard

- vista base disponible,
- parte de los datos todavía es demo.

### Presupuesto

- listado,
- creación,
- edición,
- eliminación.

### Transacciones

- listado de movimientos,
- creación,
- edición,
- eliminación.

### Reportes

- agregación por meses,
- categorías de gasto.

## 5. Flujo ETL de tarjeta

El ETL sigue asociado principalmente a la experiencia de escritorio.

Uso general:

1. abrir el flujo de nueva transacción,
2. elegir carga masiva de tarjeta,
3. seleccionar el Excel,
4. validar y cargar.

## 6. Limitaciones actuales

- No todas las pantallas de Flet existen aún en HTML.
- El dashboard web no está completado al cien por ciento.
- Algunas funciones avanzadas siguen dependiendo del flujo heredado.
