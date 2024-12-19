import os
import logging
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import pyotp
import requests
import sys
import datetime


# Load biến môi trường
load_dotenv()

# Lấy thông tin từ .env
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
NGROK_URL = os.getenv("NGROK_URL")  # URL từ Ngrok
PORT = int(os.getenv("PORT", 8443))
USERS = {
    "vcs.anhnt" : os.getenv("USER_OTP_VCS_AHNT", ""),
    "vcs.minhtn" : os.getenv("USER_OTP_VCS_MIHTN", ""),
    "vcs.dainc" : os.getenv("USER_OTP_VCS_DANC", ""),
    "vcs.ngandpx" : os.getenv("USER_OTP_VCS_NGNDPX", ""),
    "vcs.haidv" : os.getenv("USER_OTP_VCS_HADV", ""),
    "vcs.binhhh" : os.getenv("USER_OTP_VCS_BIHHH", ""),
    "vcs.lamnc" : os.getenv("USER_OTP_VCS_LMNC", ""),
    "vcs.datlq" : os.getenv("USER_OTP_VCS_DALQ", "")
}

# Cấu hình logging
log_file_path = "./logs/app.log"
os.makedirs(os.path.dirname(log_file_path), exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    handlers=[
        logging.FileHandler(log_file_path),  # Ghi log vào file
        logging.StreamHandler(sys.stdout)
    ]
)

# Tạo ứng dụng Flask
app = Flask(__name__)


WORKING_DAYS = range(0, 6)  # 0: Thứ Hai, 4: Thứ Sáu
WORKING_HOURS = range(6, 19)  # 8 giờ đến 18 giờ
END_TIME=False
ADMIN_ID=833425787


def is_working_hour():
    if END_TIME:
        return False
    now = datetime.datetime.now()
    
    if now.weekday() in WORKING_DAYS and now.hour in WORKING_HOURS:
        return True
    return False


def send_message(chat_id, text):
    """
    Gửi tin nhắn đến người dùng Telegram.
    """
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
    }
    response = requests.post(url, json=payload)
    logging.info(f"Gửi tin nhắn: {response.status_code}, {response.text}".encode("ascii", "ignore").decode("ascii"))

def get_otp(user):
    """
    Lấy OTP cho user.
    """
    key_otp = USERS.get(user, "")
    if key_otp == "":
        logging.warning(f"Không tìm thấy OTP cho user: {user}".encode("ascii", "ignore").decode("ascii"))
        return "Không tìm thấy OTP"
    totp = pyotp.TOTP(key_otp)
    otp = totp.now()
    logging.info(f"OTP của user {user}: {otp}".encode("ascii", "ignore").decode("ascii"))
    return otp

@app.route('/nup4kachi/webhook', methods=['POST'])
def webhook():
    """
    Xử lý các yêu cầu từ Telegram gửi đến.
    """
    data = request.get_json()
    logging.info(f"Nhận dữ liệu: {data}".encode("ascii", "ignore").decode("ascii"))
    
    
    global END_TIME
    global WORKING_DAYS
    global WORKING_HOURS

    # if not is_working_hour() or END_TIME:
    #     args = text.split(" ")
    #     if len(args) < 2:
    #         send_message(chat_id, "Vui lòng nhập lệnh.")
    #         return jsonify({"ok": True})
    #     cmd = args[1]
    #     if cmd == "open":
    #         END_TIME=False
    #         WORKING_DAYS = range(0, 6)  # 0: Thứ Hai, 4: Thứ Sáu
    #         WORKING_HOURS = range(0, 23)  # 8 giờ đến 18 giờ
    #         send_message(chat_id, "Bot đã được mở full thời gian")
    #         return jsonify({"ok": True})
    #     send_message(data["message"]["chat"]["id"], "Hết thời gian làm việc!!!")
    #     return jsonify({"ok": True})

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")
        
        if text.startswith("/otp"):
            # Lấy username từ tin nhắn
            args = text.split(" ")
            if len(args) < 2:
                send_message(chat_id, "Vui lòng nhập username.")
            else:
                user = args[1]
                otp = get_otp(user)
                send_message(chat_id, f"Mã OTP của {user} là: {otp}")
        elif text.startswith("/open_time") and data["message"]["chat"]["id"] == ADMIN_ID:
            args = text.split(" ")
            if len(args) < 2:
                send_message(chat_id, "Vui lòng nhập lệnh.")
            else:
                cmd = args[1]
                if cmd == "open":
                    END_TIME=False
                    WORKING_DAYS = range(0, 6)  # 0: Thứ Hai, 4: Thứ Sáu
                    WORKING_HOURS = range(0, 23)  # 8 giờ đến 18 giờ
                    send_message(chat_id, "Bot đã được mở full thời gian")
                elif cmd == "close":
                    END_TIME=False
                    WORKING_DAYS = range(0, 6)  # 0: Thứ Hai, 4: Thứ Sáu
                    WORKING_HOURS = range(6, 19)  # 8 giờ đến 18 giờ
                    send_message(chat_id, "Bot đang chạy tại giờ 6h - 19h")
                elif cmd == "end":
                    END_TIME=True
                    send_message(chat_id, "Hết thời gian làm việc")
                else:
                    send_message(chat_id, "Lệnh không hợp lệ. Sử dụng /open_time open/close")
        elif text.startswith("/help"):
            send_message(chat_id, "Sử dụng /otp <username> gửi OTP.")
        else:
            send_message(chat_id, "Lệnh không hợp lệ. Sử dụng /otp <username>")
    return jsonify({"status": "ok"})

def set_webhook():
    """
    Đặt webhook trên Telegram.
    """
    # Đặt webhook
    if not BOT_TOKEN or not NGROK_URL:
        logging.error("TELEGRAM_BOT_TOKEN hoặc NGROK_URL chưa được cấu hình trong .env".encode("ascii", "ignore").decode("ascii"))
        send_message(ADMIN_ID, "TELEGRAM_BOT_TOKEN hoặc NGROK_URL chưa được cấu hình trong .env")
        exit(1)

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook"
    webhook_url = f"{NGROK_URL}/nup4kachi/webhook"
    response = requests.post(url, json={"url": webhook_url})
    if response.status_code == 200:
        logging.info(f"Webhook đã được đặt tại: {webhook_url}".encode("ascii", "ignore").decode("ascii"))
    else:
        logging.error(f"Lỗi khi đặt webhook: {response.status_code}, {response.text}".encode("ascii", "ignore").decode("ascii"))

set_webhook()
# if __name__ == "__main__":
#     # Đặt webhook
#     if not BOT_TOKEN or not NGROK_URL:
#         logging.error("TELEGRAM_BOT_TOKEN hoặc NGROK_URL chưa được cấu hình trong .env".encode("ascii", "ignore").decode("ascii"))
#         exit(1)

#     set_webhook()

#     # Chạy Flask
#     logging.info(f"Chạy ứng dụng tại cổng {PORT}".encode("ascii", "ignore").decode("ascii"))
#     app.run(host="0.0.0.0", port=PORT)