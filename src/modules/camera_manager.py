import gphoto2 as gp
from typing import Optional, List, Dict
import yaml
import os

from src.utils.rcp_logger import Logger
from src.utils.utils import *
from src.utils.gphoto_errors import GPhotoErrorInterpreter

class CameraManager:
    def __init__(self, config_path: Optional[str] = None):
        # Initialize logger
        self.__logger = Logger.get_logger("Camera Manager")
        self.__logger.debug('Camera Manager logger has been initialized')

        # Load configuration
        self.__config = self.__load_config(config_path)
        
        # Initialize GPhoto2 context
        self.__context = gp.Context()
        self.__logger.debug('GPhoto2 context has been created')

        # Camera-related attributes
        self.__camera: Optional[gp.Camera] = None
        self.__connected_camera_info: Optional[Dict[str, str]] = None
        self.__available_cameras: List[Dict[str, str]] = []

    def __load_config(self, config_path: Optional[str] = None) -> Dict:
        """
        Load configuration from YAML file.
        
        :param config_path: Path to the configuration file. If None, uses default path.
        :return: Loaded configuration dictionary
        """
        default_config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config.yaml')
        config_file = config_path or default_config_path

        try:
            with open(config_file, 'r') as file:
                config = yaml.safe_load(file)
                self.__logger.info(f"Configuration loaded from {config_file}")
                return config
        except FileNotFoundError:
            self.__logger.warning(f"Configuration file not found at {config_file}. Using default settings.")
            return {}
        except yaml.YAMLError as e:
            self.__logger.error(f"Error parsing configuration file: {e}")
            return {}

    def __del__(self):
        """Destructor to clean up the CameraManager resources."""
        if self.__camera:
            self.disconnect_camera()
        self.__logger.debug('CameraManager instance is being destroyed.')

    def __detect_cameras(self) -> bool:
        method_name = "detect_cameras"
        self.__logger.debug(f'[{method_name}] Starting camera detection')

        try:
            camera_list = gp.Camera.autodetect(self.__context)
            camera_count = len(camera_list)
            
            # Sanitized logging
            self.__logger.info(f'[{method_name}] Detected {camera_count} camera(s)')

            if camera_list:
                # Log camera names without sensitive details
                camera_names = [name for name, _ in camera_list]
                self.__logger.debug(f'[{method_name}] Camera names: {", ".join(camera_names)}')
                
                for name, path in camera_list:
                    self.__available_cameras.append({"name": name, "port": path})
                
                return True
            else:
                self.__logger.warning(f'[{method_name}] No cameras detected')
                return False

        except gp.GPhoto2Error as e:
            self.__logger.error(f'[{method_name}] GPhoto2 detection error: {e}')
            return False
        except Exception as e:
            self.__logger.error(f'[{method_name}] Unexpected detection error: {e}')
            return False

    def __connect_camera(self, port: Optional[str] = None) -> bool:
        """Connects to a camera on the specified port."""
        if not self.__available_cameras:
            self.__logger.warning('No cameras available to connect')
            return False

        try:
            selected_camera_info = None
            if port:
                # Find camera with the specified port
                selected_camera_info = next((cam for cam in self.__available_cameras if cam['port'] == port), None)
                if not selected_camera_info:
                    self.__logger.warning(f"No camera found on port '{port}', attempting to connect to the first available camera")
                    selected_camera_info = self.__available_cameras[0]
            else:
                selected_camera_info = self.__available_cameras[0]

            self.__logger.debug(f"Selected camera: {selected_camera_info['name']} at port: {selected_camera_info['port']}")

            # Initialize the camera
            self.__camera = gp.Camera()
            self.__camera.init(self.__context)
            self.__connected_camera_info = selected_camera_info
            self.__logger.info(f'Connected to camera: {selected_camera_info["name"]} at port: {selected_camera_info["port"]}')
            return True

        except gp.GPhoto2Error as e:
            self.__logger.error(f"Error: Unable to connect to the camera. {e}")
            self.__camera = None
            self.__connected_camera_info = None
            return False
        except Exception as e:
            self.__logger.error(f"Unknown error during camera connection: {e}")
            self.__camera = None
            self.__connected_camera_info = None
            return False

    def disconnect_camera(self) -> Dict:
        """Disconnects the currently connected camera."""
        if self.__camera:
            try:
                self.__camera.exit(self.__context)
                self.__logger.info("Camera disconnected.")
                return sdict(True, message="Camera disconnected.")
            except gp.GPhoto2Error as e:
                self.__logger.error(f"Error during camera disconnection: {e}")
                return sdict(False, message=f"Error during disconnection: {e}")
            finally:
                self.__camera = None
                self.__connected_camera_info = None
        return sdict(False, message="No camera to disconnect.")

    def reset_camera(self) -> Dict:
        """Resets the camera connection."""
        if self.__camera:
            self.__logger.debug("Resetting camera: disconnecting existing connection")
            self.disconnect_camera()
        self.__logger.debug("Attempting to reconnect the camera")
        success = self.__connect_camera()
        return sdict(success, message="Camera reset successfully." if success else "Failed to reset camera.")

    def get_camera_summary(self) -> Dict:
        """Tests the camera connection by retrieving its summary."""
        self.__logger.debug('Getting camera summary')

        if not self.__connected_camera_info:
            self.__logger.warning('No camera connected to test')
            return sdict(False, message="No camera connected.")

        try:
            summary = self.__camera.get_summary(self.__context)
            self.__logger.info(f"Camera connected at port: {self.__connected_camera_info['port']}")
            return sdict(True, data={"summary": summary}, message="Camera summary retrieved.")
        except gp.GPhoto2Error as e:
            self.__logger.error(f"Error: Unable to retrieve camera summary: {e}")
            return sdict(False, message=f"Error: {e}")
        except Exception as e:
            self.__logger.error(f"Unknown error during connection test: {e}")
            return sdict(False, message=f"Unknown error: {e}")

    def send_signal(self) -> Dict:
        method_name = "send_signal"
        try:
            if not self.__camera:
                self.__logger.warning(f'[{method_name}] No camera connected')
                return sdict(False, message="No camera connected")

            config = self.__camera.get_config()
            
            # More robust signal handling
            try:
                action = config.get_child_by_name("eosremoterelease")
                if action:
                    action.set_value('Press Full')
                    self.__camera.set_config(config)
                    self.__logger.info(f'[{method_name}] Signal sent successfully')
                    return sdict(True, message="Camera signal sent")
                else:
                    self.__logger.warning(f'[{method_name}] No remote release action found')
                    return sdict(False, message="Remote release not supported")
            
            except Exception as config_error:
                self.__logger.error(f'[{method_name}] Configuration error: {config_error}')
                return sdict(False, message=f"Configuration error: {config_error}")

        except gp.GPhoto2Error as e:
            error_interpreter = GPhotoErrorInterpret1er(e)
            self.__logger.error(f'[{method_name}] GPhoto2 signal error: {error_interpreter.get_error_message()}')
            return sdict(False, message=f"Camera signal error: {error_interpreter.get_error_message()}")
        except Exception as e:
            self.__logger.error(f'[{method_name}] Unexpected signal error: {e}')
            return sdict(False, message="Unexpected error during signal sending")

    def connect(self, camera_name: Optional[str] = None) -> Dict:
        """
        Attempts to detect and connect to a camera.

        :param camera_name: Optional. The name of the camera to connect to.
        :return: A dictionary with the success status and details of the connected camera.
        """
        self.__logger.debug('Starting camera connection process')

        # Detect cameras
        if not self.__detect_cameras():
            error_message = 'Camera detection failed or no cameras found'
            self.__logger.error(error_message)
            return sdict(False, message=error_message)

        selected_camera_info = None

        # Select a specific camera if name is provided
        if camera_name:
            self.__logger.debug(f"Looking for camera named '{camera_name}'")
            selected_camera_info = next((cam for cam in self.__available_cameras if cam['name'] == camera_name), None)
            if not selected_camera_info:
                warning_message = f"No camera found with name '{camera_name}', switching to auto mode"
                self.__logger.warning(warning_message)
                selected_camera_info = self.__available_cameras[0]
        elif self.__config.get('camera', {}).get('name'):
            camera_name = self.__config['camera']['name']
            self.__logger.debug(f"Using camera name from config: {camera_name}")
            selected_camera_info = next((cam for cam in self.__available_cameras if cam['name'] == camera_name), None)
            if not selected_camera_info:
                warning_message = f"No camera found with name '{camera_name}', switching to auto mode"
                self.__logger.warning(warning_message)
                selected_camera_info = self.__available_cameras[0]
        else:
            selected_camera_info = self.__available_cameras[0]

        # Connect to the selected camera
        self.__logger.debug(f"Connecting to camera: {selected_camera_info['name']} at port: {selected_camera_info['port']}")
        if not self.__connect_camera(port=selected_camera_info['port']):
            error_message = f"Failed to connect to camera: {selected_camera_info['name']}"
            self.__logger.error(error_message)
            return sdict(False, message=error_message)

        self.__logger.info(f"Successfully connected to camera: {selected_camera_info['name']} at port: {selected_camera_info['port']}")
        return sdict(True, data={"camera_name": selected_camera_info['name'], "port": selected_camera_info['port']}, message="Camera connected successfully.")

    def get_camera(self) -> Optional[gp.Camera]:
        """Provides access to the current camera instance."""
        return self.__camera

    def get_config(self) -> Dict:
        """
        Retrieve the loaded configuration.
        If configuration loading failed, returns a default configuration.

        :return: Dictionary containing the loaded configuration or default configuration
        """
        # If configuration is empty or None, return a default configuration
        if not self.__config:
            default_config = {
                'camera': {
                    'name': 'Default Camera',
                    'connection_timeout': 10
                },
                'capture': {
                    'save_directory': './images',
                    'preview_directory': './previews',
                    'retry_attempts': 3,
                    'retry_delay': 1
                },
                'log_settings': {
                    'console_level': 'ERROR',
                    'file_level': 'DEBUG'
                }
            }
            self.__logger.warning("Using default configuration as no config was loaded.")
            return default_config
        
        return self.__config
