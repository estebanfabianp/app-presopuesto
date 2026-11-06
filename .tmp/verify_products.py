import os
import sys
sys.path.insert(0, os.getcwd())
import requests
from app import create_app
from src.database.db_connector import DatabaseConnector
from flask_jwt_extended import create_access_token

app = create_app('development')
app.config['TESTING'] = True
with app.app_context():
    db = DatabaseConnector()
    try:
        persona_id = 1
        token = create_access_token(identity=str(persona_id), fresh=True)
        response = requests.get('http://127.0.0.1:5000/api/productos', headers={'Authorization': f'Bearer {token}'}, timeout=10)
        print('status', response.status_code)
        print(response.text[:1500])
    finally:
        db.close()