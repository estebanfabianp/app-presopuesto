# Guía de Despliegue

## 🚀 Preparación para Producción

### 1. Optimización del Código

```bash
# Limpiar archivos temporales
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} +

# Verificar código
black src/
flake8 src/
mypy src/
```

### 2. Testing Completo

```bash
# Ejecutar todos los tests
pytest tests/ -v --cov=src

# Tests de integración
pytest tests/integration/ -v

# Tests de rendimiento
pytest tests/performance/ -v
```

## 📦 Crear Ejecutable

### Windows

```bash
# Instalar PyInstaller
pip install pyinstaller

# Crear ejecutable
pyinstaller --onefile --windowed --icon=assets/icon.ico main.py

# Ejecutable en dist/main.exe
```

### macOS

```bash
# Crear app bundle
pyinstaller --onefile --windowed --icon=assets/icon.icns main.py

# Crear DMG (opcional)
hdiutil create -volname "App Presupuesto" -srcfolder dist/ -ov app-presupuesto.dmg
```

### Linux

```bash
# Crear ejecutable
pyinstaller --onefile main.py

# Crear AppImage (opcional)
# Requiere appimagetool
```

## 🐳 Docker Deployment

### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY assets/ ./assets/

EXPOSE 8080

CMD ["python", "main.py"]
```

### Docker Compose

```yaml
version: '3.8'
services:
  app-presupuesto:
    build: .
    ports:
      - "8080:8080"
    volumes:
      - ./data:/app/data
    environment:
      - DEBUG=False
      - DATABASE_URL=sqlite:///data/app.db
```

## ☁️ Cloud Deployment

### Heroku

```bash
# Crear Procfile
echo "web: python main.py" > Procfile

# Crear app
heroku create app-presupuesto

# Deploy
git push heroku main
```

### AWS EC2

```bash
# Conectar a instancia
ssh -i key.pem ubuntu@ec2-instance

# Instalar dependencias
sudo apt update
sudo apt install python3-pip

# Clonar y configurar
git clone https://github.com/tu-usuario/app-presopuesto.git
cd app-presupuesto
pip3 install -r requirements.txt

# Ejecutar como servicio
sudo systemctl enable app-presupuesto
sudo systemctl start app-presopuesto
```

## 🔒 Configuración de Seguridad

### Variables de Entorno

```bash
# .env
DEBUG=False
SECRET_KEY=your-secret-key-here
DATABASE_URL=your-database-url
ALLOWED_HOSTS=localhost,127.0.0.1
```

### SSL/HTTPS

```nginx
# nginx.conf
server {
    listen 443 ssl;
    server_name tu-dominio.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://localhost:8080;
    }
}
```

## 📊 Monitoreo

### Health Checks

```python
def health_check():
    """Endpoint para verificar estado de la aplicación."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }
```

### Logging en Producción

```python
import logging
from logging.handlers import RotatingFileHandler

# Configurar logging para producción
handler = RotatingFileHandler('app.log', maxBytes=10000000, backupCount=5)
handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
))
logger.addHandler(handler)
logger.setLevel(logging.INFO)
```

## 🔄 CI/CD Pipeline

### GitHub Actions

```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: pytest

  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to production
        run: echo "Deploying to production..."
```
