# Menggunakan base image Python 3.9
FROM python:3.9

# Menginstal nmap
RUN apt-get update && \
    apt-get install -y nmap && \
    apt-get clean

# Menginstal nikto
RUN apt-get update && \
    apt-get install -y nikto && \
    apt-get clean

# Menyimpan direktori kerja di /app dalam container
WORKDIR /app

# Menyalin file requirements.txt ke dalam container
COPY requirements.txt .

# Menginstal dependencies yang diperlukan
RUN pip install --no-cache-dir -r requirements.txt

# Menyalin seluruh kode aplikasi ke dalam container
COPY . .

# Menjalankan aplikasi Flask dengan gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]

