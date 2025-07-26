import asyncio
import websockets
import serial
import serial.tools.list_ports
import json

# --- AYARLAR ---
# Bilgisayarınızdaki Aygıt Yöneticisi'nden doğru COM portunu bulun ve buraya yazın.
# Windows'ta genellikle 'COM3', 'COM4' gibi bir isim alır.
# Eğer doğru portu bulamazsanız, program otomatik olarak bulmaya çalışacaktır.
SERIAL_PORT = 'COM3' 
# A12E indikatör dökümanındaki varsayılan baud rate (P2 parametresi).
# İndikatör üzerinden bu ayarı değiştirdiyseniz, burayı da güncelleyin.
BAUD_RATE = 1200  
WEBSOCKET_HOST = 'localhost'
WEBSOCKET_PORT = 5678

# Bağlı olan tüm WebSocket istemcilerini (web sayfalarını) tutan set.
connected_clients = set()

def find_serial_port():
    """Mevcut seri portları listeler ve USB-to-Serial adaptörünü otomatik bulmaya çalışır."""
    ports = serial.tools.list_ports.comports()
    print("Mevcut seri portlar:")
    if not ports:
        print("-> Hiç seri port bulunamadı. Lütfen kantarın bağlı olduğundan emin olun.")
        return None
    for port in ports:
        print(f"-> {port.device}: {port.description}")
    
    # Genellikle USB-to-Serial adaptörleri bu isimlerden birini içerir.
    for port in ports:
        if "CH340" in port.description or "USB-SERIAL" in port.description or "Prolific" in port.description:
            print(f"\n>> Otomatik olarak '{port.device}' portu seçildi.")
            return port.device
            
    print(f"\n>> Otomatik port bulunamadı. Varsayılan port ({SERIAL_PORT}) kullanılacak.")
    return SERIAL_PORT


def parse_indicator_data(data_string):
    """
    A12E indikatöründen gelen 15 byte'lık veriyi ayrıştırır.
    Örnek Formatlar: 'W G   4.139kg...', 'OL', 'LO'
    Dökümana göre veri formatı: [Durum(1)][Tip(1)][Ağırlık(7)][Birim(2)][Checksum(2)][CR][LF]
    """
    try:
        # Gelen veriyi temizle
        data_string = data_string.strip()
        
        # Aşırı yük veya düşük yük durumlarını kontrol et
        if 'OL' in data_string:
            return "Overload"
        if 'LO' in data_string:
            return "Underload"

        # Sadece sayısal ve ondalık ayırıcı karakterleri alarak ağırlığı bul
        weight_str = ''.join(filter(lambda x: x.isdigit() or x == '.' or x == '-', data_string))
        
        if weight_str:
            return float(weight_str)
        return None
    except (ValueError, IndexError) as e:
        print(f"Veri ayrıştırma hatası: {e} - Gelen Ham Veri: '{data_string}'")
        return None

async def serial_reader():
    """Seri porttan sürekli veri okur ve bağlı olan tüm web istemcilerine gönderir."""
    
    port_to_use = find_serial_port()
    if not port_to_use:
        print("\nKantar portu bulunamadı. Lütfen kantarınızı bağlayıp programı yeniden başlatın.")
        return

    while True:
        try:
            with serial.Serial(port_to_use, BAUD_RATE, timeout=1) as ser:
                print(f"\n>> '{port_to_use}' portu {BAUD_RATE} baud rate ile dinleniyor...")
                print(">> Web sayfası artık kantardan veri alabilir.")
                
                while True:
                    # İndikatörden bir satır veri oku (ASCII olarak)
                    line = ser.readline().decode('ascii', errors='ignore')
                    
                    if line and connected_clients:
                        weight = parse_indicator_data(line)
                        
                        if weight is not None:
                            # Anlık okunan ağırlığı konsola yazdır
                            print(f"Okunan Ağırlık: {weight}", end='\r')
                            
                            # Veriyi JSON formatında hazırla
                            message = json.dumps({'type': 'weight_update', 'weight': weight})
                            
                            # WebSocket üzerinden bağlı tüm istemcilere (web sayfalarına) gönder
                            # asyncio.gather, tüm gönderme işlemlerini eşzamanlı yapar
                            await asyncio.gather(
                                *[client.send(message) for client in connected_clients]
                            )

        except serial.SerialException as e:
            print(f"\nSeri port hatası: {e}")
            print("5 saniye içinde yeniden bağlanmaya çalışılacak...")
            await asyncio.sleep(5)
        except Exception as e:
            print(f"\nBeklenmedik bir hata oluştu: {e}")
            await asyncio.sleep(5)


async def handler(websocket, path):
    """Yeni WebSocket bağlantılarını yönetir."""
    # Yeni istemciyi (web sayfasını) listeye ekle
    connected_clients.add(websocket)
    print(f"\n>> Yeni bir web sayfası bağlandı. Toplam bağlantı: {len(connected_clients)}")
    try:
        # İstemci bağlantısı açık olduğu sürece bekle
        await websocket.wait_closed()
    finally:
        # İstemci bağlantısı kapandığında listeden kaldır
        connected_clients.remove(websocket)
        print(f"\n>> Bir web sayfası bağlantısı koptu. Kalan bağlantı: {len(connected_clients)}")


async def main():
    """Ana program fonksiyonu. WebSocket sunucusunu ve seri port okuyucuyu başlatır."""
    # WebSocket sunucusunu başlat
    server = await websockets.serve(handler, WEBSOCKET_HOST, WEBSOCKET_PORT)
    print(f">> WebSocket sunucusu ws://{WEBSOCKET_HOST}:{WEBSOCKET_PORT} adresinde çalışıyor.")
    
    # Seri port okuyucusunu ayrı bir görev olarak başlat
    asyncio.create_task(serial_reader())
    
    # Sunucu kapanana kadar bekle
    await server.wait_closed()

if __name__ == "__main__":
    print("--- Kantar Agent Başlatılıyor ---")
    print("İndikatör ayarlarından P4'ün 'sürekli iletim' (2) veya 'sabitken iletim' (3) modunda olduğundan emin olun.")
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nProgram kapatılıyor.")
