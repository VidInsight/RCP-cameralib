import os
from src.modules.camera_manager import CameraManager

def main():
    # Özel bir yapılandırma dosyası kullanarak CameraManager örneği oluştur
    print("\nCustom Configuration Example:")
    # Proje dizinindeki config.yaml dosyasını kullan
    custom_config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.yaml')
    camera_manager_custom = CameraManager(config_path=custom_config_path)

    # Kamera tespiti ve bağlanma (özel yapılandırma ile)
    connect_result_custom = camera_manager_custom.connect()
    if connect_result_custom["success"]:
        print(f"Camera connected using custom config: {connect_result_custom['data']}")
    else:
        print(f"Failed to connect with custom config: {connect_result_custom['message']}")

    # Kameranın özetini al
    summary_result = camera_manager_custom.get_camera_summary()
    if summary_result["success"]:
        print(f"\nCamera summary:\n{summary_result['data']['summary']}")
    else:
        print(f"Failed to get camera summary: {summary_result['message']}")

    camera_manager_custom.send_signal()

    # Kamerayı resetleme
    reset_result = camera_manager_custom.reset_camera()
    if reset_result["success"]:
        print("\nCamera reset successfully.")
    else:
        print(f"Failed to reset camera: {reset_result['message']}")

    # Kamera bağlantısını kesme
    disconnect_result = camera_manager_custom.disconnect_camera()
    if disconnect_result["success"]:
        print("\nCamera disconnected successfully.")
    else:
        print(f"Failed to disconnect camera: {disconnect_result['message']}")


if __name__ == "__main__":
    main()
