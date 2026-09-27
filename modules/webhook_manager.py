import requests
import logging

logger = logging.getLogger("ZetaLabs")

DEFAULT_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"

class WebhookManagerMixin:
    def send_webhook(self, url, message, username, avatar_url, embed_title, embed_desc, embed_color):
        if not url:
            return {"status": "error", "msg": "Webhook URL boş olamaz!"}
        
        payload = {}
        if message:
            payload["content"] = message
        if username:
            payload["username"] = username
        if avatar_url:
            payload["avatar_url"] = avatar_url
            
        if embed_title or embed_desc:
            color_int = 0
            if embed_color:
                try:
                    color_int = int(embed_color.replace("#", ""), 16)
                except:
                    color_int = 0
            embed = {}
            if embed_title: embed["title"] = embed_title
            if embed_desc: embed["description"] = embed_desc
            if color_int: embed["color"] = color_int
            payload["embeds"] = [embed]
            
        if not payload:
            return {"status": "error", "msg": "Gönderilecek mesaj veya embed bulunamadı!"}

        try:
            req = requests.post(url, json=payload, headers={"User-Agent": DEFAULT_UA}, timeout=6)
            if req.status_code in (200, 204):
                self._add_log("Webhook", "Mesaj gönderildi", "success")
                return {"status": "success", "msg": "✅ Webhook mesajı başarıyla gönderildi!"}
            else:
                self._add_log("Webhook", f"Gönderim hatası ({req.status_code})", "error")
                return {"status": "error", "msg": f"❌ Gönderim başarısız. (Hata kodu: {req.status_code})"}
        except Exception as e:
            logger.error(f"Webhook hatası: {e}")
            self._add_log("Webhook", "Bağlantı hatası", "error")
            return {"status": "error", "msg": "Bağlantı hatası!"}
