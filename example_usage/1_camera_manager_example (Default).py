import os
from src.modules.camera_manager import CameraManager

def main():
    # Varsayılan yapılandırmayı kullanarak CameraManager örneği oluştur
    print("Default Configuration Example:")
    camera_manager_default = CameraManager()

    # Kamera tespiti ve bağlanma (varsayılan yapılandırma ile)
    connect_result_default = camera_manager_default.connect()
    if connect_result_default["success"]:
        print(f"Camera connected using default config: {connect_result_default['data']}")
    else:
        print(f"Failed to connect with default config: {connect_result_default['message']}")

    # Kameranın özetini al
    summary_result = camera_manager_default.get_camera_summary()
    if summary_result["success"]:
        print(f"\nCamera summary:\n{summary_result['data']['summary']}")
    else:
        print(f"Failed to get camera summary: {summary_result['message']}")

    # Kamerayı resetleme
    reset_result = camera_manager_default.reset_camera()
    if reset_result["success"]:
        print("\nCamera reset successfully.")
    else:
        print(f"Failed to reset camera: {reset_result['message']}")

    # Kamera bağlantısını kesme
    disconnect_result = camera_manager_default.disconnect_camera()
    if disconnect_result["success"]:
        print("\nCamera disconnected successfully.")
    else:
        print(f"Failed to disconnect camera: {disconnect_result['message']}")

if __name__ == "__main__":
    main()
