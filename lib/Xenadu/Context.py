import logging
import os
from optparse import OptionParser
import tempfile

class Context(object):
    command_line = OptionParser()

    command_chosen = {}
    env = {}
    globals = {}
    host = {}
    guest = {}
    db = {}
    config = {}
    logger = None

    def __init__(self):
        pass
    
    def init_logger(self):
        Context.logger = logging.getLogger("Xenadu")
        Context.logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(formatter)
        Context.logger.addHandler(ch)

    def import_config(self):
        #config_file = "%s/.xenadu/global.py" % os.path.expanduser('~')
        #execfile(config_file, globals(), Context.globals)
        Context.globals = []
        Context.globals['cwd'] = os.getcwd()
        Context.globals['tmp_path'] = tempfile.mkdtemp(suffix='xenadu')
        