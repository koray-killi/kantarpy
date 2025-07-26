import os
import csv
import json
from datetime import datetime

CSV_FILE_PATH = 'fis_dokumu.csv'
MUSTAHSIL_FILE_PATH = 'mustahsiller.json'

class Mal:
    """Mal bilgilerini tutan sınıf."""
    def __init__(self, sahip, cins, kasa, dolu_kantar, bos_kantar, adet):
        self.sahip = sahip
        self.cins = cins
        self.kasa = kasa
        self.bos_kantar = float(bos_kantar)
        self.dolu_kantar = float(dolu_kantar)
        self.kantar_fark = self.dolu_kantar - self.bos_kantar
        self.adet = int(adet)

    @property
    def net_kilo(self):
        """Net kiloyu hesaplayan property."""
        carpan = 0.0
        if self.kasa == 'siyah': carpan = 0.7
        elif self.kasa == 'sepet': carpan = 1.3
        elif self.kasa == 'standart': carpan = 1.5
        elif self.kasa == 'büyük': carpan = 2.0
        return (self.dolu_kantar - self.bos_kantar) - (self.adet * carpan)

    @property
    def dara(self):
        """Dara miktarını hesaplayan property."""
        carpan = 0.0
        if self.kasa == 'siyah': carpan = 0.7
        elif self.kasa == 'sepet': carpan = 1.3
        elif self.kasa == 'standart': carpan = 1.5
        elif self.kasa == 'büyük': carpan = 2.0
        return self.adet * carpan

def append_to_csv(mustahsil_adi, mal_listesi):

    file_exists = os.path.isfile(CSV_FILE_PATH)
    with open(CSV_FILE_PATH, mode='a', newline='', encoding='utf-8-sig') as file:
        writer = csv.writer(file, delimiter=';')
        if not file_exists:
            writer.writerow(['Tarih', 'Müstahsil Adı', 'Cins', 'Kasa', 'Dolu Kantar', 'Boş Kantar', 'Kantar Fark', 'Adet', 'Dara', 'Net Kilo'])
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for mal in mal_listesi:
            writer.writerow([
                current_time, mustahsil_adi, mal.cins, mal.kasa,
                f"{mal.dolu_kantar:.2f}", f"{mal.bos_kantar:.2f}", f"{mal.kantar_fark:.2f}",
                mal.adet, f"{mal.dara:.2f}", f"{mal.net_kilo:.2f}"
            ])


def get_all_mustahsiller():
    """mustahsiller.json dosyasından tüm kayıtlı müstahsilleri okur."""
    if not os.path.exists(MUSTAHSIL_FILE_PATH):
        return []
    try:
        with open(MUSTAHSIL_FILE_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []

def save_mustahsil(name_to_save):
    """Yeni bir müstahsil adını listeye ekler, eğer zaten yoksa."""
    if not name_to_save:
        return
    
    # İsmi standartlaştırmak için baş harfleri büyük yap
    formatted_name = name_to_save.strip().title()
    
    mustahsiller = get_all_mustahsiller()
    
    # Büyük/küçük harf duyarsız kontrol yap
    if formatted_name.lower() not in (m.lower() for m in mustahsiller):
        mustahsiller.append(formatted_name)
        # Alfabetik olarak sırala
        mustahsiller.sort()
        try:
            with open(MUSTAHSIL_FILE_PATH, 'w', encoding='utf-8') as f:
                json.dump(mustahsiller, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Müstahsil kaydedilirken hata oluştu: {e}")

