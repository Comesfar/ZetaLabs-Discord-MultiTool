// Global token durumu
let hasTokens = false;

window.addEventListener('pywebviewready', async function() {
    let settings = await window.pywebview.api.get_settings();
    let botToken = settings.bot_token || "";
    let selfToken = settings.self_token || "";
    
    document.getElementById("setBotToken").value = botToken;
    document.getElementById("setSelfToken").value = selfToken;
    
    // Kurulum ekrani kontrolu
    if (!botToken && !selfToken) {
        document.getElementById("splashLoading").style.display = "none";
        document.getElementById("setupForm").style.display = "block";
    } else {
        hasTokens = true;
        setTimeout(() => {
            let splash = document.getElementById("splashScreen");
            splash.style.opacity = "0";
            setTimeout(() => splash.style.display = "none", 500);
        }, 1500); // 1.5 sn logo animasyonu izlet
    }
});

// XSS koruması — kullanıcı verisini HTML'e güvenli şekilde ekler
function escapeHtml(str) {
    if (str === null || str === undefined) return '';
    const div = document.createElement('div');
    div.textContent = String(str);
    return div.innerHTML;
}

function switchTab(tabId, btnElement) {
    document.querySelectorAll('.glass-panel').forEach(tab => tab.classList.remove('active'));
    document.querySelectorAll('.nav-btn').forEach(btn => btn.classList.remove('active'));
    document.getElementById(tabId).classList.add('active');
    btnElement.classList.add('active');

    // Geçmiş tabına geçince otomatik yükle
    if (tabId === 'historyTab') loadHistory();
}

// =============================================
//  AYARLAR MODÜLÜ
// =============================================
async function saveSettings() {
    let botToken = document.getElementById("setBotToken").value.trim();
    let selfToken = document.getElementById("setSelfToken").value.trim();
    let resBox = document.getElementById("settingsResult");

    resBox.className = "result-box glow-idle mt-20";
    resBox.innerHTML = "Kaydediliyor...";

    try {
        let response = await window.pywebview.api.save_settings(botToken, selfToken);
        if (response.status === "success") {
            resBox.className = "result-box glow-success mt-20";
            hasTokens = true;
        } else {
            resBox.className = "result-box glow-error mt-20";
        }
        resBox.innerHTML = escapeHtml(response.msg);
    } catch (e) {
        resBox.className = "result-box glow-error mt-20";
        resBox.innerHTML = "❌ Kaydetme sırasında bir hata oluştu: " + escapeHtml(e);
    }
}

async function completeSetup() {
    let botToken = document.getElementById("setupBotToken").value.trim();
    let selfToken = document.getElementById("setupSelfToken").value.trim();
    
    document.getElementById("setBotToken").value = botToken;
    document.getElementById("setSelfToken").value = selfToken;
    
    await window.pywebview.api.save_settings(botToken, selfToken);
    
    hasTokens = true;
    let splash = document.getElementById("splashScreen");
    splash.style.opacity = "0";
    setTimeout(() => splash.style.display = "none", 500);
}

// Global olarak hangi tokenin kullanılacağını seçen yardımcı fonksiyon
async function getActiveToken(manualToken, tokenType) {
    if (manualToken !== "") return manualToken;
    let settings = await window.pywebview.api.get_settings();
    return tokenType === "bot" ? settings.bot_token : settings.self_token;
}

// =============================================
//  MODÜL 1: TOKEN VALIDATOR (Tekli)
// =============================================
async function runTokenCheck() {
    let type = document.getElementById("tokenType").value;
    let tokenToUse = document.getElementById("tokenTargetInput").value.trim();
    let resBox = document.getElementById("valResult");

    if (!tokenToUse) {
        resBox.className = "result-box glow-error";
        resBox.innerHTML = "Lütfen sorgulanacak tokeni giriniz!";
        return;
    }
    
    resBox.className = "result-box glow-idle";
    resBox.innerHTML = "Sorgulanıyor...";
    
    try {
        let response = await window.pywebview.api.check_token(tokenToUse, type);
        resBox.className = response.status === "success" ? "result-box glow-success" : "result-box glow-error";
        resBox.innerHTML = response.msg;
    } catch (e) {
        resBox.className = "result-box glow-error";
        resBox.innerHTML = "Bağlantı kurulamadı.";
    }
}

// =============================================
//  MODÜL 2: TOPLU TOKEN CHECKER
// =============================================
async function runBulkCheck() {
    let tokenType = document.getElementById("bulkTokenType").value;
    let tokensText = document.getElementById("bulkTokensInput").value.trim();
    let statusText = document.getElementById("bulkStatusText");
    let resBox = document.getElementById("bulkResult");
    let resultsList = document.getElementById("bulkResultsList");
    let progressBar = document.getElementById("bulkProgressBar");

    if (!tokensText) {
        resBox.className = "result-box glow-error";
        statusText.innerHTML = "Lütfen en az bir token girin!";
        resultsList.style.display = "none";
        progressBar.style.display = "none";
        return;
    }

    resBox.className = "result-box glow-idle";
    statusText.innerHTML = "⏳ Kontrol ediliyor... Bu işlem biraz sürebilir.";
    resultsList.style.display = "none";
    progressBar.style.display = "flex";
    document.getElementById("bulkProgressFill").style.width = "30%";
    document.getElementById("bulkProgressText").textContent = "Çalışıyor...";

    try {
        let response = await window.pywebview.api.bulk_check_tokens(tokensText, tokenType);
        
        progressBar.style.display = "none";

        if (response.status === "error") {
            resBox.className = "result-box glow-error";
            statusText.innerHTML = response.msg;
            return;
        }

        resBox.className = "result-box glow-success";
        statusText.innerHTML = `✅ Toplam: ${escapeHtml(response.total)} | ✅ Geçerli: ${escapeHtml(response.valid)} | ❌ Geçersiz: ${escapeHtml(response.invalid)}`;
        
        // Sonuç listesini oluştur
        resultsList.style.display = "block";
        resultsList.innerHTML = response.results.map((r, i) => {
            let statusClass = r.status === "valid" ? "bulk-valid" : "bulk-invalid";
            let statusIcon = r.status === "valid" ? "✅" : "❌";
            return `<div class="bulk-result-item ${statusClass}">
                <span class="bulk-index">#${i + 1}</span>
                <span class="bulk-token">${escapeHtml(r.token)}</span>
                <span class="bulk-name">${escapeHtml(r.name)}</span>
                <span class="bulk-status-icon">${statusIcon}</span>
            </div>`;
        }).join('');
    } catch (e) {
        progressBar.style.display = "none";
        resBox.className = "result-box glow-error";
        statusText.innerHTML = "Bağlantı kurulamadı.";
    }
}

async function loadTokensFile() {
    try {
        let result = await window.pywebview.api.load_tokens_file();
        if (result.status === "success") {
            document.getElementById("bulkTokensInput").value = result.content;
        }
    } catch (e) {
        console.error("Dosya yükleme hatası:", e);
    }
}

// =============================================
//  MODÜL 3: ASSET İNDİRİCİ
// =============================================
let currentAssetUrls = { avatar: null, banner: null, name: "" };

async function runAssetFetch() {
    let tokenType = document.getElementById("assetTokenType").value;
    let targetType = document.getElementById("assetTargetType").value;
    let targetId = document.getElementById("assetIdInput").value.trim();
    
    let statusText = document.getElementById("assetStatusText");
    let imgContainer = document.getElementById("imageContainer");
    let resBox = statusText.parentElement;

    let manualToken = document.getElementById("assetTokenInput") ? document.getElementById("assetTokenInput").value.trim() : "";
    let tokenToUse = await getActiveToken(manualToken, tokenType);
    
    if (!tokenToUse || !targetId) {
        imgContainer.style.display = "none";
        resBox.className = "result-box glow-error mt-20";
        statusText.innerHTML = "Lütfen ID giriniz ve geçerli bir token sağlandığından emin olunuz!";
        return;
    }

    resBox.className = "result-box glow-idle mt-20";
    statusText.innerHTML = "API ile haberleşiliyor...";
    imgContainer.style.display = "none";

    try {
        let response = await window.pywebview.api.fetch_assets(tokenToUse, tokenType, targetId, targetType);

        if (response.status === "error") {
            resBox.className = "result-box glow-error mt-20";
            statusText.innerHTML = response.msg;
            return;
        }

        currentAssetUrls.avatar = response.avatar;
        currentAssetUrls.banner = response.banner;
        currentAssetUrls.name = response.name || "asset";

        resBox.className = "result-box glow-success mt-20";
        statusText.innerHTML = `✅ Bulundu: ${escapeHtml(response.name)}`;
        imgContainer.style.display = "flex";

        setupImage("imgAvatar", "linkAvatar", "btnDownloadAvatar", response.avatar);
        setupImage("imgBanner", "linkBanner", "btnDownloadBanner", response.banner);
    } catch (e) {
        resBox.className = "result-box glow-error mt-20";
        statusText.innerHTML = "Bağlantı kurulamadı.";
    }
}

function setupImage(imgId, linkId, btnId, url) {
    let imgEl = document.getElementById(imgId);
    let linkEl = document.getElementById(linkId);
    let btnEl = document.getElementById(btnId);
    if (url) {
        imgEl.src = url;
        imgEl.style.display = "block";
        linkEl.href = url;
        linkEl.style.display = "inline-block";
        btnEl.style.display = "inline-block";
    } else {
        imgEl.style.display = "none";
        linkEl.style.display = "none";
        btnEl.style.display = "none";
    }
}

async function downloadAsset(type) {
    let url = type === "avatar" ? currentAssetUrls.avatar : currentAssetUrls.banner;
    if (!url) return;

    let ext = url.includes(".gif") ? "gif" : "png";
    let defaultName = `${currentAssetUrls.name}_${type}.${ext}`;

    try {
        let result = await window.pywebview.api.download_asset(url, defaultName);
        if (result.status === "success") {
            let statusText = document.getElementById("assetStatusText");
            statusText.innerHTML += `<br>${result.msg}`;
        }
    } catch (e) {
        console.error("İndirme hatası:", e);
    }
}

// =============================================
//  MODÜL 4: KULLANICI DETAY PANELİ
// =============================================
function toggleUserDetailInputs() {
    let queryType = document.getElementById("userDetailQueryType").value;
    let tokenGroup = document.getElementById("userDetailTokenGroup");
    let label = document.getElementById("userDetailInputLabel");
    let input = document.getElementById("userDetailTokenInput");
    
    if (queryType === "token") {
        tokenGroup.style.display = "block";
        label.innerText = "Sorgulanacak Token *";
        input.placeholder = "Token giriniz...";
    } else {
        tokenGroup.style.display = "none";
        label.innerText = "Kullanıcı ID *";
        input.placeholder = "Örn: 1234567890...";
    }
}

async function runUserDetail() {
    let queryType = document.getElementById("userDetailQueryType").value;
    let type = document.getElementById("userDetailType").value;
    let targetInput = document.getElementById("userDetailTokenInput").value.trim();
    let statusText = document.getElementById("userDetailStatus");
    let card = document.getElementById("userDetailCard");
    let resBox = document.getElementById("userDetailResult");

    if (!targetInput) {
        resBox.className = "result-box glow-error mt-20";
        statusText.innerHTML = queryType === "token" ? "Lütfen sorgulanacak tokeni giriniz!" : "Lütfen kullanıcı ID giriniz!";
        card.style.display = "none";
        return;
    }

    resBox.className = "result-box glow-idle mt-20";
    statusText.innerHTML = "Bilgiler çekiliyor...";
    card.style.display = "none";

    try {
        let r;
        if (queryType === "token") {
            r = await window.pywebview.api.get_user_details(targetInput, type);
        } else {
            let settings = await window.pywebview.api.get_settings();
            let authToken = settings.bot_token || settings.self_token;
            let authType = settings.bot_token ? "bot" : "user";
            
            if (!authToken) {
                resBox.className = "result-box glow-error mt-20";
                statusText.innerHTML = "Lütfen Ayarlar sekmesine bir aracı token ekleyin!";
                return;
            }
            r = await window.pywebview.api.get_user_by_id(targetInput, authToken, authType);
        }

        if (r.status === "error") {
            resBox.className = "result-box glow-error mt-20";
            statusText.innerHTML = r.msg;
            return;
        }

        resBox.className = "result-box glow-success mt-20";
        statusText.innerHTML = `✅ ${escapeHtml(r.display_name)} bilgileri başarıyla çekildi`;
        card.style.display = "block";

        // Banner
        let bannerArea = document.getElementById("userBannerArea");
        if (r.banner_url) {
            bannerArea.style.backgroundImage = `url(${r.banner_url})`;
            bannerArea.style.display = "block";
        } else if (r.banner_color) {
            bannerArea.style.background = `#${r.banner_color.toString(16).padStart(6, '0')}`;
            bannerArea.style.display = "block";
        } else {
            bannerArea.style.display = "none";
        }

        // Avatar
        let avatarEl = document.getElementById("userDetailAvatar");
        if (r.avatar_url) {
            avatarEl.src = r.avatar_url;
            avatarEl.style.display = "block";
        } else {
            avatarEl.style.display = "none";
        }

        document.getElementById("userDetailName").textContent = r.display_name;
        document.getElementById("userDetailTag").textContent = `${r.username}#${r.discriminator}`;
        document.getElementById("userDetailId").textContent = r.id;
        document.getElementById("userDetailCreated").textContent = r.created_date;
        
        // Sadece token ile çekilebilenler:
        document.getElementById("userDetailNitro").textContent = r.nitro || "—";
        document.getElementById("userDetailMfa").textContent = r.mfa_enabled !== undefined ? (r.mfa_enabled ? "✅ Aktif" : "❌ Kapalı") : "—";
        document.getElementById("userDetailLocale").textContent = r.locale || "—";
        document.getElementById("userDetailEmail").textContent = r.email || "—";
        document.getElementById("userDetailPhone").textContent = r.phone || "—";
        document.getElementById("userDetailGuilds").textContent = r.guild_count !== undefined ? r.guild_count : "—";
        document.getElementById("userDetailVerified").textContent = r.verified !== undefined ? (r.verified ? "✅ Evet" : "❌ Hayır") : "—";
        document.getElementById("userDetailFriends").textContent = r.friends_count !== undefined ? r.friends_count : "—";
        document.getElementById("userDetailBlocked").textContent = r.blocked_count !== undefined ? r.blocked_count : "—";

        // Badges
        let badgesEl = document.getElementById("userBadges");
        if (r.badges && r.badges.length > 0) {
            badgesEl.innerHTML = r.badges.map(b => `<span class="badge-tag">${b}</span>`).join('');
            badgesEl.style.display = "flex";
        } else {
            badgesEl.innerHTML = "";
            badgesEl.style.display = "none";
        }
        
        // Connections
        let connTitle = document.getElementById("userConnectionsTitle");
        let connEl = document.getElementById("userConnections");
        if (r.connections && r.connections.length > 0) {
            connEl.innerHTML = r.connections.map(c => `<span class="badge-tag">${escapeHtml(c.type.toUpperCase())}: ${escapeHtml(c.name)}</span>`).join('');
            connTitle.style.display = "block";
        } else {
            connEl.innerHTML = "";
            connTitle.style.display = "none";
        }
        
    } catch (e) {
        resBox.className = "result-box glow-error mt-20";
        statusText.innerHTML = "Bağlantı kurulamadı.";
    }
}

// =============================================
//  MODÜL 5: SUNUCU BİLGİ ÇEKİCİ
// =============================================
async function runGuildInfo() {
    let tokenType = document.getElementById("guildTokenType").value;
    let guildId = document.getElementById("guildIdInput").value.trim();
    let statusText = document.getElementById("guildStatusText");
    let card = document.getElementById("guildDetailCard");
    let resBox = document.getElementById("guildResult");

    let tokenToUse = await getActiveToken("", tokenType);

    if (!tokenToUse || !guildId) {
        resBox.className = "result-box glow-error mt-20";
        statusText.innerHTML = "Lütfen Sunucu ID ve geçerli bir token (Ayarlar'da) giriniz!";
        card.style.display = "none";
        return;
    }

    resBox.className = "result-box glow-idle mt-20";
    statusText.innerHTML = "Sunucu bilgileri çekiliyor...";
    card.style.display = "none";

    try {
        let r = await window.pywebview.api.get_guild_info(tokenToUse, tokenType, guildId);

        if (r.status === "error") {
            resBox.className = "result-box glow-error mt-20";
            statusText.innerHTML = r.msg;
            return;
        }

        resBox.className = "result-box glow-success mt-20";
        statusText.innerHTML = `✅ ${escapeHtml(r.name)} bilgileri başarıyla çekildi`;
        card.style.display = "block";

        // Banner
        let bannerArea = document.getElementById("guildBannerArea");
        if (r.banner_url) {
            bannerArea.style.backgroundImage = `url(${r.banner_url})`;
            bannerArea.style.display = "block";
        } else {
            bannerArea.style.display = "none";
        }

        // İkon
        let iconEl = document.getElementById("guildDetailIcon");
        if (r.icon_url) {
            iconEl.src = r.icon_url;
            iconEl.style.display = "block";
        } else {
            iconEl.style.display = "none";
        }

        document.getElementById("guildDetailName").textContent = r.name;
        document.getElementById("guildDetailDesc").textContent = r.description;
        document.getElementById("guildDetailId").textContent = r.id;
        document.getElementById("guildDetailCreated").textContent = r.created_date;
        document.getElementById("guildDetailMembers").textContent = r.member_count;
        document.getElementById("guildDetailOnline").textContent = r.online_count;
        document.getElementById("guildDetailBoostLevel").textContent = r.boost_level;
        document.getElementById("guildDetailBoosts").textContent = r.boost_count;
        document.getElementById("guildDetailVerification").textContent = r.verification;
        document.getElementById("guildDetailOwner").textContent = r.owner_id;
        document.getElementById("guildDetailRoles").textContent = r.role_count;
        document.getElementById("guildDetailEmojis").textContent = r.emoji_count;
        document.getElementById("guildDetailVanity").textContent = r.vanity_url;
    } catch (e) {
        resBox.className = "result-box glow-error mt-20";
        statusText.innerHTML = "Bağlantı kurulamadı.";
    }
}

// =============================================
//  MODÜL 6: VANITY URL SORGULAMA
// =============================================
async function runVanityCheck() {
    let vanityCode = document.getElementById("vanityInput").value.trim();
    let statusText = document.getElementById("vanityStatusText");
    let guildInfo = document.getElementById("vanityGuildInfo");
    let resBox = document.getElementById("vanityResult");

    // "discord.gg/vanity" girildiyse bile sadece vanity kismini al
    if (vanityCode.includes("/")) {
        vanityCode = vanityCode.split("/").pop();
    }

    if (!vanityCode) {
        resBox.className = "result-box glow-error mt-20";
        statusText.innerHTML = "Lütfen bir URL kodu giriniz!";
        guildInfo.style.display = "none";
        return;
    }

    resBox.className = "result-box glow-idle mt-20";
    statusText.innerHTML = "Sorgulanıyor...";
    guildInfo.style.display = "none";

    try {
        // Rate limit'i az yansıtmak için ayarlardaki bot tokenini (varsa) kullanalim
        let tokenToUse = await getActiveToken("", "bot") || await getActiveToken("", "user");
        let tokenType = tokenToUse === (await getActiveToken("", "bot")) ? "bot" : "user";
        
        let r = await window.pywebview.api.check_vanity_url(tokenToUse || "", tokenType, vanityCode);

        if (r.status === "error") {
            resBox.className = "result-box glow-error mt-20";
            statusText.innerHTML = escapeHtml(r.msg);
            return;
        } else if (r.status === "taken") {
            resBox.className = "result-box glow-error mt-20";
            statusText.innerHTML = escapeHtml(r.msg);
            guildInfo.innerHTML = `Sunucu: <strong>${escapeHtml(r.guild_name)}</strong> &nbsp;|&nbsp; Üye: <strong>${escapeHtml(r.member_count)}</strong>`;
            guildInfo.style.display = "block";
        } else if (r.status === "available") {
            resBox.className = "result-box glow-success mt-20";
            statusText.innerHTML = escapeHtml(r.msg);
        }
    } catch (e) {
        resBox.className = "result-box glow-error mt-20";
        statusText.innerHTML = "Bağlantı kurulamadı.";
    }
}

// =============================================
//  MODÜL 7: İŞLEM GEÇMİŞİ
// =============================================
async function loadHistory() {
    let listEl = document.getElementById("historyList");
    let resBox = document.getElementById("historyResult");
    
    try {
        let logs = await window.pywebview.api.get_logs();

        if (!logs || logs.length === 0) {
            resBox.className = "result-box glow-idle mt-20";
            listEl.innerHTML = '<div class="history-empty">Henüz hiç işlem kaydı yok.</div>';
            return;
        }

        resBox.className = "result-box glow-idle mt-20";
        listEl.innerHTML = logs.map(log => {
            let statusClass = log.status === "success" ? "history-success" : "history-error";
            let statusIcon = log.status === "success" ? "✅" : "❌";
            return `<div class="history-item ${statusClass}">
                <div class="history-icon">${statusIcon}</div>
                <div class="history-content">
                    <div class="history-action">${escapeHtml(log.action)}</div>
                    <div class="history-detail">${escapeHtml(log.detail)}</div>
                </div>
                <div class="history-time">${escapeHtml(log.time)}</div>
            </div>`;
        }).join('');
    } catch (e) {
        listEl.innerHTML = "Geçmiş yüklenemedi.";
    }
}

async function clearHistory() {
    try {
        let result = await window.pywebview.api.clear_logs();
        let resBox = document.getElementById("historyResult");
        resBox.className = "result-box glow-success mt-20";
        document.getElementById("historyList").innerHTML = '<div class="history-empty">Geçmiş temizlendi.</div>';
    } catch (e) {
        console.error("Geçmiş temizleme hatası:", e);
    }
}

// =============================================
//  MODÜL 8: WEBHOOK YÖNETİCİSİ
// =============================================
async function runWebhookSend() {
    let url = document.getElementById("webhookUrl").value.trim();
    let username = document.getElementById("webhookUsername").value.trim();
    let avatar = document.getElementById("webhookAvatar").value.trim();
    let content = document.getElementById("webhookContent").value.trim();
    let embedTitle = document.getElementById("webhookEmbedTitle").value.trim();
    let embedColor = document.getElementById("webhookEmbedColor").value.trim();
    let embedDesc = document.getElementById("webhookEmbedDesc").value.trim();
    
    let resBox = document.getElementById("webhookResult");

    if (!url) {
        resBox.className = "result-box glow-error mt-20";
        resBox.innerHTML = "Webhook URL boş olamaz!";
        return;
    }

    resBox.className = "result-box glow-idle mt-20";
    resBox.innerHTML = "Gönderiliyor...";

    try {
        let r = await window.pywebview.api.send_webhook(url, content, username, avatar, embedTitle, embedDesc, embedColor);
        if (r.status === "error") {
            resBox.className = "result-box glow-error mt-20";
        } else {
            resBox.className = "result-box glow-success mt-20";
        }
        resBox.innerHTML = escapeHtml(r.msg);
    } catch (e) {
        resBox.className = "result-box glow-error mt-20";
        resBox.innerHTML = "Bağlantı kurulamadı.";
    }
}

// =============================================
//  MODÜL 9: DAVET ÇÖZÜMLEYİCİ
// =============================================
async function runInviteResolve() {
    let invite = document.getElementById("inviteInput").value.trim();
    let statusText = document.getElementById("inviteStatusText");
    let card = document.getElementById("inviteDetailCard");
    let resBox = document.getElementById("inviteResult");

    if (!invite) {
        resBox.className = "result-box glow-error mt-20";
        statusText.innerHTML = "Lütfen bir davet kodu veya URL giriniz!";
        card.style.display = "none";
        return;
    }

    resBox.className = "result-box glow-idle mt-20";
    statusText.innerHTML = "Çözümleniyor...";
    card.style.display = "none";

    try {
        let r = await window.pywebview.api.resolve_invite(invite);
        if (r.status === "error") {
            resBox.className = "result-box glow-error mt-20";
            statusText.innerHTML = escapeHtml(r.msg);
            return;
        }

        resBox.className = "result-box glow-success mt-20";
        statusText.innerHTML = `✅ ${escapeHtml(r.guild_name)} sunucusu bilgileri alındı`;
        card.style.display = "block";

        let iconEl = document.getElementById("inviteDetailIcon");
        if (r.icon_url) {
            iconEl.src = r.icon_url;
            iconEl.style.display = "block";
        } else {
            iconEl.style.display = "none";
        }

        document.getElementById("inviteDetailName").textContent = r.guild_name;
        document.getElementById("inviteDetailCode").textContent = `/${r.code}`;
        document.getElementById("inviteDetailId").textContent = r.guild_id;
        document.getElementById("inviteDetailInviter").textContent = r.inviter;
        document.getElementById("inviteDetailMembers").textContent = r.member_count;
        document.getElementById("inviteDetailOnline").textContent = r.online_count;
        document.getElementById("inviteDetailExpires").textContent = r.expires_at;
    } catch (e) {
        resBox.className = "result-box glow-error mt-20";
        statusText.innerHTML = "Bağlantı kurulamadı.";
    }
}

// =============================================
//  MODÜL 10: SNOWFLAKE DECODER
// =============================================
async function runSnowflakeDecode() {
    let sfId = document.getElementById("snowflakeInput").value.trim();
    let statusText = document.getElementById("snowflakeStatusText");
    let details = document.getElementById("snowflakeDetails");
    let resBox = document.getElementById("snowflakeResult");

    if (!sfId) {
        resBox.className = "result-box glow-error mt-20";
        statusText.innerHTML = "Lütfen bir ID giriniz!";
        details.style.display = "none";
        return;
    }

    resBox.className = "result-box glow-idle mt-20";
    statusText.innerHTML = "Çözümleniyor...";
    details.style.display = "none";

    try {
        let r = await window.pywebview.api.decode_snowflake(sfId);
        if (r.status === "error") {
            resBox.className = "result-box glow-error mt-20";
            statusText.innerHTML = escapeHtml(r.msg);
            return;
        }

        resBox.className = "result-box glow-success mt-20";
        statusText.innerHTML = `✅ ID Başarıyla Çözümlendi`;
        details.style.display = "block";

        document.getElementById("sfDate").textContent = r.date_utc;
        document.getElementById("sfTimestamp").textContent = r.timestamp;
        document.getElementById("sfWorker").textContent = r.internal_worker;
        document.getElementById("sfProcess").textContent = r.internal_process;
        document.getElementById("sfIncrement").textContent = r.increment;
    } catch (e) {
        resBox.className = "result-box glow-error mt-20";
        statusText.innerHTML = "Hata oluştu.";
    }
}

// =============================================
//  MODÜL 11: TOKEN DECODER
// =============================================
async function runTokenDecode() {
    let token = document.getElementById("tokenDecInput").value.trim();
    let statusText = document.getElementById("tokenDecStatusText");
    let details = document.getElementById("tokenDecDetails");
    let resBox = document.getElementById("tokenDecResult");

    if (!token) {
        resBox.className = "result-box glow-error mt-20";
        statusText.innerHTML = "Lütfen bir Token giriniz!";
        details.style.display = "none";
        return;
    }

    resBox.className = "result-box glow-idle mt-20";
    statusText.innerHTML = "Çözümleniyor...";
    details.style.display = "none";

    try {
        let r = await window.pywebview.api.decode_token(token);
        if (r.status === "error") {
            resBox.className = "result-box glow-error mt-20";
            statusText.innerHTML = escapeHtml(r.msg);
            return;
        }

        resBox.className = "result-box glow-success mt-20";
        statusText.innerHTML = `✅ Token Başarıyla Çözümlendi`;
        details.style.display = "block";

        document.getElementById("tdUserId").textContent = r.user_id;
        document.getElementById("tdCreated").textContent = r.creation_time;
        document.getElementById("tdPart1").textContent = r.raw_part1;
        document.getElementById("tdPart2").textContent = r.raw_part2;
    } catch (e) {
        resBox.className = "result-box glow-error mt-20";
        statusText.innerHTML = "Hata oluştu.";
    }
}

// =============================================
//  MODÜL 12: EMOJİ İNDİRİCİ
// =============================================
let currentEmojiList = [];

async function runEmojiFetch() {
    let tokenType = document.getElementById("emojiTokenType").value;
    let guildId = document.getElementById("emojiGuildId").value.trim();
    let statusText = document.getElementById("emojiStatusText");
    let container = document.getElementById("emojiListContainer");
    let resBox = document.getElementById("emojiResult");
    let btnDownloadBulk = document.getElementById("btnEmojiDownloadBulk");

    let tokenToUse = await getActiveToken("", tokenType);

    if (!tokenToUse || !guildId) {
        resBox.className = "result-box glow-error mt-20";
        statusText.innerHTML = "Lütfen Sunucu ID ve Token giriniz!";
        container.style.display = "none";
        btnDownloadBulk.style.display = "none";
        return;
    }

    resBox.className = "result-box glow-idle mt-20";
    statusText.innerHTML = "Emojiler aranıyor...";
    container.style.display = "none";
    btnDownloadBulk.style.display = "none";

    try {
        let r = await window.pywebview.api.fetch_guild_emojis(tokenToUse, tokenType, guildId);
        if (r.status === "error") {
            resBox.className = "result-box glow-error mt-20";
            statusText.innerHTML = escapeHtml(r.msg);
            return;
        }

        currentEmojiList = r.emojis;
        resBox.className = "result-box glow-success mt-20";
        statusText.innerHTML = `✅ ${r.count} emoji bulundu.`;
        
        container.innerHTML = currentEmojiList.map(e => {
            return `<img src="${escapeHtml(e.url)}" title="${escapeHtml(e.name)}" style="width:32px; height:32px; border-radius:4px; object-fit:contain; background:rgba(0,0,0,0.3); padding:2px;">`;
        }).join('');
        container.style.display = "flex";
        btnDownloadBulk.style.display = "inline-block";
    } catch (e) {
        resBox.className = "result-box glow-error mt-20";
        statusText.innerHTML = "Bağlantı kurulamadı.";
    }
}

async function runEmojiDownloadBulk() {
    let statusText = document.getElementById("emojiStatusText");
    let resBox = document.getElementById("emojiResult");

    if (currentEmojiList.length === 0) return;

    statusText.innerHTML = "İndirme işlemi için klasör seçin ve bekleyin...";
    resBox.className = "result-box glow-idle mt-20";

    try {
        let r = await window.pywebview.api.download_emojis_bulk(currentEmojiList);
        if (r.status === "error") {
            resBox.className = "result-box glow-error mt-20";
            statusText.innerHTML = escapeHtml(r.msg);
        } else if (r.status === "cancelled") {
            resBox.className = "result-box glow-idle mt-20";
            statusText.innerHTML = escapeHtml(r.msg);
        } else {
            resBox.className = "result-box glow-success mt-20";
            statusText.innerHTML = escapeHtml(r.msg) + `<br><small style="color:#a1a1aa;">Klasör: ${escapeHtml(r.folder)}</small>`;
        }
    } catch (e) {
        resBox.className = "result-box glow-error mt-20";
        statusText.innerHTML = "İndirme hatası.";
    }
}

// =============================================
//  MODÜL 13: SERVER CLONER
// =============================================
async function runServerCloner() {
    let token = document.getElementById("clonerTokenInput").value.trim();
    let sourceId = document.getElementById("clonerSourceId").value.trim();
    let targetId = document.getElementById("clonerTargetId").value.trim();
    
    let tokenToUse = await getActiveToken(token, "user"); // Sadece user token
    if (!tokenToUse || !sourceId || !targetId) {
        document.getElementById("clonerResult").className = "result-box glow-error mt-20";
        document.getElementById("clonerStatusText").innerHTML = "Lütfen Self Token, Kaynak ve Hedef ID alanlarını doldurun.";
        return;
    }

    document.getElementById("btnStartCloner").disabled = true;
    document.getElementById("btnStartCloner").innerHTML = "Kopyalanıyor...";
    document.getElementById("clonerResult").className = "result-box glow-idle mt-20";
    document.getElementById("clonerStatusText").innerHTML = "Başlatılıyor...";
    document.getElementById("clonerProgressArea").style.display = "block";
    document.getElementById("clonerProgressFill").style.width = "0%";
    document.getElementById("clonerProgressText").innerHTML = "0%";
    document.getElementById("clonerEtaText").innerHTML = "Hesaplanıyor...";

    try {
        let r = await window.pywebview.api.start_cloner(tokenToUse, sourceId, targetId);
        if (r.status === "error") {
            document.getElementById("clonerResult").className = "result-box glow-error mt-20";
            document.getElementById("clonerStatusText").innerHTML = escapeHtml(r.msg);
            document.getElementById("btnStartCloner").disabled = false;
            document.getElementById("btnStartCloner").innerHTML = "🔄 Kopyalamayı Başlat";
        }
    } catch (e) {
        document.getElementById("clonerResult").className = "result-box glow-error mt-20";
        document.getElementById("clonerStatusText").innerHTML = "API Hatası: " + escapeHtml(e);
        document.getElementById("btnStartCloner").disabled = false;
        document.getElementById("btnStartCloner").innerHTML = "🔄 Kopyalamayı Başlat";
    }
}

// Backend'den (evaluate_js) çağrılan fonksiyon
function updateClonerProgress(msg, progress, eta) {
    let statusText = document.getElementById("clonerStatusText");
    
    // Mesajı log gibi alta ekleme (sadece son 5 mesaj kalsın)
    let currentLogs = statusText.innerHTML.split("<br>");
    if (currentLogs.length > 5) currentLogs.shift();
    if(msg) currentLogs.push(escapeHtml(msg));
    statusText.innerHTML = currentLogs.join("<br>");
    
    if (progress >= 0) {
        document.getElementById("clonerProgressFill").style.width = progress + "%";
        document.getElementById("clonerProgressText").innerHTML = progress + "%";
    }
    if (eta) {
        document.getElementById("clonerEtaText").innerHTML = escapeHtml(eta);
    }
    
    // Bittiğinde butonu aç
    if (progress >= 100) {
        document.getElementById("btnStartCloner").disabled = false;
        document.getElementById("btnStartCloner").innerHTML = "🔄 Kopyalamayı Başlat";
        if (msg.includes("HATA") || msg.includes("İptal")) {
            document.getElementById("clonerResult").className = "result-box glow-error mt-20";
        } else {
            document.getElementById("clonerResult").className = "result-box glow-success mt-20";
        }
    }
}

// =============================================
//  PENCERE KONTROLLERİ
// =============================================
async function minimizeApp() { await window.pywebview.api.minimize_window(); }
async function maximizeApp() { await window.pywebview.api.toggle_maximize(); }
async function closeApp() { await window.pywebview.api.close_window(); }