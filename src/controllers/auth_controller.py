from src.models.usuario import db, Usuario

def registrar_usuario(nombre, correo, password):
    """
    Registra un nuevo usuario en la base de datos.
    Args:
        nombre (str): Nombre del usuario.
        correo (str): Correo electrónico único.
        password (str): Contraseña en texto plano.
    Returns:
        tuple: (Usuario, None) si el registro es exitoso, (None, mensaje de error) si falla.
    """
    if Usuario.query.filter_by(correo=correo).first():
        return None, "El correo ya está registrado"
    
    nuevo = Usuario(nombre=nombre, correo=correo)
    nuevo.set_password(password)
    db.session.add(nuevo)
    db.session.commit()
    return nuevo, None

def autenticar_usuario(correo, password):
    """
    Autentica un usuario verificando correo y contraseña.
    Args:
        correo (str): Correo electrónico del usuario.
        password (str): Contraseña en texto plano.
    Returns:
        Usuario: Instancia de usuario si la autenticación es exitosa, None si falla.
    """
    usuario = Usuario.query.filter_by(correo=correo).first()
    if usuario and usuario.check_password(password):
        return usuario
    return None
