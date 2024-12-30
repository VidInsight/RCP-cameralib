import gphoto2 as gp

class GPhotoErrorInterpreter:
    ERROR_CODES = {
        # Core Errors
        -1: "Generic Error",
        -2: "Bad Parameters",
        -3: "No Memory",
        -4: "Internal Library Error",
        -5: "Unknown Port",
        -6: "Operation Not Supported",
        
        # Camera Connection Errors
        -10: "Camera Not Found",
        -11: "Camera Busy",
        -12: "Camera Self-Test Failed", 
        -13: "Camera I/O Error",
        
        # File and Storage Errors
        -20: "File Not Found",
        -21: "File Already Exists",
        -22: "Directory Not Found",
        -23: "Storage Full",
        
        # Communication Errors
        -30: "Communication Timeout",
        -31: "Serial Port Error",
        -32: "USB Communication Error",
        -33: "Communication Protocol Error",
        
        # Capture Errors
        -40: "Image Capture Failed",
        -41: "Preview Capture Failed",
        -42: "Autofocus Failed",
        -43: "Exposure Setting Failed"
    }

    @classmethod
    def interpret_error(cls, error_code: int) -> str:
        """
        Interpret a GPhoto2 error code.
        
        :param error_code: The error code from a GPhoto2 exception
        :return: Human-readable error description
        """
        return cls.ERROR_CODES.get(error_code, f"Unknown Error Code: {error_code}")

    @classmethod
    def log_error(cls, logger, method_name: str, error: gp.GPhoto2Error):
        """
        Log a GPhoto2 error with detailed interpretation.
        
        :param logger: Logger instance
        :param method_name: Name of the method where error occurred
        :param error: GPhoto2 error exception
        """
        error_code = error.code
        error_message = cls.interpret_error(error_code)
        
        logger.error(
            f"[{method_name}] GPhoto2 Error: {error_message} "
            f"(Error Code: {error_code}, Original: {str(error)})"
        )
