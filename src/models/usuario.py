from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class Usuario(db.Model):
    """
    Modelo de usuario para la autenticación y gestión de usuarios.
    """
    __tablename__ = "usuarios"
    
    id = db.Column(db.Integer, primary_key=True)
    correo = db.Column(db.String(100), unique=True, nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

    def set_password(self, password):
        """
        Genera y almacena el hash de la contraseña.
        Args:
            password (str): Contraseña en texto plano.
        """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """
        Verifica si la contraseña proporcionada coincide con el hash almacenado.
        Args:
            password (str): Contraseña en texto plano.
        Returns:
            bool: True si la contraseña es correcta, False en caso contrario.
        """
        return check_password_hash(self.password_hash, password)
