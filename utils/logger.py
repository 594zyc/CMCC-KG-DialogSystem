import logging

def create_logger(logdir, print_details):
    fmt = '%(message)s'
    # datefmt = "%y-%m-%d %H:%M:%S"
    logging.basicConfig(level=logging.INFO,
                                      format=fmt,
                                      filename=logdir)
                                      # datefmt=datefmt)

    logger = logging.getLogger('CMCClogger')
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    logger.addHandler(console)

    return logger
