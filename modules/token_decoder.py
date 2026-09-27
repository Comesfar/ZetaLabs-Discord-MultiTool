import logging
import base64
from datetime import datetime, timezone

logger = logging.getLogger("ZetaLabs")

class TokenDecoderMixin:
    def decode_token(self, token):
        try:
            parts = token.split(".")
            if len(parts) < 2:
                return {"status": "error", "msg": "Geçersiz token formatı!"}
                
            def pad_base64(data):
                missing_padding = len(data) % 4
                if missing_padding:
                    data += '=' * (4 - missing_padding)
                return data

            user_id_b64 = pad_base64(parts[0])
            user_id = base64.b64decode(user_id_b64).decode('utf-8')
            
            timestamp_b64 = pad_base64(parts[1])
            timestamp_bytes = base64.b64decode(timestamp_b64)
            
            try:
                creation_time = "Bilinmiyor"
                if len(timestamp_bytes) == 4:
                    ts = int.from_bytes(timestamp_bytes, 'big') + 1293840000
                    creation_time = datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%d/%m/%Y %H:%M:%S UTC")
            except:
                pass

            self._add_log("Token Decoder", "Token bilgileri çözüldü", "success")
            return {
                "status": "success",
                "user_id": user_id,
                "creation_time": creation_time,
                "raw_part1": parts[0],
                "raw_part2": parts[1]
            }
        except Exception as e:
            return {"status": "error", "msg": f"Çözümleme hatası: Hatalı format."}
