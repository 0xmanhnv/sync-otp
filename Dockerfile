# Sử dụng Python image
FROM python:3.10-slim

# Copy toàn bộ code vào container
WORKDIR /app

# Copy file yêu cầu và source code
COPY app/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY app/ .
COPY users.json /app/users.json


# Expose cổng 5000
EXPOSE 5000

# Chạy ứng dụng Flask qua Gunicorn
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]

# Chạy ứng dụng
# CMD ["python", "app.py"]
