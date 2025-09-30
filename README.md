# App Presupuesto 💰

Aplicación de gestión de presupuestos desarrollada con Flet y arquitectura MVC.

## 📋 Descripción

Sistema de login y gestión de usuarios con interfaz gráfica moderna construida con Python y Flet.

## 🚀 Características

- ✅ Interfaz gráfica moderna con Flet
- 🏗️ Arquitectura MVC (Modelo-Vista-Controlador)
- 🔐 Sistema de autenticación de usuarios
- 🎨 Diseño responsive y centrado
- 📱 Ventana no redimensionable (400x500px)

## 📁 Estructura del Proyecto

```
app-presupuesto/
├── src/
│   ├── views/          # Interfaces de usuario (UI)
│   │   └── user_view.py
│   ├── controllers/    # Lógica de negocio
│   │   └── __init__.py
│   ├── models/         # Modelos de datos
│   │   └── __init__.py
│   └── database/       # Conexión a base de datos
├── requirements.txt
└── README.md
```

## 🛠️ Instalación

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/usuario/app-presopuesto.git
   cd app-presopuesto
   ```

2. **Crear entorno virtual:**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   # source venv/bin/activate  # Linux/Mac
   ```

3. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

## 🎮 Uso

### Ejecutar la aplicación:
```bash
python src/views/user_view.py
```

### Características de la interfaz:
- **Campo Usuario:** Acepta cualquier nombre de usuario
- **Campo Contraseña:** Campo oculto con opción de mostrar
- **Botón Login:** Valida que ambos campos tengan contenido
- **Mensajes:** Feedback visual en verde (éxito) o rojo (error)

## 👨‍💻 Desarrollo

### Tecnologías utilizadas:
- **Python 3.x**
- **Flet** - Framework para UI
- **Arquitectura MVC**

### Autor:
**Esteban Fabián Patiño Montealegre**

### Versión:
**0.2.0**

## 🐛 Solución de problemas

Si encuentras errores de importación:
1. Verifica que estés en el directorio correcto
2. Asegúrate de que el entorno virtual esté activado
3. Instala las dependencias: `pip install flet`

## 📝 Licencia

Este proyecto está bajo licencia MIT.