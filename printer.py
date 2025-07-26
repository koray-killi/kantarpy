from escpos.printer import Usb
from datetime import datetime




def yazdir(m_adi,mal_liste):
    printer = Usb(0x8866, 0x0100, interface=0, out_ep=0x2, in_ep=0x81)
    def buyuk_yaz(text):
        printer._raw(b"\x1B\x21\x30")  # width=2, height=2
        printer.text(f"{text}\n")
        printer._raw(b"\x1B\x21\x00") 
        # normal fonta geri dön
    def yaz(text):
        printer._raw(b"\x1B\x21\x30")
        printer._raw(text.encode("cp857"))
    def veri_yaz(name_column,data_column):
        printer.set(bold=True)
        yaz(name_column)
        printer.set(bold=False)
        yaz(" "+data_column + "\n")


    # === BAŞLIK ===

    printer.set(align='center', bold=True)
    buyuk_yaz("MAL BILGI FISI\n\n")
    printer.set(align='left')
    yaz(f"Müstahsil Adı:\n"+m_adi)
    yaz("\n")
    safi = float()
    for item in mal_liste:
        # === KANTAR BİLGİLERİ ===
        carpan = float()
        if item.kasa == 'siyah':
            carpan = 0.7
        if item.kasa == 'sepet':
            carpan = 1.3
        if item.kasa == 'standart':
            carpan = 1.5
        if item.kasa == 'büyük':
            carpan = 2
        net_kilo = str((item.dolu_kantar - item.bos_kantar) - (item.adet * carpan))
        yaz("------------------------")
        yaz(f"D. Kantar   : {item.dolu_kantar} kg\n")
        yaz(f"B.  Kantar  : {item.bos_kantar} kg\n")
        yaz(f"Kantar Fark : {item.dolu_kantar - item.bos_kantar} kg")
        yaz("\n")
        yaz("\n")
        # === ÜRÜN BİLGİLERİ ===
        yaz("\n")
        veri_yaz("Mal Cins :",item.cins)
        veri_yaz("Adet     :",str(item.adet))
        veri_yaz("Kasa Tür :",item.kasa)
        dara = str(item.adet*carpan)
        veri_yaz("Dara     :",dara +" kg")
        veri_yaz("Safi     :",net_kilo + " kg")
        safi += float(net_kilo)
        yaz("\n")
    # === Tarih ===
    yaz("------------------------\n")
    yaz("NET SAFI: " + str(safi)+ " kg \n")
    yaz("------------------------")
    printer.set(align='center')
    yaz("\n")
    yaz("\nTarih: " +"\n" + datetime.now().strftime("%d.%m.%Y %H:%M:%S") + "\n")


    # === Alt Bilgi ===
    yaz("\n")
    yaz("Bereketli olsun...")
    printer.set(align='center')
    yaz("\n")
    yaz("\n")
    yaz("\n")
    printer._raw(b'\x1B!\x00')
    printer.text("Bilgilendirme amaçlıdır.")

    printer.cut()
    printer.close()
    return print("Yazdırma Başarılı....")

