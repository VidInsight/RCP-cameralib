import os
import yaml
import logging

from logging.handlers import RotatingFileHandler
from datetime import datetime


class Logger:
    """
    Merkezi log sistemi.
    Varsayılan log dosya adı: rcp_log_<timestamp>.log
    Varsayılan log dizini: Masaüstünde 'SRC_LOGS/' klasörü.
    """

    @staticmethod
    def get_default_log_dir():
        """
        Masaüstünde varsayılan 'SRC_LOGS/' klasörünü döndürür.
        """
        desktop_path = os.path.expanduser("~")
        default_log_dir = os.path.join(desktop_path, "SRC_LOGS")
        if not os.path.exists(default_log_dir):
            os.makedirs(default_log_dir)  # Klasör yoksa oluştur
        return default_log_dir

    @staticmethod
    def load_config():
        """
        YAML yapılandırma dosyasını yükler.
        Eğer dosyaya ulaşılamazsa varsayılan yapılandırmayı döndürür.
        """
        default_log_dir = Logger.get_default_log_dir()
        config_path = "../config.yaml"
        default_config = {
            "console_level": "INFO",
            "file_level": "DEBUG",
            "log_dir": default_log_dir,
            "max_log_size": 5242880,  # 5 MB
            "backup_count": 5,
            "log_format": "%(asctime)s - [%(name)s] - %(levelname)s - %(message)s",
            "date_format": "%Y-%m-%d %H:%M:%S",
            "log_file_name": "rcp_log",
            "handlers": {
                "console": True,
                "file": True
            }
        }

        try:
            if os.path.exists(config_path):
                with open(config_path, "r") as file:
                    config = yaml.safe_load(file)
                    return config.get("log_settings", default_config)
        except yaml.YAMLError as e:
            print(f"YAML dosyasından okuma hatası: {e}")
        except Exception as e:
            print(f"Yapılandırma dosyası yüklenirken hata: {e}")

        print("config.yaml bulunamadı, varsayılan ayarlar kullanılacak.")
        return default_config

    @staticmethod
    def get_logger(name: str):
        """
        Logger oluşturur ve yapılandırmayı uygular.
        :param name: Logger adı (genelde modül adı)
        :return: logging.Logger instance
        """
        # Yapılandırmayı yükle
        config = Logger.load_config()

        # Log dizinini al
        log_dir = config.get("log_dir", Logger.get_default_log_dir())
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        # Log dosyasının adı
        timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        log_file_name = config.get("log_file_name", "rcp_log")
        log_file = os.path.join(log_dir, f"{log_file_name}-{timestamp}.log")

        # Log seviyelerini al
        console_level = getattr(logging, config.get("console_level", "INFO").upper(), logging.INFO)
        file_level = getattr(logging, config.get("file_level", "DEBUG").upper(), logging.DEBUG)

        # Log formatını al
        log_format = config.get("log_format", "%(asctime)s - [%(name)s] - %(levelname)s - %(message)s")
        date_format = config.get("date_format", "%Y-%m-%d %H:%M:%S")

        # Dosya boyutu ve yedekleme ayarlarını al
        max_bytes = config.get("max_log_size", 5 * 1024 * 1024)
        backup_count = config.get("backup_count", 5)

        # Handlers kontrolü
        handlers = config.get("handlers", {"console": True, "file": True})

        logger = logging.getLogger(name)

        # Eğer logger zaten handler'lara sahipse yeniden ekleme yapma
        if not logger.hasHandlers():
            # Formatter: Log formatı
            formatter = logging.Formatter(fmt=log_format, datefmt=date_format)

            if handlers.get("file", True):
                # Dosya Handler
                file_handler = RotatingFileHandler(
                    log_file,
                    maxBytes=max_bytes,
                    backupCount=backup_count,
                    encoding="utf-8",
                )
                file_handler.setFormatter(formatter)
                file_handler.setLevel(file_level)
                logger.addHandler(file_handler)

            if handlers.get("console", True):
                # Konsol Handler
                console_handler = logging.StreamHandler()
                console_handler.setFormatter(formatter)
                console_handler.setLevel(console_level)
                logger.addHandler(console_handler)

        logger.setLevel(min(console_level, file_level))  # Genel log seviyesi, en düşük seviyeye ayarlanır.
        return logger
