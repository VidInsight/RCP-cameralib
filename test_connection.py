import subprocess

class GPhoto2Camera:
    @staticmethod
    def list_ports():
        """
        List all available ports for camera connections.
        """
        try:
            result = subprocess.run([
                "gphoto2", "--list-ports"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            if result.returncode != 0:
                raise RuntimeError(f"Error listing ports: {result.stderr.strip()}")

            return result.stdout.strip()
        except FileNotFoundError:
            raise FileNotFoundError("gPhoto2 is not installed or not in PATH.")

    @staticmethod
    def get_camera_summary():
        """
        Get the summary of the connected camera.
        """
        try:
            result = subprocess.run([
                "gphoto2", "--summary"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            if result.returncode != 0:
                raise RuntimeError(f"Error retrieving camera summary: {result.stderr.strip()}")

            return result.stdout.strip()
        except FileNotFoundError:
            raise FileNotFoundError("gPhoto2 is not installed or not in PATH.")

    @staticmethod
    def disconnect_camera():
        """
        Disconnect the currently connected camera.
        """
        try:
            result = subprocess.run([
                "gphoto2", "--reset"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            if result.returncode != 0:
                raise RuntimeError(f"Error disconnecting the camera: {result.stderr.strip()}")

            return "Camera disconnected successfully."
        except FileNotFoundError:
            raise FileNotFoundError("gPhoto2 is not installed or not in PATH.")

if __name__ == "__main__":
    try:
        # List available ports
        print("Listing available ports...")
        ports = GPhoto2Camera.list_ports()
        print(ports)

        # Get camera summary
        print("\nRetrieving camera summary...")
        summary = GPhoto2Camera.get_camera_summary()
        print(summary)

        # Disconnect the camera
        print("\nDisconnecting the camera...")
        disconnect_message = GPhoto2Camera.disconnect_camera()
        print(disconnect_message)
    except Exception as e:
        print(f"Error: {e}")
