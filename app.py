from flask import Flask, render_template, request, jsonify
from helpers import Mal, append_to_csv, get_all_mustahsiller, save_mustahsil
from printer import yazdir # Güncellenmiş printer.py'den import ediliyor
import sys

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/mustahsiller', methods=['GET'])
def api_get_mustahsiller():
    return jsonify(get_all_mustahsiller())

@app.route('/print_and_save', methods=['POST'])
def print_and_save():
    data = request.get_json()
    required_keys = ['mustahsilAdi', 'malListesi', 'fisTarihi', 'printerConfig']
    if not data or not all(key in data for key in required_keys):
        return jsonify({'status': 'error', 'message': 'Eksik veri gönderildi.'}), 400

    mustahsil_adi = data['mustahsilAdi']
    mal_listesi_json = data['malListesi']
    fis_tarihi = data['fisTarihi']
    printer_config = data['printerConfig']

    mal_nesneleri = []
    for item_data in mal_listesi_json:
        mal = Mal(
            sahip=mustahsil_adi, cins=item_data['cins'], kasa=item_data['kasaTuru'],
            dolu_kantar=float(item_data['doluKantar']), bos_kantar=float(item_data['bosKantar']),
            adet=int(item_data['adet'])
        )
        mal_nesneleri.append(mal)

    if not mustahsil_adi or not mal_nesneleri:
        return jsonify({'status': 'error', 'message': 'Müstahsil adı veya mal listesi boş olamaz.'}), 400

    try:
        append_to_csv(mustahsil_adi, mal_nesneleri, fis_tarihi)
        
        # Arayüzden gelen VID ve PID'yi al. Hex string'i integer'a çevir.
        vid = int(printer_config.get('vid', '0x8866'), 16)
        pid = int(printer_config.get('pid', '0x0100'), 16)
        
        # Yazdır fonksiyonunu yeni ayarlar ile çağır
        yazdir(mustahsil_adi, mal_nesneleri, fis_tarihi=fis_tarihi, vid=vid, pid=pid)
        yazdir(mustahsil_adi, mal_nesneleri, fis_tarihi=fis_tarihi, vid=vid, pid=pid)
        

        save_mustahsil(mustahsil_adi)
        return jsonify({'status': 'success', 'message': 'Fiş başarıyla kaydedildi ve yazdırıldı.'})

    except Exception as e:
        print(f"Hata oluştu: {e}", file=sys.stderr)
        return jsonify({'status': 'error', 'message': f'Sunucu hatası: {e}'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
