from typing import Dict, Any
import bcrypt
import jwt
from cryptography.fernet import Fernet
import re

class SecurityManager:
    """Gestiona la seguridad del sistema a múltiples niveles"""
    
    def __init__(self, secret_key: str, encryption_key: bytes):
        self.secret_key = secret_key
        self.cipher = Fernet(encryption_key)
        
    def hash_password(self, password: str) -> str:
        """Hash seguro de contraseñas usando bcrypt"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
        
    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Verifica una contraseña contra su hash"""
        return bcrypt.checkpw(password.encode('utf-8'), 
                           hashed_password.encode('utf-8'))
                           
    def generate_token(self, payload: Dict[str, Any], 
                     expires_in: int = 3600) -> str:
        """Genera un token JWT para autenticación"""
        payload_copy = payload.copy()
        payload_copy['exp'] = datetime.now().timestamp() + expires_in
        return jwt.encode(payload_copy, self.secret_key, algorithm='HS256')
        
    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verifica y decodifica un token JWT"""
        try:
            return jwt.decode(token, self.secret_key, algorithms=['HS256'])
        except jwt.InvalidTokenError:
            raise SecurityError("Token inválido o expirado")
            
    def encrypt_data(self, data: str) -> str:
        """Cifra datos sensibles"""
        return self.cipher.encrypt(data.encode('utf-8')).decode('utf-8')
        
    def decrypt_data(self, encrypted_data: str) -> str:
        """Descifra datos previamente cifrados"""
        return self.cipher.decrypt(encrypted_data.encode('utf-8')).decode('utf-8')
        
    def validate_input(self, input_data: Any, expected_type: type, 
                     max_length: int = None) -> bool:
        """Valida y sanitiza entrada de datos"""
        if not isinstance(input_data, expected_type):
            raise SecurityError(f"Tipo de dato inválido. Esperado: {expected_type}")
            
        if max_length and len(str(input_data)) > max_length:
            raise SecurityError(f"Longitud máxima excedida: {max_length}")
            
        # Sanitización básica para prevenir injection
            # Eliminar caracteres potencialmente peligrosos
            sanitized = re.sub(r'[;\\\'"<>]', '', input_data)
            return sanitized if sanitized != input_data else input_data
            
        return input_data
        return input_data