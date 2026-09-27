import requests
import logging
from datetime import datetime, timezone

logger = logging.getLogger("ZetaLabs")

DEFAULT_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"

class GuildInfoMixin:
    def get_guild_info(self, token, token_type, guild_id):
        headers = {
            "Authorization": f"Bot {token}" if token_type == "bot" else token,
            "User-Agent": DEFAULT_UA
        }
        try:
            req = requests.get(
                f"https://discord.com/api/v10/guilds/{guild_id}?with_counts=true",
                headers=headers, timeout=6
            )
            
            data = None
            if req.status_code == 200:
                data = req.json()
            else:
                # Bot sunucuda olmayabilir, açık sunucu önizlemesini dene
                preview_req = requests.get(f"https://discord.com/api/v10/guilds/{guild_id}/preview", headers=headers, timeout=6)
                if preview_req.status_code == 200:
                    data = preview_req.json()

            if not data:
                self._add_log("Sunucu Bilgi", f"ID: {guild_id} — erişilemedi", "error")
                return {"status": "error", "msg": "Sunucu bulunamadı veya erişim yetkisi yok!"}

            guild_id_int = int(data.get("id", guild_id))
            created_timestamp = ((guild_id_int >> 22) + 1420070400000) / 1000
            created_date = datetime.fromtimestamp(created_timestamp, tz=timezone.utc).strftime("%d/%m/%Y %H:%M UTC")

            icon_hash = data.get("icon")
            icon_url = None
            if icon_hash:
                ext = "gif" if icon_hash.startswith("a_") else "png"
                icon_url = f"https://cdn.discordapp.com/icons/{guild_id}/{icon_hash}.{ext}?size=256"

            banner_hash = data.get("banner") or data.get("discovery_splash") or data.get("splash")
            banner_url = None
            if banner_hash:
                ext = "gif" if banner_hash.startswith("a_") else "png"
                subfolder = "banners" if data.get("banner") else "discovery-splashes"
                banner_url = f"https://cdn.discordapp.com/{subfolder}/{guild_id}/{banner_hash}.{ext}?size=600"

            verification_levels = {0: "Yok", 1: "Düşük", 2: "Orta", 3: "Yüksek", 4: "En Yüksek"}
            verification = verification_levels.get(data.get("verification_level", 0), "Bilinmiyor")

            boost_tiers = {0: "Yok", 1: "Seviye 1", 2: "Seviye 2", 3: "Seviye 3"}

            result = {
                "status": "success",
                "name": data.get("name", "—"),
                "id": str(guild_id_int),
                "icon_url": icon_url,
                "banner_url": banner_url,
                "owner_id": data.get("owner_id", "—"),
                "created_date": created_date,
                "member_count": data.get("approximate_member_count", "—"),
                "online_count": data.get("approximate_presence_count", "—"),
                "boost_level": boost_tiers.get(data.get("premium_tier", 0), "—"),
                "boost_count": data.get("premium_subscription_count", 0),
                "verification": verification,
                "role_count": len(data.get("roles", [])),
                "emoji_count": len(data.get("emojis", [])),
                "channel_count": "—",  
                "description": data.get("description") or "—",
                "vanity_url": data.get("vanity_url_code") or "—",
            }

            self._add_log("Sunucu Bilgi", f"{result['name']} bilgileri çekildi", "success")
            return result
        except requests.exceptions.Timeout:
            logger.warning("Sunucu bilgi: zaman aşımı")
            self._add_log("Sunucu Bilgi", "Zaman aşımı", "error")
            return {"status": "error", "msg": "Bağlantı zaman aşımına uğradı!"}
        except requests.exceptions.RequestException as e:
            logger.error(f"Sunucu bilgi hatası: {e}")
            self._add_log("Sunucu Bilgi", "Bağlantı hatası", "error")
            return {"status": "error", "msg": "Bağlantı hatası!"}
