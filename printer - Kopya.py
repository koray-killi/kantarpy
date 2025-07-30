from escpos.printer import Usb
from datetime import datetime

# FONKSİYON İMZASI GÜNCELLENDİ:
# Artık arayüzden gelen fis_tarihi, vid ve pid değerlerini alıyor.
# Varsayılan değerler, ayar yapılmadığında sorun çıkmasını engeller.
def yazdir(vid=0x8866, pid=0x0100):
    
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
    buyuk_yaz("OSMAN GÜCLÜ\n\n")
    printer.set(align='left')
    
   
    printer.cut()
    printer.close()
    return print("Yazdırma Başarılı....")


yazdir()