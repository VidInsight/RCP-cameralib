import time
import os
import gphoto2 as gp
from typing import Optional

from src.modules.camera_manager import CameraManager
from src.utils.rcp_logger import Logger
from src.utils.utils import *
from src.utils.gphoto_errors import GPhotoErrorInterpreter

class CaptureHandler:
    def __init__(self, camera_manager: CameraManager):
        """
        Initialize CaptureHandler using configuration from CameraManager.

        :param camera_manager: CameraManager instance
        """
        self.__camera_manager = camera_manager
        self.__logger = Logger.get_logger("Capture Handler")
        
        # Retrieve configuration directly from CameraManager
        try:
            self.__config = camera_manager.get_config()
            
            # Set capture settings from configuration
            self.__save_directory = self.__config.get('capture', {}).get('save_directory', './images')
            self.__preview_directory = self.__config.get('capture', {}).get('preview_directory', './previews')
            self.__retry_attempts = self.__config.get('capture', {}).get('retry_attempts', 3)
            self.__retry_delay = self.__config.get('capture', {}).get('retry_delay', 1)

            # Ensure save directories exist
            try:
                os.makedirs(self.__save_directory, exist_ok=True)
                os.makedirs(self.__preview_directory, exist_ok=True)
            except OSError as e:
                self.__logger.error(f"Failed to create save directories: {e}")
                # Fallback to current directory if directory creation fails
                self.__save_directory = '.'
                self.__preview_directory = '.'

        except Exception as e:
            # Fallback to default settings if configuration retrieval fails
            self.__logger.error(f"Failed to load configuration: {e}")
            
            # Default settings
            self.__save_directory = './images'
            self.__preview_directory = './previews'
            self.__retry_attempts = 3
            self.__retry_delay = 1

            # Try to create directories, but don't fail if it doesn't work
            try:
                os.makedirs(self.__save_directory, exist_ok=True)
                os.makedirs(self.__preview_directory, exist_ok=True)
            except OSError:
                self.__save_directory = '.'
                self.__preview_directory = '.'

    def capture_image(self, save_path: Optional[str] = None) -> dict:
        """
        Capture an image with configurable save path and retry mechanism.

        :param save_path: Optional custom save path. If not provided, uses config or default.
        :return: Dictionary with capture result
        """
        method_name = "capture_image"
        self.__logger.debug(f'[{method_name}] Initiating image capture')

        # Comprehensive connection check
        if not self.__camera_manager.get_camera():
            error_message = "No camera connected for image capture"
            self.__logger.error(f'[{method_name}] {error_message}')
            return sdict(False, message=error_message)

        # Intelligent save path generation
        if not save_path:
            timestamp = time.strftime('%Y%m%d_%H%M%S')
            filename = f"capture_{timestamp}.jpg"
            save_path = os.path.join(self.__save_directory, filename)
            self.__logger.debug(f'[{method_name}] Generated save path: {save_path}')

        # Retry mechanism with detailed logging
        for attempt in range(self.__retry_attempts):
            try:
                self.__logger.info(f'[{method_name}] Capture attempt {attempt + 1}/{self.__retry_attempts}')
                
                file_path = self.__camera_manager.get_camera().capture(gp.GP_CAPTURE_IMAGE)
                self.__logger.debug(f'[{method_name}] Camera captured image at: {file_path.folder}/{file_path.name}')

                return sdict(True, message="Success")

                """
                download_result = self._download_image(file_path, save_path)
                
                if download_result["success"]:
                    self.__logger.info(f'[{method_name}] Image capture successful: {save_path}')
                    return download_result
                """

                self.__logger.warning(f'[{method_name}] Download failed, retrying in {self.__retry_delay} seconds')
                time.sleep(self.__retry_delay)

            except gp.GPhoto2Error as e:
                error_message = GPhotoErrorInterpreter.interpret_error(e)
                self.__logger.warning(f'[{method_name}] {error_message}')
                time.sleep(self.__retry_delay)

        # Final failure logging
        error_message = f"Failed to capture image after {self.__retry_attempts} attempts"
        self.__logger.error(f'[{method_name}] {error_message}')
        return sdict(False, message=error_message)

    def capture_preview(self, save_path: Optional[str] = None) -> dict:
        """
        Capture a preview image with configurable save path.

        :param save_path: Optional custom save path. If not provided, uses config or default.
        :return: Dictionary with preview capture result
        """
        method_name = "capture_preview"
        self.__logger.debug(f'[{method_name}] Starting preview capture')

        if not self.__camera_manager.get_camera():
            error_message = "No camera is connected. Please connect a camera before capturing a preview."
            self.__logger.error(f'[{method_name}] {error_message}')
            return sdict(False, message=error_message)

        # Use provided save_path or generate one based on configuration
        if not save_path:
            filename = f"preview_{time.strftime('%Y%m%d_%H%M%S')}.jpg"
            save_path = os.path.join(self.__preview_directory, filename)
            self.__logger.debug(f'[{method_name}] Generated preview save path: {save_path}')

        try:
            # Capture the preview and store it in a CameraFile object
            camera_file = gp.CameraFile()
            self.__camera_manager.get_camera().capture_preview(camera_file)
            self.__logger.info(f'[{method_name}] Preview image captured')

            camera_file.save(save_path)
            self.__logger.info(f'[{method_name}] Preview image saved locally at: {save_path}')
            return sdict(True, data={"save_path": save_path}, message="Preview captured and saved successfully.")

        except gp.GPhoto2Error as e:
            error_message = GPhotoErrorInterpreter.interpret_error(e)
            self.__logger.error(f'[{method_name}] {error_message}')
            return sdict(False, message=error_message)
        except Exception as e:
            error_message = f"Unexpected error during preview capture: {e}"
            self.__logger.error(f'[{method_name}] {error_message}')
            return sdict(False, message=error_message)

    def wait_until_ready(self, timeout: Optional[int] = None) -> bool:
        """
        Wait until the camera is ready, with a configurable timeout.

        :param timeout: Maximum time to wait in seconds. Uses config value if not provided.
        :return: Boolean indicating if camera is ready
        """
        # Use provided timeout or get from config, with a default fallback
        if timeout is None:
            timeout = self.__config.get('camera', {}).get('connection_timeout', 10)

        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                self.__camera_manager.get_camera().get_config()  # Test connection
                return True
            except gp.GPhoto2Error as e:
                error_message = GPhotoErrorInterpreter.interpret_error(e)
                self.__logger.warning(f"Camera not ready, retrying... {error_message}")
                time.sleep(0.5)
        self.__logger.error("Camera not ready after waiting.")
        return False

    def _download_image(self, file_path: gp.CameraFilePath, save_path: str) -> dict:
        """
        Download an image from the camera to a local path.

        :param file_path: Camera file path
        :param save_path: Local save path
        :return: Dictionary with download result
        """
        self.__logger.debug(f"Downloading image from {file_path.folder}/{file_path.name} to {save_path}")

        try:
            camera_file = gp.CameraFile()
            self.__camera_manager.get_camera().file_get(
                file_path.folder, file_path.name, gp.GP_FILE_TYPE_NORMAL, camera_file
            )
            camera_file.save(save_path)
            self.__logger.info(f"Image downloaded successfully to: {save_path}")
            return sdict(True, data={"save_path": save_path}, message=f"Image downloaded successfully to {save_path}.")
        except gp.GPhoto2Error as e:
            error_message = GPhotoErrorInterpreter.interpret_error(e)
            self.__logger.error(error_message)
            return sdict(False, message=error_message)