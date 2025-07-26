from flask import Flask, render_template, request, jsonify
from helpers import Mal, append_to_csv, get_all_mustahsiller, save_mustahsil
from printer import yazdir
import sys

app = Flask(__name__)

@app.route('/')
def index():
    """Ana sayfayı render eder."""
    return render_template('index.html')

# --- YENİ API ENDPOINT'LERİ ---
@app.route('/api/mustahsiller', methods=['GET'])
def api_get_mustahsiller():
    """Kayıtlı tüm müstahsil isimlerini JSON olarak döndürür."""
    return jsonify(get_all_mustahsiller())

# --- GÜNCELLENMİŞ ENDPOINT ---
@app.route('/print_and_save', methods=['POST'])
def print_and_save():
    """
    Web arayüzünden gelen fiş verilerini alır, CSV'ye kaydeder,
    yazıcıya gönderir ve müstahsil adını veritabanına ekler.
    """
    data = request.get_json()
    if not data or 'mustahsilAdi' not in data or 'malListesi' not in data:
        return jsonify({'status': 'error', 'message': 'Eksik veri gönderildi.'}), 400

    mustahsil_adi = data['mustahsilAdi']
    mal_listesi_json = data['malListesi']

    mal_nesneleri = []
    for item_data in mal_listesi_json:
        try:
            mal = Mal(
                sahip=mustahsil_adi, cins=item_data['cins'], kasa=item_data['kasaTuru'],
                dolu_kantar=float(item_data['doluKantar']), bos_kantar=float(item_data['bosKantar']),
                adet=int(item_data['adet'])
            )
            mal_nesneleri.append(mal)
        except (KeyError, ValueError) as e:
            return jsonify({'status': 'error', 'message': f'Hatalı veri yapısı: {e}'}), 400

    if not mustahsil_adi or not mal_nesneleri:
        return jsonify({'status': 'error', 'message': 'Müstahsil adı veya mal listesi boş olamaz.'}), 400

    try:
        # 1. CSV dosyasına kaydet
        append_to_csv(mustahsil_adi, mal_nesneleri)

        # 2. Yazıcıya gönder (Bu fonksiyonun printer.py'de olması gerekir)
        yazdir(mustahsil_adi,mal_nesneleri)
        yazdir(mustahsil_adi,mal_nesneleri)
        # from printer import yazdir
        # yazdir(mustahsil_adi, mal_nesneleri)

        # 3. Müstahsil adını kaydet (YENİ)
        save_mustahsil(mustahsil_adi)

        return jsonify({'status': 'success', 'message': 'Fiş başarıyla kaydedildi ve yazdırıldı.'})

    except Exception as e:
        print(f"Hata oluştu: {e}", file=sys.stderr)
        return jsonify({'status': 'error', 'message': f'Sunucu hatası: {e}'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
