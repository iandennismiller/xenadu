from Xenadu.Core import Core

class Registry(object):
	task_registry = {}
	options_registry = {}

	def __init__(self):
		pass

	def register_function(self, option, function):
		Registry.task_registry[option] = function

	def register_option(self, option, help):
		Core().context.command_line.add_option("--" + option, action="store_true", help=help)
		Registry.options_registry[option] = 1

	def register_argument(self, option, help):
		Core().context.command_line.add_option("--" + option, help=help)
		Registry.options_registry[option] = 1

	def register_task(self, name, args, help, function):
		if args > 0:
			self.register_argument(name, help)
		else:
			self.register_option(name, help)
		self.register_function(name, function)
