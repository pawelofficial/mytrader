import logging 
import os 

this_path=os.path.dirname(os.path.abspath(__file__))

def setup_logger(name,mode='w',fp=None):
    # Create a custom logger
    if fp is None:
        fp=os.path.join(this_path,'logs')
    logger = logging.getLogger(name)

    # Set the level of logger to INFO
    logger.setLevel(logging.INFO)

    # Create handlers
    c_handler = logging.StreamHandler()
    fp=os.path.join(fp,f'{name}.log')
    f_handler = logging.FileHandler(fp,mode)

    # Set level of handlers to INFO
    c_handler.setLevel(logging.ERROR)
    f_handler.setLevel(logging.INFO)

    # Create formatters and add it to handlers
    format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    c_handler.setFormatter(format)
    f_handler.setFormatter(format)

    # Add handlers to the logger
    logger.addHandler(c_handler)
    logger.addHandler(f_handler)

    return logger