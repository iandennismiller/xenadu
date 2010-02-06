import Task.__registry__

class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg

class Core(object):
    registry = None
    context = None

    def __init__(self):
        pass

    def call_chosen_function(self):
        for option in Core.context.command_chosen.keys():
            Core.context.logger.info("calling " + option)
            function = Core.registry.task_registry[option]
            function(Core.context.command_chosen[option])

    def load_configs(self, options):
        #try:
            ### 
            config_file = getattr(options, "config")
            #host_file = "%s/%s/dom0/xenadu_host.py" % (Core.context.globals['host_path'], getattr(options, "host"))
            execfile(config_file, globals(), Core.context.config)
            Core.context.logger.info("config file: " + config_file)
            Core.context.config["filename"] = getattr(options, "config")
        #except:
        #    print "exception: no config file"

        #Core.context.globals["guest"] = getattr(options, "guest")
        #guest_file = "%s/%s/%s/%s.py" % (Core.context.globals['host_path'], getattr(options, "host"), 
        #    getattr(options, "guest"), getattr(options, "guest"))
        #execfile(guest_file, globals(), Core.context.guest)
        #Core.context.logger.info("guest file: " + guest_file)
        
    def process_cmdline(self):
        Task.__registry__.register_tasks()

        Core.context.command_line.add_option("--config", help="config file path")
        
        #Core.context.command_line.add_option("--host", help="host path")
        #Core.context.command_line.add_option("--guest", help="guest path")

        (options, args) = Core.context.command_line.parse_args()

        for option in Core.registry.options_registry.keys():
            if getattr(options, option):
                Core.context.command_chosen[option] = getattr(options, option)

        self.load_configs(options)

        self.call_chosen_function()

    def start(self):
        from Xenadu.Registry import Registry
        from Xenadu.Context import Context

        Core.registry = Registry()
        Core.context = Context()
        Core.context.init_logger()
        Core.context.import_config()
        self.process_cmdline()
