import requests
import logging
from datetime import datetime, timezone

logger = logging.getLogger("ZetaLabs")

DEFAULT_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"

class UserDetailMixin:
    def get_user_details(self, token, token_type):
        headers = {
            "Authorization": f"Bot {token}" if token_type == "bot" else token,
            "User-Agent": DEFAULT_UA
        }
        try:
            user_req = requests.get("https://discord.com/api/v10/users/@me", headers=headers, timeout=6)
            if user_req.status_code != 200:
                self._add_log("Hesap Detay", "Token geçersiz veya yetkisiz", "error")
                return {"status": "error", "msg": "Token geçersiz veya yetkisiz!"}

            user = user_req.json()
            user_id = int(user.get("id", 0))
            
            created_timestamp = ((user_id >> 22) + 1420070400000) / 1000
            created_date = datetime.fromtimestamp(created_timestamp, tz=timezone.utc).strftime("%d/%m/%Y %H:%M UTC")

            premium_types = {0: "Yok", 1: "Nitro Classic", 2: "Nitro", 3: "Nitro Basic"}
            nitro = premium_types.get(user.get("premium_type", 0), "Yok")

            avatar_hash = user.get("avatar")
            avatar_url = None
            if avatar_hash:
                ext = "gif" if avatar_hash.startswith("a_") else "png"
                avatar_url = f"https://cdn.discordapp.com/avatars/{user_id}/{avatar_hash}.{ext}?size=256"

            banner_hash = user.get("banner")
            banner_url = None
            if banner_hash:
                ext = "gif" if banner_hash.startswith("a_") else "png"
                banner_url = f"https://cdn.discordapp.com/banners/{user_id}/{banner_hash}.{ext}?size=600"

            guild_count = "—"
            friends_count = "—"
            blocked_count = "—"
            connections_list = []
            
            if token_type == "user":
                try:
                    guilds_req = requests.get("https://discord.com/api/v10/users/@me/guilds", headers=headers, timeout=5)
                    if guilds_req.status_code == 200:
                        guild_count = len(guilds_req.json())
                except Exception:
                    pass

                try:
                    rel_req = requests.get("https://discord.com/api/v10/users/@me/relationships", headers=headers, timeout=5)
                    if rel_req.status_code == 200:
                        relationships = rel_req.json()
                        friends_count = sum(1 for r in relationships if r.get('type') == 1)
                        blocked_count = sum(1 for r in relationships if r.get('type') == 2)
                except Exception:
                    pass

                try:
                    conn_req = requests.get("https://discord.com/api/v10/users/@me/connections", headers=headers, timeout=5)
                    if conn_req.status_code == 200:
                        conns = conn_req.json()
                        for c in conns:
                            connections_list.append({"type": c.get("type"), "name": c.get("name")})
                except Exception:
                    pass

            flags = user.get("public_flags", 0)
            badge_map = {
                1: "Discord Staff",
                2: "Partner",
                4: "HypeSquad Events",
                8: "Bug Hunter Lv1",
                64: "HypeSquad Bravery",
                128: "HypeSquad Brilliance",
                256: "HypeSquad Balance",
                512: "Early Supporter",
                16384: "Bug Hunter Lv2",
                65536: "Verified Bot",
                131072: "Early Bot Developer",
                262144: "Discord Moderator",
                4194304: "Active Developer",
            }
            badges = [name for bit, name in badge_map.items() if flags & bit]

            disc = user.get("discriminator", "0")
            display_disc = "" if disc == "0" else f"#{disc}"

            result = {
                "status": "success",
                "username": user.get("username", "—") + display_disc,
                "display_name": user.get("global_name") or user.get("username", "—"),
                "discriminator": disc,
                "id": str(user_id),
                "avatar_url": avatar_url,
                "banner_url": banner_url,
                "banner_color": user.get("accent_color"),
                "created_date": created_date,
                "nitro": nitro,
                "mfa_enabled": user.get("mfa_enabled", False),
                "locale": user.get("locale", "—"),
                "email": user.get("email", "—"),
                "phone": user.get("phone", "—") or "—",
                "verified": user.get("verified", False),
                "guild_count": guild_count,
                "friends_count": friends_count,
                "blocked_count": blocked_count,
                "connections": connections_list,
                "badges": badges,
                "is_bot": user.get("bot", False)
            }

            self._add_log("Hesap Detay", f"{result['username']} bilgileri çekildi", "success")
            return result
        except requests.exceptions.Timeout:
            logger.warning("Kullanıcı detay: zaman aşımı")
            self._add_log("Hesap Detay", "Zaman aşımı", "error")
            return {"status": "error", "msg": "Bağlantı zaman aşımına uğradı!"}
        except requests.exceptions.RequestException as e:
            logger.error(f"Kullanıcı detay hatası: {e}")
            self._add_log("Hesap Detay", "Bağlantı hatası", "error")
            return {"status": "error", "msg": "Bağlantı hatası!"}

    def get_user_by_id(self, target_id, auth_token, token_type):
        if not auth_token:
            return {"status": "error", "msg": "Ayarlarda aracı token bulunamadı! ID sorgusu için Ayarlar kısmına bir token girmelisiniz."}
            
        headers = {
            "Authorization": f"Bot {auth_token}" if token_type == "bot" else auth_token,
            "User-Agent": DEFAULT_UA
        }
        try:
            user_req = requests.get(f"https://discord.com/api/v10/users/{target_id}", headers=headers, timeout=6)
            if user_req.status_code == 404:
                return {"status": "error", "msg": "Kullanıcı bulunamadı!"}
            elif user_req.status_code != 200:
                return {"status": "error", "msg": f"API Hatası: Yetkisiz token veya limit aşıldı ({user_req.status_code})"}

            user = user_req.json()
            user_id = int(user.get("id", 0))
            
            created_timestamp = ((user_id >> 22) + 1420070400000) / 1000
            created_date = datetime.fromtimestamp(created_timestamp, tz=timezone.utc).strftime("%d/%m/%Y %H:%M UTC")

            avatar_hash = user.get("avatar")
            avatar_url = None
            if avatar_hash:
                ext = "gif" if avatar_hash.startswith("a_") else "png"
                avatar_url = f"https://cdn.discordapp.com/avatars/{user_id}/{avatar_hash}.{ext}?size=256"

            banner_hash = user.get("banner")
            banner_url = None
            if banner_hash:
                ext = "gif" if banner_hash.startswith("a_") else "png"
                banner_url = f"https://cdn.discordapp.com/banners/{user_id}/{banner_hash}.{ext}?size=600"

            flags = user.get("public_flags", 0)
            badge_map = {
                1: "Discord Staff",
                2: "Partner",
                4: "HypeSquad Events",
                8: "Bug Hunter Lv1",
                64: "HypeSquad Bravery",
                128: "HypeSquad Brilliance",
                256: "HypeSquad Balance",
                512: "Early Supporter",
                16384: "Bug Hunter Lv2",
                65536: "Verified Bot",
                131072: "Early Bot Developer",
                262144: "Discord Moderator",
                4194304: "Active Developer",
            }
            badges = [name for bit, name in badge_map.items() if flags & bit]

            disc = user.get("discriminator", "0")
            display_disc = "" if disc == "0" else f"#{disc}"

            result = {
                "status": "success",
                "username": user.get("username", "—") + display_disc,
                "display_name": user.get("global_name") or user.get("username", "—"),
                "discriminator": disc,
                "id": str(user_id),
                "avatar_url": avatar_url,
                "banner_url": banner_url,
                "banner_color": user.get("accent_color"),
                "created_date": created_date,
                "badges": badges,
                "is_bot": user.get("bot", False)
            }

            self._add_log("Hesap Detay (ID)", f"{result['username']} bilgileri çekildi", "success")
            return result
        except requests.exceptions.Timeout:
            return {"status": "error", "msg": "Bağlantı zaman aşımına uğradı!"}
        except requests.exceptions.RequestException:
            return {"status": "error", "msg": "Bağlantı hatası!"}
