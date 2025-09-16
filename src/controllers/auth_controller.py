from src.models.usuario import db, Usuario

def registrar_usuario(nombre, correo, password):
    if Usuario.query.filter_by(correo=correo).first():
        return None, "El correo ya está registrado"
    
    nuevo = Usuario(nombre=nombre, correo=correo)
    nuevo.set_password(password)
    db.session.add(nuevo)
    db.session.commit()
    return nuevo, None

def autenticar_usuario(correo, password):
    usuario = Usuario.query.filter_by(correo=correo).first()
    if usuario and usuario.check_password(password):
        return usuario
    return None
