import requests
import logging
import webview
import os

DEFAULT_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"

class EmojiDownloaderMixin:
    def fetch_guild_emojis(self, token, token_type, guild_id):
        headers = {
            "Authorization": f"Bot {token}" if token_type == "bot" else token,
            "User-Agent": DEFAULT_UA
        }
        try:
            req = requests.get(f"https://discord.com/api/v10/guilds/{guild_id}/emojis", headers=headers, timeout=5)
            if req.status_code == 200:
                emojis = req.json()
                if not emojis:
                    return {"status": "error", "msg": "Bu sunucuda hiç emoji yok!"}
                
                emoji_list = []
                for e in emojis:
                    ext = "gif" if e.get("animated") else "png"
                    emoji_list.append({
                        "name": e.get("name"),
                        "id": e.get("id"),
                        "url": f"https://cdn.discordapp.com/emojis/{e.get('id')}.{ext}?size=128",
                        "animated": e.get("animated", False)
                    })
                
                self._add_log("Emoji İndirici", f"{len(emoji_list)} emoji listelendi", "success")
                return {"status": "success", "emojis": emoji_list, "count": len(emoji_list)}
            else:
                return {"status": "error", "msg": "Sunucu bulunamadı veya erişim izni yok!"}
        except Exception as e:
            return {"status": "error", "msg": "Bağlantı hatası!"}

    def download_emojis_bulk(self, emoji_list):
        if not emoji_list:
            return {"status": "error", "msg": "İndirilecek emoji listesi boş!"}
            
        try:
            result = webview.windows[0].create_file_dialog(
                webview.FOLDER_DIALOG
            )
            if not result:
                return {"status": "cancelled", "msg": "Klasör seçilmedi."}
                
            folder_path = result if isinstance(result, str) else result[0]
            
            success_count = 0
            for e in emoji_list:
                ext = "gif" if e.get("animated") else "png"
                clean_name = "".join(c for c in e.get("name", "emoji") if c.isalnum() or c in ("_", "-"))
                file_name = f"{clean_name}_{e.get('id')}.{ext}"
                save_path = os.path.join(folder_path, file_name)
                
                try:
                    resp = requests.get(e.get("url"), headers={"User-Agent": DEFAULT_UA}, timeout=6)
                    if resp.status_code == 200:
                        with open(save_path, 'wb') as f:
                            f.write(resp.content)
                        success_count += 1
                except:
                    pass
                    
            self._add_log("Emoji İndirici", f"{success_count}/{len(emoji_list)} emoji indirildi", "success")
            return {"status": "success", "msg": f"✅ {success_count} emoji başarıyla indirildi!", "folder": folder_path}
            
        except Exception as e:
            return {"status": "error", "msg": f"İndirme sırasında hata: {e}"}
