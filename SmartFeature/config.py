from firebase_admin import credentials, initialize_app
import os
from dotenv import load_dotenv

load_dotenv()

class FirebaseConfig:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FirebaseConfig, cls).__new__(cls)
            # Inicializar Firebase Admin SDK
            cred = credentials.Certificate(os.getenv('FIREBASE_CREDENTIALS_PATH'))
            initialize_app(cred)
        return cls._instance

