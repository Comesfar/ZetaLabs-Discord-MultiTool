import logging
from datetime import datetime, timezone

logger = logging.getLogger("ZetaLabs")

class SnowflakeDecoderMixin:
    def decode_snowflake(self, snowflake_id):
        try:
            if not snowflake_id.isdigit():
                return {"status": "error", "msg": "ID sadece rakamlardan oluşmalıdır!"}
                
            id_int = int(snowflake_id)
            timestamp = ((id_int >> 22) + 1420070400000) / 1000
            
            dt = datetime.fromtimestamp(timestamp, tz=timezone.utc)
            
            self._add_log("Snowflake", f"{snowflake_id} çevrildi", "success")
            return {
                "status": "success",
                "date_utc": dt.strftime("%d/%m/%Y %H:%M:%S UTC"),
                "timestamp": int(timestamp),
                "internal_worker": (id_int & 0x3E0000) >> 17,
                "internal_process": (id_int & 0x1F000) >> 12,
                "increment": id_int & 0xFFF
            }
        except Exception as e:
            return {"status": "error", "msg": f"Geçersiz Snowflake ID: {e}"}
