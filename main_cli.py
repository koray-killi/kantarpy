from colorama import just_fix_windows_console
from colorama import Fore, Back, Style
from printer import yazdir
import sys
import os
import subprocess



just_fix_windows_console()

def limit_input(dialog,condition_list):
    input_dialog = input(Fore.YELLOW + dialog + Style.RESET_ALL)
    while input_dialog not in condition_list:
        print(Fore.RED + "Geçersiz işlem." + Style.RESET_ALL)
        return limit_input(dialog,condition_list)
    return input_dialog

def fix_input(dialog):
    input_dialog = input(Fore.YELLOW + dialog + Style.RESET_ALL)
    while input_dialog =="" or input_dialog[0] == " " :
        print(Fore.RED + "Geçersiz işlem." + Style.RESET_ALL)
        return fix_input(dialog)
    return input_dialog

def num_input(dialog,type=None):
    if type == 'int':
        try:
            input_dialog = input(Fore.YELLOW + dialog + Style.RESET_ALL)
            input_dialog_numb = int(input_dialog)
            return input_dialog_numb
        except Exception:
            print(Fore.RED + "Geçersiz sayı." + Style.RESET_ALL)
            return num_input(dialog, type='int')
    try:
        input_dialog = input(Fore.YELLOW + dialog + Style.RESET_ALL)
        input_dialog_numb = float(input_dialog)
        return input_dialog_numb
    except Exception:
        print(Fore.RED + "Geçersiz sayı." + Style.RESET_ALL)
        return num_input(dialog)

def str_range(count):
    temp = list()
    try:
        for i in range(count):
            temp.append(f"{i}")
        
    except Exception:
        return print("List is not valid.")
    return temp
###### MENU ########

class Menu:
    def main_menu():
        print(Fore.GREEN + '''
┌───────────────────────────────────────┐
│        KORAY.FİS v1.0                 │
│   Müstahsil Bilgi Fişi Programı       │
└───────────────────────────────────────┘
Yapmak istediğiniz işlemi seçiniz:

   ● ANA MENÜ ●
───────────────────────────────────────
1. Yeni Fiş Oluştur
2. Yeni Pencere Aç
3. Günlük Döküm Oluştur
4. Ayarları Düzenle
0. Programdan Çık
───────────────────────────────────────
''' + Style.RESET_ALL)
        choose = limit_input("İşlem Giriniz: ",["1","2","3","0"])
        if choose == "1":
            return Fis.on_fis_menu()
        if choose == "2":
            def yeni_oturum_ac():
                python_exe = sys.executable
                dosya_yolu = os.path.abspath(__file__)

                # Yeni CMD penceresinde bu dosyayı başlat
                subprocess.Popen(
                    ['start', 'cmd', '/k', python_exe, dosya_yolu],
                    shell=True
                )
            yeni_oturum_ac()
            return Menu.main_menu()


        if choose == "3":
            pass
        if choose == "0":
            exit()

        
class Fis:
    mal_liste = []
    gecerli_musthasil = "(Lütfen Seçiniz)"
    def on_fis_menu():
        print("\n")
        isim = fix_input("Lütfen Müstahsil adı giriniz (İptal Etmek için '0' yazın): ")
        if isim == '0':
            return Menu.main_menu()
        Fis.gecerli_musthasil = isim
        return Fis.fis_menu()
    def sifirla():
        pass
    def fis_menu():
        print("\n" + Fore.CYAN)
        print(f'''
┌───────────────────────────────────────┐
│        KORAY.FİS v1.0                 │
│   Müstahsil Bilgi Fişi Programı       │
└───────────────────────────────────────┘
Yapmak istediğiniz işlemi seçiniz:

   ● FİŞ MENÜSÜ ●

Geçerli Müstahsil: {Fis.gecerli_musthasil}
───────────────────────────────────────
1. Müstahsil İsim Güncelle
2. Mala Ekleme Yap
3. Mal Çıkar
4. Fişi Yazdır
0. Fişi İptal Et
───────────────────────────────────────
''')
        choose = limit_input("İşlem Giriniz: ",["1","2","3","4","0"])
        if choose == "1":

            print("\n")
            isim = fix_input("Lütfen Müstahsil adı giriniz: ")
            Fis.gecerli_musthasil = isim
            print(Fis.gecerli_musthasil)
            return Fis.fis_menu()

        if choose == "2":
            temp_dolu_kantar = num_input("Dolu kantarı giriniz: ")
            temp_bos_kantar = num_input("Boş kantarı giriniz: ")
            temp_cins = fix_input("Malın cinsini giriniz: ")
            temp_kasa = limit_input("Kasa türünü giriniz (siyah 0.7, sepet 1.3, büyük 2, standart 1.5 ):\n ",['siyah','büyük','sepet','standart'])
            temp_adet = num_input("Kasa adedini giriniz: ", type='int')
            Fis.mal_liste.append(Mal(Fis.gecerli_musthasil,temp_cins,temp_kasa,temp_dolu_kantar,temp_bos_kantar,temp_adet))
            print(Fore.GREEN + f"{Fis.mal_liste.index(Fis.mal_liste[-1])+1} ID'li {temp_cins} malı başarıyla eklendi." + Style.RESET_ALL)
            return Fis.fis_menu()
            print(str(temp_dolu_kantar) + " kg")
        if choose == "3":
                try:
                    Fis.mal_liste[0]
                except:
                    print(Fore.RED + "Hiç mal bulunamadı.")
                    return Fis.fis_menu()
            
                print("Mal Listesi:")
                for i in Fis.mal_liste:
                    print(f"{Fis.mal_liste.index(i)+1}. {i.cins}, Kantar Fark: {i.kantar_fark}, Adet {i.adet}")
                delete_item = limit_input("Lütfen silinecek malın kodunu giriniz(Çıkmak için '0'):  ", str_range(Fis.mal_liste.index(Fis.mal_liste[-1])+2))
                if delete_item == '0':
                    return Fis.fis_menu()
                else:
                    temp_cins = Fis.mal_liste[int(delete_item)-1].cins
                    Fis.mal_liste.pop(int(delete_item)-1)
                    print(Fore.RED + f"{delete_item} ID'li {temp_cins} malı başarıyla silindi." + Style.RESET_ALL)
                    return Fis.fis_menu()
        if choose == "4":
            if Fis.mal_liste == []:
                print("Yazdırmadan önce ürün girmelisiniz.")
                return Fis.fis_menu()
            yazdir(Fis.gecerli_musthasil,Fis.mal_liste)
            Fis.mal_liste = []
            return Menu.main_menu()
        if choose == "0":
            Fis.mal_liste = []
            print(Fore.RED + "Fiş Başarıyla İptal Edildi.")
            return Menu.main_menu()
        

class Mal:
    def __init__(self,sahip,cins,kasa,dolu_kantar,bos_kantar,adet):
        self.sahip = sahip
        self.cins = cins
        self.kasa = kasa
        self.bos_kantar = bos_kantar
        self.dolu_kantar = dolu_kantar
        self.kantar_fark = dolu_kantar - bos_kantar
        self.adet = adet



Menu.main_menu()