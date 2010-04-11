#import Task.__registry__

import sys, traceback, os.path
import os
import tempfile
import logging
from optparse import OptionParser

class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg

class Core(object):
    registry = None
    logger = None
    config = {}
    env = {}

    def __init__(self):
        self.command_line = OptionParser()
        self.command_chosen = {}
        self.init_logger()

    def init_logger(self):
        Core.logger = logging.getLogger("Xenadu")
        Core.logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(formatter)
        Core.logger.addHandler(ch)

    def process_cmdline(self):
        self.command_line.add_option("--config", help="config file path")
        (options, args) = self.command_line.parse_args()

        for option in Core.registry.options.keys():
            if getattr(options, option):
                self.command_chosen[option] = getattr(options, option)

        self.load_config(options)

        for option in self.command_chosen.keys():
            Core.logger.info("calling " + option)
            function = Core.registry.tasks[option]
            function(self.command_chosen[option])

    def load_config(self, options):
        try:
            config_file = getattr(options, "config")
        except KeyError:
            print "exception: no config file"

        Core.env = {
            'cwd': os.getcwd(),
            #'tmp_path': tempfile.mkdtemp(suffix='xenadu'),
            'tmp_path': "/tmp/xenadu",
            'guest_path': os.path.dirname(os.path.abspath(config_file))
        }

        try:
            execfile(config_file, globals(), Core.config)
            Core.logger.info("config file: " + config_file)
            Core.config["filename"] = getattr(options, "config")
        except IOError:
            traceback.print_tb(sys.exc_info()[2])
            Core.logger.error("Xenadu cannot load or execute config file '%s'; exiting." % config_file)
            sys.exit()
        
        try:
            dom0_config_filename = Core.config["xen"]["dom0_config"]
        except KeyError:
            dom0_config_filename = 0
            Core.logger.warn("There is no dom0 config file.  Is this a Xen root domain?")

        if dom0_config_filename:
            try:
                host_hash = {}
                Core.logger.info("dom0 config file: " + dom0_config_filename)
                execfile(Core.config["xen"]["dom0_config"], globals(), host_hash)
                Core.config["dom0"] = host_hash
            except IOError:
                traceback.print_tb(sys.exc_info()[2])
                Core.logger.warn("Xenadu cannot load or execute config file '%s'; exiting" % dom0_config_filename)
                sys.exit()

    def start(self):
        from Xenadu.Registry import Registry
        Core.registry = Registry(self)
        Core.registry.update()

        self.process_cmdline()
