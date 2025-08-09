import requests

# Địa chỉ API (đổi thành đúng host và port của bạn)
url = "http://127.0.0.1:8000/analyze"

# Nếu API không cần gửi dữ liệu
response = requests.post(url)

# Nếu API trả về JSON
if response.status_code == 200:
    print("Kết quả:", response.json())
else:
    print("Lỗi:", response.status_code, response.text)
