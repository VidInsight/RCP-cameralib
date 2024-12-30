import os

from src.modules.camera_manager import CameraManager
from src.modules.config_handler import ConfigHandler

def main():
    # CameraManager oluştur
    custom_config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.yaml')
    camera_manager = CameraManager(config_path=custom_config_path)

    # Kamerayı bağla
    connect_result = camera_manager.connect()
    if not connect_result["success"]:
        print(f"Kamera bağlantısı başarısız: {connect_result['message']}")
        return

    print(f"Kamera bağlandı: {connect_result['data']}")

    # ConfigHandler örneği oluştur
    config_handler = ConfigHandler(camera_manager)

    # Tek bir ayarın değerini alma
    print("\n--- Tek Ayar Değeri Alma ---")
    iso_setting = "iso"
    iso_result = config_handler.get_config_value(iso_setting)
    if iso_result["success"]:
        print(f"{iso_setting.upper()} mevcut değeri: {iso_result['data']['value']}")
    else:
        print(f"{iso_setting.upper()} ayarı alınamadı: {iso_result['message']}")

    # Birden fazla ayarın değerini alma
    print("\n--- Çoklu Ayar Değerleri Alma ---")
    settings_to_get = {
        'iso': None, 
        'aperture': None, 
        'shutter_speed': None,
        'white_balance': None
    }
    multiple_results = config_handler.get_multiple_config_values(settings_to_get)
    for setting, result in multiple_results.items():
        if result['success']:
            print(f"{setting.upper()} değeri: {result['data']['value']}")
        else:
            print(f"{setting.upper()} ayarı alınamadı: {result['message']}")

    # Tek bir ayarı ayarlama
    print("\n--- Tek Ayar Değeri Ayarlama ---")
    new_iso_value = '400'
    set_iso_result = config_handler.set_single_config(iso_setting, new_iso_value)
    if set_iso_result["success"]:
        print(f"{iso_setting.upper()} değeri {new_iso_value} olarak ayarlandı.")
    else:
        print(f"{iso_setting.upper()} ayarlanamadı: {set_iso_result['message']}")

    # Çoklu ayar ayarlama
    print("\n--- Çoklu Ayar Değerleri Ayarlama ---")
    settings_to_set = {
        'iso': '200',
        'aperture': '5.6',
        'shutter_speed': '1/250',
        'white_balance': 'Auto'
    }
    multiple_set_results = config_handler.set_multiple_configs(settings_to_set)
    for setting, result in multiple_set_results.items():
        if result['success']:
            print(f"{setting.upper()} değeri {settings_to_set[setting]} olarak ayarlandı.")
        else:
            print(f"{setting.upper()} ayarlanamadı: {result['message']}")

    # Var olmayan bir ayarı alma denemesi
    print("\n--- Var Olmayan Ayar Denemesi ---")
    non_existent_setting = "non_existent_setting"
    non_existent_result = config_handler.get_config_value(non_existent_setting)
    if not non_existent_result["success"]:
        print(f"Beklenen hata - Var olmayan ayar: {non_existent_result['message']}")

if __name__ == "__main__":
    main()
