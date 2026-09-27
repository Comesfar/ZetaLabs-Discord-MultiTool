import sys
import threading
import asyncio
import customtkinter as ctk
from tkinter import messagebox
import discord

# --- CTK AYARLARI ---
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# --- KONSOL YAZDIRMA YÖNLENDİRİCİSİ (Arayüz Çökmesini Engeller) ---
class PrintRedirector:
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, string):
        # İşlemleri arka plan thread'inden ana arayüze güvenle aktarır
        self.text_widget.after(0, self._insert, string)

    def _insert(self, string):
        self.text_widget.insert("end", string)
        self.text_widget.see("end")

    def flush(self):
        pass

# --- LOG YAZDIRMA FONKSİYONLARI ---
def print_add(message):
    print(f"[+] {message}")

def print_delete(message):
    print(f"[-] {message}")

def print_warning(message):
    print(f"[UYARI] {message}")

def print_error(message):
    print(f"[HATA] {message}")

# --- KOPYALAMA İŞLEMLERİ ---
class Clone:
    @staticmethod
    async def roles_delete(guild_to: discord.Guild):
        for role in guild_to.roles:
            try:
                if role.name != "@everyone":
                    await role.delete()
                    print_delete(f"Rol Silindi: {role.name}")
            except discord.Forbidden:
                print_error(f"Rol Silerken Hata Oluştu: {role.name}")
            except discord.HTTPException:
                print_error(f"Rol Silinemiyor: {role.name}")

    @staticmethod
    async def roles_create(guild_to: discord.Guild, guild_from: discord.Guild):
        roles = [role for role in guild_from.roles if role.name != "@everyone"]
        roles = roles[::-1]
        for role in roles:
            try:
                await guild_to.create_role(
                    name=role.name,
                    permissions=role.permissions,
                    colour=role.colour,
                    hoist=role.hoist,
                    mentionable=role.mentionable
                )
                print_add(f"Rol Oluşturuldu: {role.name}")
            except discord.Forbidden:
                print_error(f"Rol Oluştururken Hata Oluştu: {role.name}")
            except discord.HTTPException:
                print_error(f"Rol Oluşturulamıyor: {role.name}")

    @staticmethod
    async def channels_delete(guild_to: discord.Guild):
        for channel in guild_to.channels:
            try:
                await channel.delete()
                print_delete(f"Kanal Silindi: {channel.name}")
            except discord.Forbidden:
                print_error(f"Kanal Silinirken Hata Oluştu: {channel.name}")
            except discord.HTTPException:
                print_error(f"Kanal Silinemiyor: {channel.name}")

    @staticmethod
    async def categories_create(guild_to: discord.Guild, guild_from: discord.Guild):
        channels = guild_from.categories
        for channel in channels:
            try:
                overwrites_to = {}
                for key, value in channel.overwrites.items():
                    role = discord.utils.get(guild_to.roles, name=key.name)
                    if role:
                        overwrites_to[role] = value
                new_channel = await guild_to.create_category(
                    name=channel.name,
                    overwrites=overwrites_to)
                await new_channel.edit(position=channel.position)
                print_add(f"Kategori Oluşturuldu: {channel.name}")
            except discord.Forbidden:
                print_error(f"Kategori Silinirken Hata Oluştu: {channel.name}")
            except discord.HTTPException:
                print_error(f"Kategori Silinemiyor: {channel.name}")

    @staticmethod
    async def channels_create(guild_to: discord.Guild, guild_from: discord.Guild):
        # Yazı Kanalları
        for channel_text in guild_from.text_channels:
            category = None
            if channel_text.category:
                for cat in guild_to.categories:
                    if cat.name == channel_text.category.name:
                        category = cat
                        break

            overwrites_to = {}
            for key, value in channel_text.overwrites.items():
                role = discord.utils.get(guild_to.roles, name=key.name)
                if role:
                    overwrites_to[role] = value
            try:
                new_channel = await guild_to.create_text_channel(
                    name=channel_text.name,
                    overwrites=overwrites_to,
                    position=channel_text.position,
                    topic=channel_text.topic,
                    slowmode_delay=channel_text.slowmode_delay,
                    nsfw=channel_text.nsfw,
                    category=category)
                print_add(f"Yazı Kanalı Oluşturuldu: {channel_text.name}")
            except:
                try:
                    await guild_to.create_text_channel(
                        name=channel_text.name,
                        overwrites=overwrites_to,
                        position=channel_text.position,
                        category=category)
                    print_add(f"Yazı Kanalı Oluşturuldu: {channel_text.name}")
                except Exception as e:
                    print_error(f"Yazı Kanalı Hatası ({channel_text.name}): {e}")

        # Ses Kanalları
        for channel_voice in guild_from.voice_channels:
            category = None
            if channel_voice.category:
                for cat in guild_to.categories:
                    if cat.name == channel_voice.category.name:
                        category = cat
                        break

            overwrites_to = {}
            for key, value in channel_voice.overwrites.items():
                role = discord.utils.get(guild_to.roles, name=key.name)
                if role:
                    overwrites_to[role] = value
            try:
                new_channel = await guild_to.create_voice_channel(
                    name=channel_voice.name,
                    overwrites=overwrites_to,
                    position=channel_voice.position,
                    bitrate=channel_voice.bitrate,
                    user_limit=channel_voice.user_limit,
                    category=category)
                print_add(f"Ses Kanalı Oluşturuldu: {channel_voice.name}")
            except:
                try:
                    await guild_to.create_voice_channel(
                        name=channel_voice.name,
                        overwrites=overwrites_to,
                        position=channel_voice.position,
                        category=category)
                    print_add(f"Ses Kanalı Oluşturuldu: {channel_voice.name}")
                except Exception as e:
                    print_error(f"Ses Kanalı Hatası ({channel_voice.name}): {e}")

    @staticmethod
    async def emojis_create(guild_to: discord.Guild, guild_from: discord.Guild):
        for emoji in guild_from.emojis:
            try:
                emoji_image = await emoji.url.read()
                await guild_to.create_custom_emoji(
                    name=emoji.name,
                    image=emoji_image)
                print_add(f"Emoji Oluşturuldu: {emoji.name}")
            except Exception:
                print_error(f"Emoji Aktarılamadı: {emoji.name}")

    @staticmethod
    async def guild_edit(guild_to: discord.Guild, guild_from: discord.Guild):
        try:
            icon_image = await guild_from.icon_url.read() if guild_from.icon_url else None
            await guild_to.edit(name=f'{guild_from.name}')
            if icon_image:
                await guild_to.edit(icon=icon_image)
            print_add(f"Sunucu Adı ve İkonu Güncellendi: {guild_to.name}")
        except Exception:
            print_error(f"Sunucu Adı/İkonu Değiştirilirken Hata: {guild_to.name}")

# --- MODERN DISCORD ARAYÜZÜ (GUI) ---
class DiscordClonerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Discord Server Cloner")
        self.geometry("600x650")
        self.resizable(False, False)
        
        # Görev Çubuğu ve Pencere İkonu (Klasörde icon.ico varsa otomatik çeker)
        try:
            self.iconbitmap("icon.ico")
        except:
            pass
        
        # Orijinal Discord Renkleri
        self.configure(fg_color="#313338") 
        
        # Başlık
        self.title_label = ctk.CTkLabel(self, text="SERVER CLONER", font=("Segoe UI", 24, "bold"), text_color="#FFFFFF")
        self.title_label.pack(pady=(30, 20))

        # --- Girdiler İçin Çerçeve ---
        self.input_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.input_frame.pack(fill="x", padx=50)

        # Token
        self.token_label = ctk.CTkLabel(self.input_frame, text="HESAP TOKEN (YEDEK HESAP)", font=("Segoe UI", 11, "bold"), text_color="#B5BAC1")
        self.token_label.pack(anchor="w", pady=(5, 0))
        self.token_entry = ctk.CTkEntry(self.input_frame, width=500, height=40, corner_radius=8, show="*",
                                        fg_color="#1E1F22", border_color="#1E1F22", text_color="#DBDEE1")
        self.token_entry.pack(pady=(5, 15))

        # Kaynak Sunucu
        self.kaynak_label = ctk.CTkLabel(self.input_frame, text="KAYNAK SUNUCU ID", font=("Segoe UI", 11, "bold"), text_color="#B5BAC1")
        self.kaynak_label.pack(anchor="w")
        self.kaynak_entry = ctk.CTkEntry(self.input_frame, width=500, height=40, corner_radius=8,
                                         fg_color="#1E1F22", border_color="#1E1F22", text_color="#DBDEE1")
        self.kaynak_entry.pack(pady=(5, 15))

        # Hedef Sunucu
        self.hedef_label = ctk.CTkLabel(self.input_frame, text="HEDEF SUNUCU ID", font=("Segoe UI", 11, "bold"), text_color="#B5BAC1")
        self.hedef_label.pack(anchor="w")
        self.hedef_entry = ctk.CTkEntry(self.input_frame, width=500, height=40, corner_radius=8,
                                        fg_color="#1E1F22", border_color="#1E1F22", text_color="#DBDEE1")
        self.hedef_entry.pack(pady=(5, 15))

        # --- Başlat Butonu ---
        self.start_btn = ctk.CTkButton(self, text="Kopyalamayı Başlat", font=("Segoe UI", 14, "bold"), height=45, width=500,
                                       corner_radius=8, fg_color="#5865F2", hover_color="#4752C4", text_color="#FFFFFF",
                                       command=self.start_cloning_thread)
        self.start_btn.pack(pady=10)

        # --- Log Ekranı ---
        self.log_label = ctk.CTkLabel(self, text="İŞLEM KAYITLARI", font=("Segoe UI", 11, "bold"), text_color="#B5BAC1")
        self.log_label.pack(anchor="w", padx=50, pady=(10, 0))
        
        self.log_area = ctk.CTkTextbox(self, width=500, height=140, corner_radius=8,
                                       fg_color="#2B2D31", text_color="#DBDEE1", font=("Consolas", 12))
        self.log_area.pack(pady=(5, 20))

        sys.stdout = PrintRedirector(self.log_area)

    def start_cloning_thread(self):
        token = self.token_entry.get().strip()
        kaynak_id = self.kaynak_entry.get().strip()
        hedef_id = self.hedef_entry.get().strip()

        if not token or not kaynak_id or not hedef_id:
            messagebox.showwarning("Eksik Bilgi", "Lütfen Token, Kaynak ve Hedef ID alanlarının tamamını doldur.")
            return

        self.start_btn.configure(state="disabled", text="İşlem Sürüyor...")
        print("Sistem başlatılıyor, lütfen bekleyin...\n")
        
        threading.Thread(target=self.run_discord_bot, args=(token, kaynak_id, hedef_id), daemon=True).start()

    def run_discord_bot(self, token, kaynak_id, hedef_id):
        # Arka planda güvenli asyncio döngüsü
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        client = discord.Client()

        @client.event
        async def on_ready():
            print(f"Bağlantı Başarılı: {client.user}")
            try:
                guild_from = client.get_guild(int(kaynak_id))
                guild_to = client.get_guild(int(hedef_id))
                
                if not guild_from or not guild_to:
                    print("[HATA] Sunucular bulunamadı! ID'leri kontrol et.")
                    await client.close()
                    return

                print(f"Kaynak Sunucu: {guild_from.name}")
                print(f"Hedef Sunucu : {guild_to.name}")
                print("========================================")
                print("Hedef sunucu temizleniyor ve kopyalama başlıyor...\n")
                
                await Clone.guild_edit(guild_to, guild_from)
                await Clone.roles_delete(guild_to)
                await Clone.channels_delete(guild_to)
                
                await Clone.roles_create(guild_to, guild_from)
                await Clone.categories_create(guild_to, guild_from)
                await Clone.channels_create(guild_to, guild_from)
                await Clone.emojis_create(guild_to, guild_from)
                
                print("\n========================================")
                print("[+] İŞLEM BAŞARIYLA TAMAMLANDI!")
            except Exception as e:
                print(f"\n[HATA] Bir sorun oluştu: {e}")
            finally:
                await client.close()
                self.start_btn.configure(state="normal", text="Kopyalamayı Başlat")

        try:
            # BOT=FALSE KOMUTU KALDIRILDI! ARTIK HATA VERMEYECEK.
            client.run(token)
        except discord.errors.LoginFailure:
            print("[HATA] Token geçersiz! Doğru token girdiğinden emin ol.")
            self.start_btn.configure(state="normal", text="Kopyalamayı Başlat")
        except Exception as e:
            print(f"[HATA] Beklenmeyen bir ağ hatası: {e}")
            self.start_btn.configure(state="normal", text="Kopyalamayı Başlat")

if __name__ == "__main__":
    app = DiscordClonerApp()
    app.mainloop()