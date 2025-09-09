import os
import secrets
from pathlib import Path
from dotenv import load_dotenv
from functools import lru_cache

class JWTConfig:
    """JWT Configuration Bean - auto-generates secure keys on startup"""
    
    def __init__(self):
        self._secret_key = None
        self._algorithm = None
        self._ensure_jwt_secret()
    
    def _ensure_jwt_secret(self):
        """Ensure JWT secret exists, generate if needed (like @Bean keyPair())"""
        # Load environment variables
        load_dotenv()
        
        # Get current secret
        current_secret = os.getenv('JWT_SECRET')
        
        # Check if we need to generate a new secret
        if not current_secret or current_secret == 'your-secret-key-change-in-production':
            print("🔑 Generating new JWT secret key...")
            self._generate_and_save_secret()
        else:
            print("🔑 Using existing JWT secret key")
            self._secret_key = current_secret
        
        # Set algorithm
        self._algorithm = os.getenv('JWT_ALGORITHM', 'HS256')
        
        print(f"🔑 JWT Config initialized - Algorithm: {self._algorithm}")
    
    def _generate_and_save_secret(self):
        """Generate cryptographically secure JWT secret (like KeyPairGenerator)"""
        try:
            # Generate 64-byte secret (like RSA 2048-bit equivalent strength)
            new_secret = secrets.token_urlsafe(64)
            
            # Update .env file
            env_path = Path(__file__).parent.parent / '.env'
            
            if env_path.exists():
                with open(env_path, 'r') as f:
                    lines = f.readlines()
            else:
                lines = []
            
            # Update or add JWT_SECRET
            secret_updated = False
            for i, line in enumerate(lines):
                if line.strip().startswith('JWT_SECRET='):
                    lines[i] = f'JWT_SECRET={new_secret}\n'
                    secret_updated = True
                    break
            
            if not secret_updated:
                lines.append(f'JWT_SECRET={new_secret}\n')
            
            # Ensure JWT_ALGORITHM exists
            algorithm_exists = any(line.strip().startswith('JWT_ALGORITHM=') for line in lines)
            if not algorithm_exists:
                lines.append('JWT_ALGORITHM=HS256\n')
            
            # Write updated file
            with open(env_path, 'w') as f:
                f.writelines(lines)
            
            self._secret_key = new_secret
            print(f"✅ Generated and saved new JWT secret key")
            
            # Reload environment variables
            load_dotenv(override=True)
            
        except Exception as e:
            raise RuntimeError(f"Failed to generate JWT secret: {e}")
    
    @property
    def secret_key(self) -> str:
        """Get JWT secret key"""
        return self._secret_key or os.getenv('JWT_SECRET')
    
    @property
    def algorithm(self) -> str:
        """Get JWT algorithm"""
        return self._algorithm or os.getenv('JWT_ALGORITHM', 'HS256')

# Singleton instance (like Spring @Bean)
@lru_cache(maxsize=1)
def get_jwt_config() -> JWTConfig:
    """Get JWT configuration bean (singleton)"""
    return JWTConfig()

# Auto-initialize on module import (like Spring context startup)
jwt_config = get_jwt_config()