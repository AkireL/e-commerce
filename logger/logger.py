import logging
import os

class PaymentLogger:
    _instance = None
    
    @classmethod
    def get_logger(cls):
        if cls._instance is None:
            logger = logging.getLogger('e-commerce')
            
            if not logger.handlers:
                enabled = os.getenv('LOG_ENABLED', 'false').lower() in ('true', '1', 'yes')
                
                if enabled:
                    logger.setLevel(logging.INFO)
                    handler = logging.StreamHandler()
                    handler.setFormatter(logging.Formatter(
                        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                    ))
                    logger.addHandler(handler)
                else:
                    logger.disabled = True
                
            cls._instance = logger
        
        return cls._instance
    
logger = PaymentLogger.get_logger()