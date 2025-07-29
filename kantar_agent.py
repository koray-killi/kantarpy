import asyncio
import websockets
import serial
import serial.tools.list_ports
import json

# --- Varsayılan Ayarlar (İstemciden yeni ayar gelmezse kullanılır) ---
DEFAULT_SERIAL_PORT = 'COM3'
DEFAULT_BAUD_RATE = 1200
WEBSOCKET_HOST = 'localhost'
WEBSOCKET_PORT = 5678

connected_clients = set()

def parse_indicator_data(data_string):
    """A12E indikatöründen gelen veriyi ayrıştırır."""
    try:
        data_string = data_string.strip()
        if 'OL' in data_string: return "Overload"
        if 'LO' in data_string: return "Underload"
        weight_str = ''.join(filter(lambda x: x.isdigit() or x == '.' or x == '-', data_string))
        if weight_str:
            return float(weight_str)
        return None
    except (ValueError, IndexError):
        return None

async def broadcast(message):
    """Mesajı bağlı olan tüm istemcilere gönderir."""
    if connected_clients:
        await asyncio.gather(*[client.send(message) for client in connected_clients])

async def serial_reader(config):
    """Verilen yapılandırmaya göre seri portu dinler."""
    port_to_use = config.get('port', DEFAULT_SERIAL_PORT)
    baud_rate = config.get('baud', DEFAULT_BAUD_RATE)
    
    print(f"Alınan ayarlar ile bağlanılıyor: Port={port_to_use}, Baud Rate={baud_rate}")

    try:
        with serial.Serial(port_to_use, baud_rate, timeout=1) as ser:
            print(f"Başarıyla bağlandı: {ser.name}")
            await broadcast(json.dumps({'type': 'status', 'message': 'Kantar Bağlandı', 'status': 'connected'}))
            
            while True:
                try:
                    line = ser.readline().decode('ascii', errors='ignore')
                    if line:
                        weight = parse_indicator_data(line)
                        if weight is not None:
                            # print(f"Okunan Ağırlık: {weight}", end='\r')
                            await broadcast(json.dumps({'type': 'weight_update', 'weight': weight}))
                except serial.SerialException as e:
                    print(f"Okuma sırasında hata: {e}")
                    break # Döngüden çıkıp yeniden bağlantı denenmesini sağla
    except serial.SerialException as e:
        print(f"Seri porta bağlanılamadı: {e}")
        await broadcast(json.dumps({'type': 'status', 'message': f'Porta Bağlanamadı: {port_to_use}', 'status': 'error'}))
    except Exception as e:
        print(f"Beklenmedik bir hata: {e}")


async def handler(websocket, path):
    """Yeni WebSocket bağlantılarını ve gelen mesajları yönetir."""
    connected_clients.add(websocket)
    print(f"Yeni istemci bağlandı. Toplam: {len(connected_clients)}")
    
    try:
        # İstemciden ilk yapılandırma mesajını bekle
        config_message = await websocket.recv()
        config = json.loads(config_message)
        
        if config.get('type') == 'configure':
            # Yapılandırma alındıktan sonra seri okuyucuyu başlat
            asyncio.create_task(serial_reader(config.get('settings', {})))
        
        # Bağlantı açık olduğu sürece bekle
        await websocket.wait_closed()
        
    except websockets.exceptions.ConnectionClosed:
        print("İstemci bağlantısı kapandı.")
    finally:
        connected_clients.remove(websocket)
        print(f"İstemci ayrıldı. Kalan: {len(connected_clients)}")


async def main():
    print("--- Kantar Agent Başlatılıyor ---")
    print("İndikatör ayarlarından P4'ün 'sürekli iletim' (2) veya 'sabitken iletim' (3) modunda olduğundan emin olun.")
    
    async with websockets.serve(handler, WEBSOCKET_HOST, WEBSOCKET_PORT):
        print(f"WebSocket sunucusu ws://{WEBSOCKET_HOST}:{WEBSOCKET_PORT} adresinde çalışıyor.")
        await asyncio.Future()  # Sunucuyu sonsuza kadar çalıştır

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nProgram kapatılıyor.")
