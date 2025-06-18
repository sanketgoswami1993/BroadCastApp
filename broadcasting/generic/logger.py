from broadcasting import settings
import os
import logging

def logger(logger_name="broadcasting"):
    log_file = os.path.join(settings.BASE_DIR, 'media/logs', logger_name+'.txt')
    dir_name = os.path.dirname(log_file)
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)

    log_object = logging.getLogger(logger_name)

    if not len(log_object.handlers):
        log_object.setLevel(logging.INFO)

        handler = logging.handlers.RotatingFileHandler(log_file, maxBytes=1024, backupCount=1)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        log_object.addHandler(handler)

    return log_object

log = logger()