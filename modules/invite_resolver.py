import requests
import logging

logger = logging.getLogger("ZetaLabs")

DEFAULT_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"

class InviteResolverMixin:
    def resolve_invite(self, invite_code):
        if not invite_code:
            return {"status": "error", "msg": "Davet kodu boş olamaz!"}
            
        if "/" in invite_code:
            invite_code = invite_code.split("/")[-1]
            
        try:
            req = requests.get(
                f"https://discord.com/api/v10/invites/{invite_code}?with_counts=true",
                headers={"User-Agent": DEFAULT_UA},
                timeout=6
            )
            if req.status_code == 200:
                data = req.json()
                guild = data.get("guild", {})
                inviter = data.get("inviter", {})
                
                result = {
                    "status": "success",
                    "code": data.get("code"),
                    "guild_name": guild.get("name", "Bilinmeyen Sunucu"),
                    "guild_id": guild.get("id", "—"),
                    "member_count": data.get("approximate_member_count", "—"),
                    "online_count": data.get("approximate_presence_count", "—"),
                    "inviter": f"{inviter.get('username', '')}#{inviter.get('discriminator', '0')}" if inviter else "—",
                    "expires_at": data.get("expires_at") or "Süresiz"
                }
                
                icon_hash = guild.get("icon")
                if icon_hash:
                    ext = "gif" if icon_hash.startswith("a_") else "png"
                    result["icon_url"] = f"https://cdn.discordapp.com/icons/{guild.get('id')}/{icon_hash}.{ext}?size=256"
                else:
                    result["icon_url"] = None
                    
                self._add_log("Davet Çözümleyici", f"{invite_code} çözümlendi", "success")
                return result
            else:
                self._add_log("Davet Çözümleyici", f"{invite_code} bulunamadı", "error")
                return {"status": "error", "msg": "❌ Geçersiz veya süresi dolmuş davet kodu!"}
        except Exception as e:
            logger.error(f"Davet çözümleme hatası: {e}")
            return {"status": "error", "msg": "Bağlantı hatası!"}
