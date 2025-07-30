from escpos.printer import Usb
from datetime import datetime

# FONKSİYON İMZASI GÜNCELLENDİ:
# Artık arayüzden gelen fis_tarihi, vid ve pid değerlerini alıyor.
# Varsayılan değerler, ayar yapılmadığında sorun çıkmasını engeller.
def yazdir(m_adi, mal_liste, fis_tarihi, vid=0x8866, pid=0x0100):
    
    # DEĞİŞİKLİK 1: YAZICI BAĞLANTISI DİNAMİK HALE GETİRİLDİ
    # Arayüzdeki Ayarlar menüsünden gelen VID ve PID değerleri burada kullanılır.
    try:
        printer = Usb(vid, pid, interface=0, out_ep=0x2, in_ep=0x81)
    except Exception as e:
        print(f"YAZICI HATASI: Yazıcıya bağlanılamadı (VID={hex(vid)}, PID={hex(pid)}). Ayarları kontrol edin. Hata: {e}")
        return # Hata durumunda programın çökmesini engelle

    # --- ORİJİNAL KODUNUZ (HİÇBİR DEĞİŞİKLİK YAPILMADI) ---
    def buyuk_yaz(text):
        printer._raw(b"\x1B\x21\x30")  # width=2, height=2
        printer.text(f"{text}\n")
        printer._raw(b"\x1B\x21\x00") 
        # normal fonta geri dön
    
    def yaz(text):
        printer._raw(b"\x1B\x21\x30") # HER SATIRI BÜYÜK YAPAN ORİJİNAL KODUNUZ
        printer._raw(text.encode("cp857", errors="replace"))

    def veri_yaz(name_column,data_column):
        printer.set(bold=True)
        yaz(name_column)
        printer.set(bold=False)
        yaz(" "+data_column + "\n")

    # === BAŞLIK (ORİJİNAL) ===
    printer.set(align='center', bold=True)
    buyuk_yaz("MAL BILGI FISI\n\n")
    printer.set(align='left')
    yaz(f"Müstahsil Adı:\n"+m_adi)
    yaz("\n")
    safi = float()
    
    # === MAL LİSTESİ DÖNGÜSÜ (ORİJİNAL) ===
    for item in mal_liste:
        carpan = float()
        if item.kasa == 'siyah':
            carpan = 0.7
        if item.kasa == 'sepet':
            carpan = 1.3
        if item.kasa == 'standart':
            carpan = 1.5
        if item.kasa == 'büyük':
            carpan = 2.0
        # Eklediğimiz yeni kasa tipleri için destek
        if item.kasa == 'dev':
            carpan = 2.5
            
        net_kilo = str(round((item.dolu_kantar - item.bos_kantar) - (item.adet * carpan), 2))
        yaz("------------------------")
        yaz(f"D. Kantar   : {item.dolu_kantar:.2f} kg\n")
        yaz(f"B.  Kantar  : {item.bos_kantar:.2f} kg\n")
        yaz(f"Kantar Fark : {item.kantar_fark:.2f} kg")
        yaz("\n")
        yaz("\n")
        yaz("\n")
        veri_yaz("Mal Cins :",item.cins)
        veri_yaz("Adet     :",str(item.adet))
        veri_yaz("Kasa Tür :",item.kasa)
        dara = str(round(item.adet*carpan, 2))
        veri_yaz("Dara     :",dara +" kg")
        veri_yaz("Safi     :",net_kilo + " kg")
        safi += float(net_kilo)
        yaz("\n")
        
    # === ALT BİLGİ (ORİJİNAL) ===
    yaz("------------------------\n")
    yaz("NET SAFI: " + str(round(safi, 2))+ " kg \n")
    yaz("------------------------")
    printer.set(align='center')
    yaz("\n")

    # DEĞİŞİKLİK 2: TARİH DİNAMİK HALE GETİRİLDİ
    # Arayüzden gelen tarih kullanılır, eğer bir sorun olursa o anın zamanı basılır.
    try:
        dt_object = datetime.strptime(fis_tarihi, '%Y-%m-%d %H:%M')
        formatted_date = dt_object.strftime('%d.%m.%Y %H:%M:%S')
        yaz("\nTarih:\n" + formatted_date + "\n")
    except (ValueError, TypeError):
        yaz("\nTarih:\n" + datetime.now().strftime("%d.%m.%Y %H:%M:%S") + "\n")

    # === FİŞ SONU (ORİJİNAL) ===
    yaz("\n")
    yaz("Bereketli olsun...")
    printer.set(align='center')
    yaz("\n")
    yaz("\n")
    yaz("\n")
    printer._raw(b'\x1B!\x00') # Fontu sıfırla
    printer.text("Bilgilendirme amaçlıdır.")

    printer.cut()
    printer.close()
    return print("Yazdırma Başarılı....")