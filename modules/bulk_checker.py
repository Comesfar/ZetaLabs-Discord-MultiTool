import requests
import logging
import webview
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger("ZetaLabs")

DEFAULT_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"

class BulkCheckerMixin:
    def bulk_check_tokens(self, tokens_text, token_type):
        lines = [line.strip() for line in tokens_text.strip().split('\n') if line.strip()]
        if not lines:
            return {"status": "error", "msg": "Hiç token bulunamadı!"}

        def check_single(token):
            headers = {
                "Authorization": f"Bot {token}" if token_type == "bot" else token,
                "User-Agent": DEFAULT_UA
            }
            masked = self._mask_token(token)
            try:
                req = requests.get("https://discord.com/api/v10/users/@me", headers=headers, timeout=6)
                if req.status_code == 200:
                    data = req.json()
                    uname = data.get('username', 'Bilinmiyor')
                    disc = data.get('discriminator', '0')
                    name = uname if disc == '0' else f"{uname}#{disc}"
                    return {"token": masked, "status": "valid", "name": name, "is_valid": True}
                elif req.status_code == 403:
                    return {"token": masked, "status": "locked", "name": "Kilitli (Doğrulama Gerekli)", "is_valid": False}
                elif req.status_code == 429:
                    return {"token": masked, "status": "ratelimit", "name": "Rate Limit", "is_valid": False}
                else:
                    return {"token": masked, "status": "invalid", "name": "Geçersiz", "is_valid": False}
            except Exception:
                return {"token": masked, "status": "error", "name": "Bağlantı hatası", "is_valid": False}

        # Eşzamanlı kontrol (maksimum 10 iş parçacığı)
        workers = min(10, len(lines))
        with ThreadPoolExecutor(max_workers=workers) as executor:
            results = list(executor.map(check_single, lines))

        valid_count = sum(1 for r in results if r.get("is_valid"))
        invalid_count = len(lines) - valid_count

        self._add_log(
            "Toplu Token", 
            f"{len(lines)} token kontrol — {valid_count} geçerli, {invalid_count} geçersiz", 
            "success" if valid_count > 0 else "error"
        )
        return {
            "status": "success",
            "results": results,
            "total": len(lines),
            "valid": valid_count,
            "invalid": invalid_count
        }

    def load_tokens_file(self):
        try:
            result = webview.windows[0].create_file_dialog(
                webview.OPEN_DIALOG,
                file_types=('Text Files (*.txt)',)
            )
            if result and len(result) > 0:
                with open(result[0], 'r', encoding='utf-8') as f:
                    return {"status": "success", "content": f.read()}
            return {"status": "cancelled", "msg": "Dosya seçilmedi."}
        except Exception as e:
            logger.error(f"Dosya okuma hatası: {e}")
            return {"status": "error", "msg": "Dosya okunamadı!"}
