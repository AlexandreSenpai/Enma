import logging

class Handler(logging.StreamHandler):
    def __init__(self):
        logging.StreamHandler.__init__(self)


class Logger:
    def __init__(self, 
                 logger_name: str,
                 default_level: int = logging.NOTSET,
                 handler: logging.StreamHandler = None,
                 formatter: logging.Formatter = None):
        self.logger = logging.getLogger(logger_name or "NHentai")
        self.logger.setLevel(default_level)
        
        if handler and formatter: handler.setFormatter(formatter)
        if handler: self.logger.addHandler(handler)
    
    def set_level(self, level: int):
        self.logger.setLevel(level)
        return self
    
    def disable_logger(self, logger_name: str='NHentai'):
        logging.getLogger(logger_name).disabled = True
        return self
    
    def info(self, msg: str):
        self.logger.info(msg)
        
    def warn(self, msg: str):
        self.logger.warning(msg)
        
    def error(self, msg: str):
        self.logger.error(msg)
        
    def debug(self, msg: str):
        self.logger.debug(msg)

logger = Logger(default_level=logging.INFO, 
                handler=Handler(),
                formatter=logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'),
                logger_name="NHentai")