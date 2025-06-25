import database
from datetime import datetime

def run_scanner_cli():
    print("--- Sistem Scanner Voucher ---")
    print("Ketik 'exit' untuk keluar.")

    while True:
        voucher_code = input("\nMasukkan kode voucher atau scan barcode: ").strip().upper()

        if voucher_code == 'EXIT':
            print("Terima kasih, sampai jumpa!")
            break

        voucher_data = database.check_voucher_status(voucher_code)

        if voucher_data:
            print(f"Voucher Ditemukan: {voucher_data['code']}")
            print(f"Nilai: Rp{voucher_data['value']:,}")
            print(f"Status: {voucher_data['status'].replace('_', ' ').title()}")
            print(f"Tanggal Kedaluwarsa: {voucher_data['expiry_date']}")

            if database.is_voucher_expired(voucher_data['expiry_date']):
                print(">>> STATUS: KADALUARSA <<<")
                print("Voucher ini sudah melewati tanggal kedaluwarsa dan tidak bisa digunakan.")
            elif voucher_data['status'] == 'sudah_digunakan':
                print(">>> STATUS: SUDAH DIGUNAKAN <<<")
                print(f"Voucher ini sudah digunakan pada: {voucher_data['used_at']}")
            else:
                confirm = input("Voucher valid. Gunakan voucher ini sekarang? (y/n): ").lower()
                if confirm == 'y':
                    if database.mark_voucher_used(voucher_code):
                        print(">>> VOUCHER BERHASIL DIGUNAKAN! <<<")
                    else:
                        print("Gagal menggunakan voucher. Coba lagi.")
                else:
                    print("Penggunaan voucher dibatalkan.")
        else:
            print("Voucher tidak ditemukan. Mohon periksa kembali kodenya.")

if __name__ == "__main__":
    run_scanner_cli()