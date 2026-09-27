import webview
import requests
import json
import os
import sys
import logging
from datetime import datetime

from modules import (
    TokenValidatorMixin,
    BulkCheckerMixin,
    AssetDownloaderMixin,
    UserDetailMixin,
    GuildInfoMixin,
    VanityUrlMixin,
    WebhookManagerMixin,
    InviteResolverMixin,
    SnowflakeDecoderMixin,
    TokenDecoderMixin,
    EmojiDownloaderMixin,
    ServerClonerMixin
)

# Logging ayarları
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger("ZetaLabs")

# Mutlak yol — CWD'den bağımsız çalışır
BASE_DIR = os.path.dirname(os.path.abspath(sys.argv[0]))
SETTINGS_FILE = os.path.join(BASE_DIR, 'settings.json')
LOG_FILE = os.path.join(BASE_DIR, 'history.json')

class ZetaApi(
    TokenValidatorMixin,
    BulkCheckerMixin,
    AssetDownloaderMixin,
    UserDetailMixin,
    GuildInfoMixin,
    VanityUrlMixin,
    WebhookManagerMixin,
    InviteResolverMixin,
    SnowflakeDecoderMixin,
    TokenDecoderMixin,
    EmojiDownloaderMixin,
    ServerClonerMixin
):
    def __init__(self):
        # Program ilk açıldığında ayar dosyası yoksa oluştur
        if not os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
                json.dump({"bot_token": "", "self_token": ""}, f, ensure_ascii=False)
        if not os.path.exists(LOG_FILE):
            with open(LOG_FILE, 'w', encoding='utf-8') as f:
                json.dump([], f)

    # =============================================
    #  YARDIMCI METODLAR
    # =============================================
    def _mask_token(self, token):
        """Token'ı güvenli şekilde maskeler. Kısa token'larda bile tam gizleme sağlar."""
        if len(token) <= 8:
            return "•" * len(token)
        if len(token) <= 30:
            return token[:4] + "•" * (len(token) - 8) + token[-4:]
        return token[:20] + "..." + token[-6:]

    # =============================================
    #  İŞLEM GEÇMİŞİ (LOG)
    # =============================================
    def _add_log(self, action, detail, status):
        """Her işlem sonrası geçmişe kayıt ekler. Asla hata fırlatmaz."""
        try:
            try:
                with open(LOG_FILE, 'r', encoding='utf-8') as f:
                    logs = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                logs = []
            
            logs.insert(0, {
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "action": action,
                "detail": detail,
                "status": status
            })
            # Maksimum 200 kayıt tut
            logs = logs[:200]
            with open(LOG_FILE, 'w', encoding='utf-8') as f:
                json.dump(logs, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Log kaydı yazılamadı: {e}")

    def get_logs(self):
        try:
            with open(LOG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def clear_logs(self):
        try:
            with open(LOG_FILE, 'w', encoding='utf-8') as f:
                json.dump([], f)
            return {"status": "success", "msg": "🗑️ Geçmiş temizlendi!"}
        except Exception as e:
            logger.error(f"Log temizleme hatası: {e}")
            return {"status": "error", "msg": "❌ Geçmiş temizlenemedi!"}

    # =============================================
    #  AYARLAR MODÜLÜ
    # =============================================
    def get_settings(self):
        try:
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError, IOError) as e:
            logger.error(f"Ayarlar okunamadı: {e}")
            return {"bot_token": "", "self_token": ""}

    def save_settings(self, bot_token, self_token):
        try:
            with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
                json.dump({"bot_token": bot_token, "self_token": self_token}, f)
            self._add_log("Ayarlar", "Token ayarları güncellendi", "success")
            return {"status": "success", "msg": "✅ Ayarlar başarıyla kaydedildi!"}
        except Exception as e:
            logger.error(f"Ayarlar kaydedilemedi: {e}")
            return {"status": "error", "msg": f"❌ Kaydetme hatası: {e}"}

    # =============================================
    #  PENCERE KONTROLLERİ
    # =============================================
    def minimize_window(self):
        webview.windows[0].minimize()

    def toggle_maximize(self):
        w = webview.windows[0]
        if w.maximized:
            w.restore()
        else:
            w.maximize()

    def close_window(self):
        webview.windows[0].destroy()

if __name__ == '__main__':
    api = ZetaApi()
    window = webview.create_window(
        title='ZetaLabs Discord Suite', 
        url=os.path.join(BASE_DIR, 'web', 'index.html'), 
        js_api=api, 
        width=950, 
        height=700,
        min_size=(800, 550),
        background_color='#09090b',
        frameless=False, 
        easy_drag=False 
    )
    webview.start()