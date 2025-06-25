import qrcode
import uuid
import os
import sqlite3
from datetime import datetime, timedelta

def create_database(db_name="vouchers.db"):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vouchers (
            code TEXT PRIMARY KEY,
            status TEXT NOT NULL DEFAULT 'belum_digunakan',
            value REAL,
            expiry_date TEXT,
            used_at TEXT
        )
    ''')
    conn.commit()
    conn.close()

def generate_voucher(num_vouchers, value=50000, days_until_expiry=365, db_name="vouchers.db", barcode_dir="barcodes"):
    """
    Menghasilkan kode voucher unik, membuat QR Code, dan menyimpannya ke database.

    Args:
        num_vouchers (int): Jumlah voucher yang ingin dibuat.
        value (float): Nilai nominal voucher.
        days_until_expiry (int): Jumlah hari sampai voucher kedaluwarsa dari tanggal pembuatan.
        db_name (str): Nama file database SQLite.
        barcode_dir (str): Direktori untuk menyimpan gambar barcode.
    """
    if not os.path.exists(barcode_dir):
        os.makedirs(barcode_dir)

    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    generated_count = 0
    while generated_count < num_vouchers:
        # Buat kode unik menggunakan UUID (Universally Unique Identifier)
        voucher_code = str(uuid.uuid4()).replace('-', '').upper()[:12] # Ambil 12 karakter pertama
        
        # Cek apakah kode sudah ada di database (untuk menghindari duplikasi sangat jarang)
        cursor.execute("SELECT code FROM vouchers WHERE code = ?", (voucher_code,))
        if cursor.fetchone():
            continue # Jika sudah ada, generate lagi

        # Hitung tanggal kedaluwarsa
        expiry_date = (datetime.now() + timedelta(days=days_until_expiry)).strftime('%Y-%m-%d')

        # Simpan ke database
        try:
            cursor.execute(
                "INSERT INTO vouchers (code, value, expiry_date) VALUES (?, ?, ?)",
                (voucher_code, value, expiry_date)
            )
            conn.commit()
            
            # Buat QR Code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(voucher_code)
            qr.make(fit=True)

            img = qr.make_image(fill_color="black", back_color="white")
            img_path = os.path.join(barcode_dir, f"{voucher_code}.png")
            img.save(img_path)

            print(f"Voucher '{voucher_code}' (nilai: {value}, kadaluarsa: {expiry_date}) berhasil dibuat dan QR Code disimpan di {img_path}")
            generated_count += 1

        except sqlite3.IntegrityError:
            print(f"Kode voucher {voucher_code} sudah ada (sangat jarang terjadi). Mencoba lagi...")
            continue # Jika terjadi IntegrityError (misal: PRIMARY KEY unik duplikat), coba lagi

    conn.close()
    print(f"\n{num_vouchers} voucher berhasil dibuat dan disimpan di database.")

if __name__ == "__main__":
    DB_NAME = "vouchers.db"
    BARCODE_DIR = "barcodes"
    
    create_database(DB_NAME)
    
    num_to_generate = int(input("Berapa banyak voucher yang ingin Anda buat? "))
    voucher_value = float(input("Berapa nilai nominal setiap voucher (contoh: 50000)? "))
    expiry_days = int(input("Berapa hari sampai voucher kedaluwarsa (contoh: 365)? "))

    generate_voucher(num_to_generate, voucher_value, expiry_days, DB_NAME, BARCODE_DIR)