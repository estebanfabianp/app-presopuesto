from models.user_model import UserModel

class UserController:
    def __init__(self):
        self.model = UserModel()

    def save_user(self, name, email):
        if not name or not email:
            return None, "Nombre y correo son obligatorios."
        
        user = self.model.add_user(name, email)
        if user:
            return user, "Usuario agregado con éxito."
        else:
            return None, "El correo ya existe en la base de datos."
