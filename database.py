import sqlite3
from datetime import datetime

DB_NAME = "vouchers.db"

def get_db_connection():
    """Mendapatkan koneksi ke database."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row # Memungkinkan akses kolom berdasarkan nama
    return conn

def create_database(db_name="vouchers.db"):
    """
    Membuat tabel 'vouchers' jika belum ada.
    """
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

def check_voucher_status(code):
    """
    Memeriksa status voucher di database.
    Mengembalikan dictionary status atau None jika tidak ditemukan.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM vouchers WHERE code = ?", (code,))
    voucher = cursor.fetchone()
    conn.close()
    if voucher:
        return dict(voucher) # Mengubah Row objek menjadi dictionary
    return None

def mark_voucher_used(code):
    """
    Mengubah status voucher menjadi 'sudah_digunakan' dan mencatat waktu penggunaan.
    Mengembalikan True jika berhasil, False jika gagal (misal: kode tidak ditemukan).
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute(
            "UPDATE vouchers SET status = ?, used_at = ? WHERE code = ?",
            ('sudah_digunakan', current_time, code)
        )
        conn.commit()
        return cursor.rowcount > 0 # Mengembalikan True jika ada baris yang diupdate
    except Exception as e:
        print(f"Terjadi kesalahan saat memperbarui voucher: {e}")
        return False
    finally:
        conn.close()

def is_voucher_expired(expiry_date_str):
    """
    Memeriksa apakah tanggal kedaluwarsa sudah terlampaui.
    """
    if not expiry_date_str: # Jika tidak ada tanggal kedaluwarsa, anggap tidak kadaluarsa
        return False
    
    expiry_date = datetime.strptime(expiry_date_str, '%Y-%m-%d')
    return datetime.now() > expiry_date