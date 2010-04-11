from Xenadu.Core import Core
import re, sys

class Registry(object):

    def __init__(self, Core):
        self.Core = Core
        self.tasks = {}
        self.options = {}

    def register_function(self, option, function):
        self.tasks[option] = function

    def register_option(self, option, help):
        self.Core.command_line.add_option("--" + option, action="store_true", help=help)
        self.options[option] = 1

    def register_argument(self, option, help):
        self.Core.command_line.add_option("--" + option, help=help)
        self.options[option] = 1

    def register_task(self, name, args, help, function):
        if args > 0:
            self.register_argument(name, help)
        else:
            self.register_option(name, help)
        self.register_function(name, function)

    def update(self):
        m = __import__("Xenadu.Task")
        for task in dir(m.Task):            
            if not re.search(r'^__', task):
                mod_name = "Xenadu.Task.%s" % task
                mod = sys.modules[mod_name]
                mod.register()
                self.Core.logger.debug("loading: %s" % mod_name)
    