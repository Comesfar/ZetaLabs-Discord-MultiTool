# ⚡ ZetaLabs Discord Suite (v4.0 - Ghost Engine)

Modern, hızlı ve zengin özelliklere sahip açık kaynaklı Discord çoklu araç kiti (Multi-Tool). PyWebView ve modern web teknolojileri (HTML5/CSS3/JS) kullanılarak geliştirilmiş minimalist ve şık bir masaüstü arayüzüne sahiptir.

---

## 🌟 Öne Çıkan Özellikler

### 🔑 1. Token Doğrulayıcı (Tekli & Toplu Checker)
- **Bot & Self Token Desteği:** Bot veya kullanıcı (self) tokenlerini tek tek doğrulayabilme.
- **Çok İş Parçacıklı (Multi-Threaded) Toplu Checker:** Onlarca tokenı saniyeler içinde dondurmadan kontrol eder.
- **Detaylı Durum Ayrımı:** Geçerli, Geçersiz, Kilitli (Telefon/E-posta onayı bekleyen), Rate Limit durumlarını ayrı ayrı listeler.
- **Dosyadan İçe Aktarma:** `.txt` dosyasından doğrudan token listesi yükleme imkanı.
- **Güvenli Maskeleme:** Tokenlar arayüzde otomatik olarak gizlenir/maskelenir.

### 🖼️ 2. Asset İndirici (Avatar, İkon, Afiş, Splash)
- **Kullanıcı & Sunucu:** Hem kullanıcı profillerinin hem de sunucuların görsellerini çeker.
- **Format Algılama:** Hareketli (GIF) ve sabit (PNG) formatları otomatik tespit eder.
- **Açık Sunucu Önizleme Desteği:** Bot sunucuda olmasa bile keşfedilebilir topluluk sunucularının afiş ve ikonlarını çekebilir.
- **Tek Tıkla İndirme:** Yüksek çözünürlüklü (1024x1024) olarak doğrudan bilgisayara kaydetme.

### 📊 3. Derinlemesine Hesap & Profil Analizi
- **Token ile Profil:** Kullanıcı adı, ID, hesap oluşturulma tarihi (UTC), Nitro türü, 2FA durumu, rozetler, e-posta, telefon ve bağlı hesaplar.
- **ID ile Kullanıcı Sorgulama:** Herhangi bir kullanıcı ID'si girerek herkese açık profil verilerini çekme.

### 🛡️ 4. Sunucu Bilgi Analizörü
- Sunucu sahibi, kuruluş tarihi, üye/çevrimiçi sayısı, Boost seviyesi ve sayısı, güvenlik seviyesi, rol ve emoji sayıları.

### 😀 5. Toplu Emoji İndirici
- Belirtilen sunucudaki tüm özel ve animasyonlu (GIF) emojileri listeler.
- Tek bir tıkla hedef klasöre hepsini otomatik ve temiz isimlendirmeyle indirir.

### 🔄 6. Sunucu Kopyalama (Server Cloner)
- Sunucu adı, ikonu, temel ayarları, rolleri (hiyerarşi ve izinleriyle), kategorileri, metin/ses kanallarını ve emojilerini hedef sunucuya aktarır.
- Canlı ilerleme çubuğu ve tahmini süre (ETA) göstergesi.

### 🔗 7. Vanity URL & Davet Çözümleyici
- Özel sunucu URL'lerinin (`/ornek`) boşta olup olmadığını anında kontrol eder.
- Davet bağlantılarını çözümleyerek sunucu detaylarını, üye sayısını ve davet eden kişiyi gösterir.

### ❄️ 8. Snowflake & Token Decoder
- Discord ID'lerinden oluşturulma zamanını, worker ve process kimliklerini çözer.
- Token formatından kullanıcı ID'si ve hesap oluşturulma tarihini ayıklar.

### 🪝 9. Webhook Yöneticisi
- Discord webhooklarına özel kullanıcı adı, profil fotoğrafı ve renkli Embed mesajları gönderme.

### 📝 10. İşlem Geçmişi (History) & Ayarlar
- Yapılan tüm işlemleri zaman damgasıyla yerel olarak kaydeder ve geçmiş sekmesinde görüntüler.
- Varsayılan bot ve self tokenlarınızı sadece kendi bilgisayarınızda (`settings.json`) saklar.

---

## 🚀 Kurulum ve Çalıştırma

### Gereksinimler
- Python 3.10 veya üzeri
- Windows 10 / 11

### Hızlı Başlatma (Windows)
Klasör içindeki **`start.bat`** dosyasına çift tıklayarak eksik kütüphaneleri otomatik yükleyip arayüzü başlatabilirsiniz.

### Manuel Başlatma (Terminal)
```bash
# 1. Gerekli kütüphaneleri yükleyin
pip install -r requirements.txt

# 2. Uygulamayı çalıştırın
python main.pyw
```

---

## 📁 Proje Dizin Yapısı

```
MultiChecker/
├── modules/                   # Modüler backend bileşenleri
│   ├── asset_downloader.py    # Görsel ve afiş motoru
│   ├── bulk_checker.py        # Çok iş parçacıklı toplu kontrolcü
│   ├── emoji_downloader.py    # Sunucu emoji indirici
│   ├── guild_info.py          # Sunucu analizörü
│   ├── invite_resolver.py     # Davet bağlantısı çözümleyici
│   ├── server_cloner.py       # Sunucu kopyalama motoru
│   ├── snowflake_decoder.py   # Discord Snowflake dönüştürücü
│   ├── token_decoder.py       # Token ayrıştırıcı
│   ├── token_validator.py     # Tekli token doğrulayıcı
│   ├── user_detail.py         # Kullanıcı analizörü
│   ├── vanity_url.py          # URL boşta/dolu denetleyicisi
│   └── webhook_manager.py     # Webhook bildirim aracı
├── web/                       # PyWebView Frontend
│   ├── index.html             # Arayüz iskeleti
│   ├── script.js              # Etkileşim ve API köprüsü
│   └── style.css              # Glassmorphism karanlık tema
├── main.pyw                   # Ana uygulama başlatıcı
├── settings.example.json      # Örnek ayar şablonu
├── requirements.txt           # Python bağımlılıkları
├── start.bat                  # Hızlı başlatıcı script
├── .gitignore                 # Güvenlik ve çöp dosya filtresi
└── README.md                  # Dokümantasyon
```

---

## 🔒 Güvenlik & Gizlilik Notu

- Bu proje tamamen açık kaynaklıdır ve **asla** üçüncü taraf bir sunucuya veri aktarmaz.
- Tokenlarınız yalnızca yerel diskinizdeki `settings.json` dosyasında tutulur ve `.gitignore` ile korunmaktadır.
- Projeyi paylaşırken veya git reposuna yüklerken `settings.json` dosyanızda token bırakmadığınızdan emin olun.

---

## ⚖️ Yasal Uyarı (Disclaimer)

Bu araç yalnızca eğitim, güvenlik araştırmaları ve kendi Discord kaynaklarınızı yönetme amacıyla geliştirilmiştir. Discord Hizmet Şartları'nı (ToS) ihlal edebilecek eylemlerden kullanıcının kendisi sorumludur.

---

## 📄 Lisans
Bu proje [MIT Lisansı](LICENSE) altında paylaşılmıştır.
