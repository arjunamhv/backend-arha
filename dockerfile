# Menggunakan base image Python 3.9
FROM python:3.9

# Menginstal dependencies sistem
RUN apt-get update && \
    apt-get install -y nmap wget && \
    apt-get clean && \
    # Menginstal Nikto secara manual dari repositori master
    wget https://github.com/sullo/nikto/archive/master.tar.gz -O /tmp/nikto.tar.gz && \
    tar -xzvf /tmp/nikto.tar.gz -C /tmp/ && \
    mv /tmp/nikto-master /opt/nikto && \
    ln -s /opt/nikto/program/nikto.pl /usr/bin/nikto && \
    rm /tmp/nikto.tar.gz

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

