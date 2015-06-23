from cli import cli
from output_parser import IndentedTextParser
import click

class RunGami:
	"""
	Class for use by other packages who want gam's functionality without having to do system calls
	TODO: Move this into its own file (just have to import the cli function, above)
	"""

	def __init__(self, catch_exceptions=False, jsonify=True):
		self.catch_exceptions = catch_exceptions
		self.jsonify = jsonify
		if self.jsonify:
			self.indent_parser = IndentedTextParser()
		else:
			self.indent_parser = None

	def parse_value(self, value):
		"""
		Turns True/False strings into booleans
		"""	
		if hasattr(value, 'lower') and value.lower() == "true":
			return True
		if hasattr(value, 'lower') and value.lower() == "false":
			return False
		return value

	def command(self, params):
		if params[0] == 'gam' or params[0] == 'gam.py':
			params.pop(0)

		from click.testing import CliRunner
		run = CliRunner()
		result = run.invoke(cli, params, catch_exceptions=self.catch_exceptions)

		if self.jsonify and not result.exception:
			python_dict = self.indent_parser.parse(result.output)
			return python_dict
		else:
			click.echo(result.output)

		if result.exception:
			click.echo(result.exception)

	def command_from_cmdline(self):
		params = sys.argv
		self.command(params)

	def command_from_string(self, str):
		"""
		@str Regular command, like 'gam info domain'
		"""
		# Use click's native way of parsing the string into params
		from click.parser import split_arg_string
		params = split_arg_string(str)
		return self.command(params)

if __name__ == "__main__":
	ig = RunGami()
	r = ig.command_from_string('gam info domain')
	r = ig.command_from_string('gam info user adam.morris nolicenses')
	r = ig.command_from_string('gam info group it.committee')