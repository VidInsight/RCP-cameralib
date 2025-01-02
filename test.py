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


    # Birden fazla ayarın değerini alma
    print("\n--- Çoklu Ayar Değerleri Alma ---")
    settings_to_get = {
        'iso': None,
        'aperture': None,
        'shutterspeed': None,
        'whitebalance': None
    }
    multiple_results = config_handler.get_multiple_config_values(settings_to_get)
    print(multiple_results)

    for setting, result in multiple_results.items():
        if result['success']:
            print(f"{setting.upper()} değeri: {result['data']['value']}")
        else:
            print(f"{setting.upper()} ayarı alınamadı: {result['message']}")




if __name__ == "__main__":
    main()
