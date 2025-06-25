# app.py (menggunakan Flask)
from flask import Flask, render_template, request, jsonify
import database

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/scan', methods=['POST'])
def scan_voucher():
    data = request.json
    voucher_code = data.get('code', '').strip().upper()

    if not voucher_code:
        return jsonify({"status": "error", "message": "Kode voucher tidak boleh kosong."}), 400

    voucher_data = database.check_voucher_status(voucher_code)

    if voucher_data:
        if database.is_voucher_expired(voucher_data['expiry_date']):
            return jsonify({
                "status": "expired",
                "message": "Voucher ini sudah melewati tanggal kedaluwarsa.",
                "code": voucher_code
            })
        elif voucher_data['status'] == 'sudah_digunakan':
            return jsonify({
                "status": "used",
                "message": f"Voucher ini sudah digunakan pada: {voucher_data['used_at']}",
                "code": voucher_code
            })
        else:
            # Voucher valid, tandai sudah digunakan
            if database.mark_voucher_used(voucher_code):
                return jsonify({
                    "status": "success",
                    "message": f"Voucher '{voucher_code}' senilai Rp{voucher_data['value']:,} berhasil digunakan!",
                    "code": voucher_code,
                    "value": voucher_data['value']
                })
            else:
                return jsonify({
                    "status": "error",
                    "message": "Gagal memperbarui status voucher. Coba lagi."
                }), 500
    else:
        return jsonify({
            "status": "not_found",
            "message": "Voucher tidak ditemukan. Mohon periksa kembali kodenya."
        }), 404

if __name__ == '__main__':
    # Pastikan database sudah ada
    database.create_database() # Panggil fungsi ini dari database.py jika belum ada
    app.run(debug=True)