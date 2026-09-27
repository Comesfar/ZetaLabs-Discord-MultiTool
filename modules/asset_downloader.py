import requests
import logging
import webview
import os

logger = logging.getLogger("ZetaLabs")

DEFAULT_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"

class AssetDownloaderMixin:
    def fetch_assets(self, token, token_type, target_id, target_type):
        headers = {
            "Authorization": f"Bot {token}" if token_type == "bot" else token,
            "User-Agent": DEFAULT_UA
        }
        try:
            url = f"https://discord.com/api/v10/{'users' if target_type == 'user' else 'guilds'}/{target_id}"
            req = requests.get(url, headers=headers, timeout=6)
            
            if req.status_code == 200:
                data = req.json()
                name = data.get("username") or data.get("name")
                result = {"status": "success", "avatar": None, "banner": None, "name": name}
                
                icon_hash = data.get("avatar") or data.get("icon")
                if icon_hash:
                    ext = "gif" if icon_hash.startswith("a_") else "png"
                    img_type = "avatars" if target_type == "user" else "icons"
                    result["avatar"] = f"https://cdn.discordapp.com/{img_type}/{target_id}/{icon_hash}.{ext}?size=1024"

                banner_hash = data.get("banner")
                if banner_hash:
                    ext = "gif" if banner_hash.startswith("a_") else "png"
                    result["banner"] = f"https://cdn.discordapp.com/banners/{target_id}/{banner_hash}.{ext}?size=1024"

                self._add_log("Asset Çekme", f"{name} ({target_type}) — görseller alındı", "success")
                return result
            
            # Sunucu özelinde: Bot sunucuda değilse açık sunucu önizlemesini dene
            if target_type == "guild" and req.status_code in (403, 404):
                preview_req = requests.get(f"https://discord.com/api/v10/guilds/{target_id}/preview", headers=headers, timeout=6)
                if preview_req.status_code == 200:
                    data = preview_req.json()
                    name = data.get("name")
                    result = {"status": "success", "avatar": None, "banner": None, "name": name}
                    icon_hash = data.get("icon")
                    if icon_hash:
                        ext = "gif" if icon_hash.startswith("a_") else "png"
                        result["avatar"] = f"https://cdn.discordapp.com/icons/{target_id}/{icon_hash}.{ext}?size=1024"
                    banner_hash = data.get("discovery_splash") or data.get("splash")
                    if banner_hash:
                        result["banner"] = f"https://cdn.discordapp.com/discovery-splashes/{target_id}/{banner_hash}.png?size=1024"
                    self._add_log("Asset Çekme", f"{name} (Açık Sunucu Önizleme) — görseller alındı", "success")
                    return result

            self._add_log("Asset Çekme", f"ID: {target_id} — veri bulunamadı", "error")
            return {"status": "error", "msg": "Veri bulunamadı veya yetkisiz token!"}
        except requests.exceptions.Timeout:
            logger.warning("Asset çekme: zaman aşımı")
            self._add_log("Asset Çekme", "Zaman aşımı", "error")
            return {"status": "error", "msg": "Bağlantı zaman aşımına uğradı!"}
        except requests.exceptions.RequestException as e:
            logger.error(f"Asset çekme hatası: {e}")
            self._add_log("Asset Çekme", "Bağlantı hatası", "error")
            return {"status": "error", "msg": "Bağlantı Hatası!"}

    def download_asset(self, url, default_name):
        try:
            result = webview.windows[0].create_file_dialog(
                webview.SAVE_DIALOG,
                save_filename=default_name,
                file_types=('Image Files (*.png;*.gif;*.jpg)',)
            )
            if not result:
                return {"status": "cancelled", "msg": "Kaydetme iptal edildi."}
            
            save_path = result if isinstance(result, str) else result[0]
            
            response = requests.get(url, headers={"User-Agent": DEFAULT_UA}, timeout=10)
            if response.status_code == 200:
                with open(save_path, 'wb') as f:
                    f.write(response.content)
                self._add_log("Asset İndirme", f"{default_name} → {os.path.basename(save_path)}", "success")
                return {"status": "success", "msg": f"✅ Kaydedildi: {os.path.basename(save_path)}"}
            return {"status": "error", "msg": "Görsel indirilemedi!"}
        except Exception as e:
            logger.error(f"Asset indirme hatası: {e}")
            return {"status": "error", "msg": "İndirme hatası!"}
