import gphoto2 as gp
from typing import Dict, Any

from src.modules.camera_manager import CameraManager
from src.utils.rcp_logger import Logger
from src.utils.utils import *
from src.utils.gphoto_errors import GPhotoErrorInterpreter

class ConfigHandler:
    def __init__(self, camera_manager: CameraManager):
        """
        Initialize ConfigHandler using configuration from CameraManager.

        :param camera_manager: CameraManager instance
        """
        self.__camera_manager = camera_manager
        self.__logger = Logger.get_logger("Config Handler")
        
        # Retrieve configuration from CameraManager
        self.__settings = camera_manager.get_config()
        self.__logger.debug("Configuration retrieved from CameraManager")

        # Only attempt to set configs if a camera is connected and settings are loaded
        if self.__camera_manager.get_camera() and self.__settings:
            camera_settings = self.__settings.get('camera', {})
            # Remove nested dictionaries or lists
            camera_settings = {k: v for k, v in camera_settings.items() 
                               if not isinstance(v, (dict, list))}
            self.set_multiple_configs(camera_settings)

    def set_single_config(self, setting_name: str, setting_value: Any) -> Dict:
        """
        Set a single configuration setting on the camera.

        :param setting_name: The name of the setting to be configured.
        :param setting_value: The value to set for the specified setting.
        :return: A dictionary indicating the success status and any relevant messages.
        """
        method_name = "set_single_config"
        try:
            camera = self.__camera_manager.get_camera()
            if not camera:
                self.__logger.error(f"[{method_name}] No connected camera available")
                return sdict(False, message="No connected camera available.")

            config = camera.get_config()
            
            # Attempt to find the setting
            try:
                setting = config.get_child_by_name(setting_name)
            except gp.GPhoto2Error as e:
                error_message = GPhotoErrorInterpreter.interpret_error(e)
                self.__logger.warning(f"[{method_name}] Setting {setting_name} not found: {error_message}")
                return sdict(False, message=f"Setting {setting_name} not found: {error_message}")

            # Validate and set value for radio/menu type settings
            if setting.get_type() in [gp.GP_WIDGET_RADIO, gp.GP_WIDGET_MENU]:
                valid_choices = [setting.get_choice(i) for i in range(setting.count_choices())]
                if str(setting_value) not in valid_choices:
                    self.__logger.warning(
                        f"[{method_name}] Invalid value for {setting_name}. "
                        f"Valid choices are: {valid_choices}. Defaulting to {valid_choices[0]}"
                    )
                    setting_value = valid_choices[0]

            setting.set_value(str(setting_value))
            camera.set_config(config)
            
            self.__logger.info(f"[{method_name}] Successfully set {setting_name} to {setting_value}")
            return sdict(True, message=f"Successfully set {setting_name}")

        except gp.GPhoto2Error as e:
            error_message = GPhotoErrorInterpreter.interpret_error(e)
            self.__logger.error(f"[{method_name}] Error setting {setting_name}: {error_message}")
            return sdict(False, message=f"Error setting {setting_name}: {error_message}")
        except Exception as e:
            self.__logger.error(f"[{method_name}] Unexpected error setting {setting_name}: {e}")
            return sdict(False, message=f"Unexpected error: {e}")

    def set_multiple_configs(self, settings: Dict[str, Any]) -> Dict:
        """
        Set multiple configuration settings on the camera.

        :param settings: A dictionary where keys are setting names and values are the settings to apply.
        :return: A dictionary with the result of each setting.
        """
        method_name = "set_multiple_configs"
        if not settings:
            self.__logger.warning(f"[{method_name}] No settings provided to set")
            return {}

        results = {}
        for setting_name, setting_value in settings.items():
            # Skip settings that are dictionaries or lists
            if isinstance(setting_value, (dict, list)):
                continue
            
            result = self.set_single_config(setting_name, setting_value)
            results[setting_name] = result

        self.__logger.info(f"[{method_name}] Configuration settings processed")
        return results

    def get_config_value(self, setting_name: str) -> Dict:
        """
        Get the current value of a specific configuration setting.

        :param setting_name: The name of the setting to retrieve.
        :return: A dictionary with the success status and the current value if successful.
        """
        method_name = "get_config_value"
        try:
            camera = self.__camera_manager.get_camera()
            if not camera:
                self.__logger.error(f"[{method_name}] No connected camera available")
                return sdict(False, message="No connected camera available.")

            config = camera.get_config()
            
            try:
                setting = config.get_child_by_name(setting_name)
            except gp.GPhoto2Error as e:
                error_message = GPhotoErrorInterpreter.interpret_error(e)
                self.__logger.warning(f"[{method_name}] Setting {setting_name} not found: {error_message}")
                return sdict(False, message=f"Setting {setting_name} not found: {error_message}")

            current_value = setting.get_value()
            self.__logger.info(f"[{method_name}] Current value of {setting_name} is {current_value}")
            return current_value

        except gp.GPhoto2Error as e:
            error_message = GPhotoErrorInterpreter.interpret_error(e)
            self.__logger.error(f"[{method_name}] Error retrieving value for {setting_name}: {error_message}")
            return sdict(False, message=f"Error retrieving value for {setting_name}: {error_message}")
        except Exception as e:
            self.__logger.error(f"[{method_name}] Unexpected error retrieving {setting_name}: {e}")
            return sdict(False, message=f"Unexpected error: {e}")

    def get_multiple_config_values(self, settings: Dict[str, None]) -> Dict:
        """
        Get the current values of multiple configuration settings.

        :param settings: A dictionary where keys are setting names.
        :return: A dictionary with setting names as keys and their current values or errors as values.
        """
        method_name = "get_multiple_config_values"
        self.__logger.debug(f"[{method_name}] Retrieving multiple configuration values")
        
        results = {}
        for setting_name in settings.keys():
            result = self.get_config_value(setting_name)
            results[setting_name] = result

        return results
