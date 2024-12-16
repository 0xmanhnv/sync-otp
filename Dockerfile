# Sử dụng Python image
FROM python:3.10-slim

# Copy toàn bộ code vào container
WORKDIR /app
COPY . /app

# Cài đặt thư viện cần thiết
RUN pip install --no-cache-dir -r requirements.txt

# Chạy ứng dụng
CMD ["python", "app.py"]
