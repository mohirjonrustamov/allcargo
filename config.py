import os

TOKEN = os.getenv("TOKEN", "fallback-token")
ADMIN_CODE = "Q1w2e3r4+"
DATA_FILE = "bot_data.json"
CHANNEL_ID = "@crm_tekshiruv"
WEBHOOK_PATH = "/webhook"
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "fallback-secret")
WEBHOOK_URL = f"https://allcargo.onrender.com{WEBHOOK_PATH}"
BITRIX_LEAD_URL = "https://pbsimpex.bitrix24.ru/rest/56/8fmh9217sb9emy66/crm.lead.add.json"
