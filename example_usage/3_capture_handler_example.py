import os

from src.modules.camera_manager import CameraManager
from src.modules.capture_handler import CaptureHandler

def main():
    # Özel yapılandırma dosyası yolu
    custom_config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.yaml')
    
    # CameraManager ve CaptureHandler örneklerini oluştur
    camera_manager = CameraManager(config_path=custom_config_path)
    capture_handler = CaptureHandler(camera_manager)

    try:
        # Kamerayı bağla
        connect_result = camera_manager.connect()
        if not connect_result["success"]:
            print(f"Kamera bağlantısı başarısız: {connect_result['message']}")
            return

        print(f"Kamera bağlandı: {connect_result['data']}")

        # Kameranın hazır olmasını bekle
        print("\n--- Kamera Hazırlık Kontrolü ---")
        if not capture_handler.wait_until_ready():
            print("Kamera hazır değil. İşlem sonlandırılıyor...")
            return

        # Görüntü yakalama
        print("\n--- Görüntü Yakalama ---")
        # Varsayılan kaydetme yolu kullanılacak
        image_result = capture_handler.capture_image()
        if image_result["success"]:
            print(f"Görüntü kaydedildi: {image_result['data']['save_path']}")
        else:
            print(f"Görüntü yakalama başarısız: {image_result['message']}")

        # Özel kaydetme yolu ile görüntü yakalama
        custom_save_path = os.path.join(os.path.dirname(__file__), 'custom_capture.jpg')
        print("\n--- Özel Kaydetme Yolu ile Görüntü Yakalama ---")
        custom_image_result = capture_handler.capture_image(save_path=custom_save_path)
        if custom_image_result["success"]:
            print(f"Özel konuma görüntü kaydedildi: {custom_image_result['data']['save_path']}")
        else:
            print(f"Özel konuma görüntü yakalama başarısız: {custom_image_result['message']}")

        # Önizleme yakalama
        print("\n--- Önizleme Yakalama ---")
        preview_result = capture_handler.capture_preview()
        if preview_result["success"]:
            print(f"Önizleme kaydedildi: {preview_result['data']['save_path']}")
        else:
            print(f"Önizleme yakalama başarısız: {preview_result['message']}")

        # Özel kaydetme yolu ile önizleme yakalama
        custom_preview_path = os.path.join(os.path.dirname(__file__), 'custom_preview.jpg')
        print("\n--- Özel Kaydetme Yolu ile Önizleme Yakalama ---")
        custom_preview_result = capture_handler.capture_preview(save_path=custom_preview_path)
        if custom_preview_result["success"]:
            print(f"Özel konuma önizleme kaydedildi: {custom_preview_result['data']['save_path']}")
        else:
            print(f"Özel konuma önizleme yakalama başarısız: {custom_preview_result['message']}")

    except Exception as e:
        print(f"Beklenmeyen bir hata oluştu: {e}")

    finally:
        # Kamerayı bağlantısını kes
        disconnect_result = camera_manager.disconnect_camera()
        if not disconnect_result["success"]:
            print(f"Kamera bağlantısı kesilirken hata oluştu: {disconnect_result['message']}")

if __name__ == "__main__":
    main()