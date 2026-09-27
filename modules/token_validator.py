import requests
import logging

logger = logging.getLogger("ZetaLabs")

DEFAULT_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"

class TokenValidatorMixin:
    def check_token(self, token, token_type):
        headers = {
            "Authorization": f"Bot {token}" if token_type == "bot" else token,
            "User-Agent": DEFAULT_UA
        }
        try:
            req = requests.get("https://discord.com/api/v10/users/@me", headers=headers, timeout=6)
            if req.status_code == 200:
                data = req.json()
                uname = data.get('username', 'Bilinmiyor')
                disc = data.get('discriminator', '0')
                name = uname if disc == '0' else f"{uname}#{disc}"
                self._add_log("Token Kontrol", f"Geçerli: {name} ({token_type})", "success")
                return {"status": "success", "msg": f"✅ Geçerli Hesap: {name}"}
            elif req.status_code == 401:
                self._add_log("Token Kontrol", f"Geçersiz token ({token_type})", "error")
                return {"status": "error", "msg": "❌ Geçersiz veya patlamış token!"}
            elif req.status_code == 403:
                self._add_log("Token Kontrol", f"Kilitli token ({token_type})", "error")
                return {"status": "error", "msg": "⚠️ Token kilitli (Telefon veya E-posta doğrulaması gerekiyor)!"}
            elif req.status_code == 429:
                self._add_log("Token Kontrol", "Rate limit", "error")
                return {"status": "error", "msg": "⚠️ Rate limit! Lütfen birkaç saniye bekleyin."}
            else:
                self._add_log("Token Kontrol", f"API Hatası: {req.status_code}", "error")
                return {"status": "error", "msg": f"❌ API Hatası: {req.status_code}"}
        except requests.exceptions.Timeout:
            logger.warning("Token kontrol: zaman aşımı")
            self._add_log("Token Kontrol", "Zaman aşımı", "error")
            return {"status": "error", "msg": "Bağlantı zaman aşımına uğradı!"}
        except requests.exceptions.RequestException as e:
            logger.error(f"Token kontrol hatası: {e}")
            self._add_log("Token Kontrol", "Bağlantı hatası", "error")
            return {"status": "error", "msg": "Bağlantı hatası!"}
