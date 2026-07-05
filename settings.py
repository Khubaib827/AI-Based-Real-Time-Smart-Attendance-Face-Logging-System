from config.constants import DEFAULT_ADMIN_USERNAME, DEFAULT_ADMIN_PASSWORD

class Settings:
    def __init__(self):
        self._settings = {
            "admin": {"username": DEFAULT_ADMIN_USERNAME, "password": DEFAULT_ADMIN_PASSWORD},
            "camera": {"index": 0},
            "recognition": {"threshold": 0.6}
        }
    
    def get(self, key, default=None):
        keys = key.split('.')
        value = self._settings
        for k in keys:
            value = value.get(k)
            if value is None:
                return default
        return value

settings = Settings()