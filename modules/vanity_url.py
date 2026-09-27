import requests
import logging

logger = logging.getLogger("ZetaLabs")

DEFAULT_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"

class VanityUrlMixin:
    def check_vanity_url(self, token, token_type, vanity_code):
        headers = {"User-Agent": DEFAULT_UA}
        if token:
            headers["Authorization"] = f"Bot {token}" if token_type == "bot" else token

        try:
            req = requests.get(f"https://discord.com/api/v10/invites/{vanity_code}?with_counts=true", headers=headers, timeout=5)
            
            if req.status_code == 200:
                data = req.json()
                guild = data.get("guild", {})
                self._add_log("Vanity Sorgusu", f"/{vanity_code} -> DOLU", "error")
                return {
                    "status": "taken", 
                    "msg": "❌ Bu URL alınmış!", 
                    "guild_name": guild.get("name", "Bilinmeyen Sunucu"),
                    "member_count": data.get("approximate_member_count", "—")
                }
            elif req.status_code == 404:
                self._add_log("Vanity Sorgusu", f"/{vanity_code} -> BOŞTA", "success")
                return {"status": "available", "msg": "✅ Bu URL boşta, alınabilir!"}
            elif req.status_code == 429:
                self._add_log("Vanity Sorgusu", f"/{vanity_code} -> Rate Limit", "error")
                return {"status": "error", "msg": "⚠️ Çok fazla istek atıldı (Rate Limit). Biraz bekleyin."}
            else:
                self._add_log("Vanity Sorgusu", f"/{vanity_code} -> Hata ({req.status_code})", "error")
                return {"status": "error", "msg": f"Bilinmeyen hata! (Kod: {req.status_code})"}
        except requests.exceptions.Timeout:
            self._add_log("Vanity Sorgusu", "Zaman aşımı", "error")
            return {"status": "error", "msg": "Bağlantı zaman aşımına uğradı!"}
        except requests.exceptions.RequestException as e:
            self._add_log("Vanity Sorgusu", "Bağlantı hatası", "error")
            return {"status": "error", "msg": "Bağlantı hatası!"}
