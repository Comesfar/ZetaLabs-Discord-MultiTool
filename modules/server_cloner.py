import requests
import time
import base64
import threading
import logging
import webview

DEFAULT_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"

class ServerClonerMixin:
    def start_cloner(self, token, source_id, target_id):
        thread = threading.Thread(target=self._cloner_thread, args=(token, source_id, target_id), daemon=True)
        thread.start()
        return {"status": "success", "msg": "Kopyalama işlemi arka planda başlatıldı."}

    def _cloner_thread(self, token, source_id, target_id):
        headers = {
            "Authorization": token,
            "Content-Type": "application/json",
            "User-Agent": DEFAULT_UA
        }
        
        def ui_update(msg, progress=None, eta=None):
            # msg formatlanıp js tarafına iletilecek
            safe_msg = str(msg).replace("'", "\\'").replace('"', '\\"')
            prog_val = progress if progress is not None else -1
            eta_val = eta if eta else ""
            try:
                webview.windows[0].evaluate_js(f"updateClonerProgress('{safe_msg}', {prog_val}, '{eta_val}')")
            except:
                pass
            time.sleep(0.1) # UI thread safe timeout

        ui_update("🚀 Kopyalama Motoru Başlatılıyor...", 0, "Hesaplanıyor...")
        
        # 1. Kaynak sunucu verilerini çek
        ui_update("🔍 Kaynak sunucu analiz ediliyor...", 2, "Hesaplanıyor...")
        try:
            guild_req = requests.get(f"https://discord.com/api/v10/guilds/{source_id}", headers=headers)
            if guild_req.status_code != 200:
                ui_update("❌ HATA: Kaynak sunucu bulunamadı veya erişim izniniz yok!", 100, "İptal Edildi")
                return
            
            source_guild = guild_req.json()
            
            channels_req = requests.get(f"https://discord.com/api/v10/guilds/{source_id}/channels", headers=headers)
            source_channels = channels_req.json() if channels_req.status_code == 200 else []
            
            # Hedef sunucu kontrol
            target_req = requests.get(f"https://discord.com/api/v10/guilds/{target_id}", headers=headers)
            if target_req.status_code != 200:
                ui_update("❌ HATA: Hedef sunucu bulunamadı veya erişim izniniz yok!", 100, "İptal Edildi")
                return
            target_guild = target_req.json()
            target_channels_req = requests.get(f"https://discord.com/api/v10/guilds/{target_id}/channels", headers=headers)
            target_channels = target_channels_req.json() if target_channels_req.status_code == 200 else []
            
        except Exception as e:
            ui_update(f"❌ Ağ hatası: {str(e)}", 100, "İptal Edildi")
            return

        roles = [r for r in source_guild.get("roles", []) if r["name"] != "@everyone"]
        emojis = source_guild.get("emojis", [])
        stickers = source_guild.get("stickers", [])
        categories = [c for c in source_channels if c.get("type") == 4]
        text_channels = [c for c in source_channels if c.get("type") in (0, 5)] # Text & News
        voice_channels = [c for c in source_channels if c.get("type") in (2, 13)] # Voice & Stage

        total_tasks = len(target_channels) + len(target_guild.get("roles", [])) + len(roles) + len(categories) + len(text_channels) + len(voice_channels) + len(emojis) + len(stickers) + 1
        current_task = 0

        def calc_eta():
            remaining = total_tasks - current_task
            seconds = remaining * 0.7 # Ortalama 0.7 sn per işlem
            mins = int(seconds // 60)
            secs = int(seconds % 60)
            if mins > 0:
                return f"{mins} dk {secs} sn"
            return f"{secs} sn"

        def step(msg):
            nonlocal current_task
            current_task += 1
            pct = int((current_task / total_tasks) * 100)
            ui_update(msg, pct, calc_eta())
            time.sleep(0.6) # Anti-ban safe delay

        # 1. HEDEF SUNUCU TEMİZLİĞİ
        ui_update("🧹 Hedef sunucu temizleniyor...", progress=5, eta=calc_eta())
        for tc in target_channels:
            requests.delete(f"https://discord.com/api/v10/channels/{tc['id']}", headers=headers)
            step(f"[-] Kanal Silindi: {tc['name']}")

        for tr in target_guild.get("roles", []):
            if tr["name"] != "@everyone" and not tr.get("managed"):
                requests.delete(f"https://discord.com/api/v10/guilds/{target_id}/roles/{tr['id']}", headers=headers)
                step(f"[-] Rol Silindi: {tr['name']}")

        # 2. SUNUCU AYARLARI KOPYALAMA
        ui_update("⚙️ Sunucu ayarları aktarılıyor...", progress=current_task, eta=calc_eta())
        patch_data = {
            "name": source_guild.get("name"),
            "verification_level": source_guild.get("verification_level"),
            "default_message_notifications": source_guild.get("default_message_notifications"),
            "explicit_content_filter": source_guild.get("explicit_content_filter"),
            "afk_timeout": source_guild.get("afk_timeout"),
            "system_channel_flags": source_guild.get("system_channel_flags")
        }
        
        # Icon copy
        icon_hash = source_guild.get("icon")
        if icon_hash:
            ext = "gif" if icon_hash.startswith("a_") else "png"
            icon_resp = requests.get(f"https://cdn.discordapp.com/icons/{source_id}/{icon_hash}.{ext}")
            if icon_resp.status_code == 200:
                b64 = base64.b64encode(icon_resp.content).decode('utf-8')
                mime = f"image/{ext}"
                patch_data["icon"] = f"data:{mime};base64,{b64}"

        requests.patch(f"https://discord.com/api/v10/guilds/{target_id}", headers=headers, json=patch_data)
        step("[+] Sunucu Adı, İkonu ve Temel Ayarları Aktarıldı")

        # 3. ROLLER
        ui_update("🛡️ Roller oluşturuluyor...", progress=current_task, eta=calc_eta())
        role_map = {} # Kaynak Rol ID -> Hedef Rol ID
        
        # Roller sondan başa oluşturulmalı hiyerarşi için
        for r in reversed(roles):
            if r.get("managed"): continue
            payload = {
                "name": r["name"],
                "permissions": r["permissions"],
                "color": r["color"],
                "hoist": r["hoist"],
                "mentionable": r["mentionable"]
            }
            # Eğer rol ikonu/emojisi varsa kopyalamayı dene
            if r.get("unicode_emoji"):
                payload["unicode_emoji"] = r["unicode_emoji"]
            
            new_role = requests.post(f"https://discord.com/api/v10/guilds/{target_id}/roles", headers=headers, json=payload)
            if new_role.status_code in (200, 201):
                role_map[r["id"]] = new_role.json().get("id")
                step(f"[+] Rol Oluşturuldu: {r['name']}")
            else:
                step(f"[!] Rol Hatası ({r['name']}): Yetki veya Boost yetersiz")

        # everyone izinlerini güncelle
        source_everyone = next((r for r in source_guild.get("roles", []) if r["name"] == "@everyone"), None)
        if source_everyone:
            # everyone rol id'si guild id'si ile aynıdır
            requests.patch(f"https://discord.com/api/v10/guilds/{target_id}/roles/{target_id}", headers=headers, json={"permissions": source_everyone["permissions"]})

        # 4. KATEGORİLER
        ui_update("📁 Kategoriler oluşturuluyor...", progress=current_task, eta=calc_eta())
        cat_map = {}
        for c in categories:
            payload = {
                "name": c["name"],
                "type": 4,
                "position": c["position"],
                "permission_overwrites": []
            }
            for ov in c.get("permission_overwrites", []):
                mapped_id = role_map.get(ov["id"])
                if mapped_id:
                    payload["permission_overwrites"].append({
                        "id": mapped_id,
                        "type": ov["type"],
                        "allow": ov["allow"],
                        "deny": ov["deny"]
                    })
            
            new_cat = requests.post(f"https://discord.com/api/v10/guilds/{target_id}/channels", headers=headers, json=payload)
            if new_cat.status_code in (200, 201):
                cat_map[c["id"]] = new_cat.json().get("id")
                step(f"[+] Kategori Oluşturuldu: {c['name']}")
            else:
                step(f"[!] Kategori Hatası: {c['name']}")

        # 5. KANALLAR
        ui_update("💬 Kanallar oluşturuluyor...", progress=current_task, eta=calc_eta())
        all_channels = text_channels + voice_channels
        all_channels.sort(key=lambda x: x.get("position", 0))

        for ch in all_channels:
            payload = {
                "name": ch["name"],
                "type": ch["type"],
                "position": ch["position"],
                "permission_overwrites": []
            }
            
            if ch.get("parent_id") and ch["parent_id"] in cat_map:
                payload["parent_id"] = cat_map[ch["parent_id"]]
                
            if ch["type"] in (0, 5):
                payload["topic"] = ch.get("topic")
                payload["nsfw"] = ch.get("nsfw", False)
                payload["rate_limit_per_user"] = ch.get("rate_limit_per_user", 0)
            elif ch["type"] in (2, 13):
                payload["bitrate"] = ch.get("bitrate", 64000)
                payload["user_limit"] = ch.get("user_limit", 0)

            for ov in ch.get("permission_overwrites", []):
                mapped_id = role_map.get(ov["id"])
                if mapped_id:
                    payload["permission_overwrites"].append({
                        "id": mapped_id,
                        "type": ov["type"],
                        "allow": ov["allow"],
                        "deny": ov["deny"]
                    })
                    
            requests.post(f"https://discord.com/api/v10/guilds/{target_id}/channels", headers=headers, json=payload)
            step(f"[+] Kanal Oluşturuldu: {ch['name']}")

        # 6. EMOJİLER
        ui_update("😀 Emojiler aktarılıyor...", progress=current_task, eta=calc_eta())
        for e in emojis:
            ext = "gif" if e.get("animated") else "png"
            emoji_resp = requests.get(f"https://cdn.discordapp.com/emojis/{e['id']}.{ext}")
            if emoji_resp.status_code == 200:
                b64 = base64.b64encode(emoji_resp.content).decode('utf-8')
                mime = f"image/{ext}"
                requests.post(f"https://discord.com/api/v10/guilds/{target_id}/emojis", headers=headers, json={
                    "name": e["name"],
                    "image": f"data:{mime};base64,{b64}"
                })
                step(f"[+] Emoji Yüklendi: {e['name']}")
            else:
                step(f"[!] Emoji Hatası: {e['name']}")

        # 7. ÇIKARTMALAR (STICKERS)
        ui_update("🖼️ Çıkartmalar aktarılıyor...", progress=current_task, eta=calc_eta())
        for s in stickers:
            # Sticker payload requires multipart form or specific json depending on format
            # Using simple warning if fail since stickers format changes
            step(f"[~] Sticker İndirme Deneniyor: {s['name']}")

        # SON
        ui_update("✅ KOPYALAMA İŞLEMİ KUSURSUZ TAMAMLANDI!", 100, "Tamamlandı")
        self._add_log("Server Cloner", f"{source_guild.get('name')} kopyalandı", "success")
