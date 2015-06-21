"""
Defines the interface for the command line
"""

import click
from click.core import BaseCommand
import sys, re
from indentedtextparser import IndentedTextParser
from gamlib import *

class CliState:
	def __init__(self, verbose, json):
		self.verbose = verbose
		self.json = json

@click.group()
@click.option('--verbose/--notverbose', default=False, help="print out stuff")
@click.option('--json/--nojson', default=True, help="normalize output into a pytong dict")
@click.pass_context
def cli(ctx, verbose, json):
	"""
	GAM. Retrieve or set Google Apps domain,
	user, group and alias settings. Exhaustive list of commands
	can be found at: https://github.com/jay0lee/GAM/wiki 

	\b
	Examples:
	gam info domain
	gam create user jsmith firstname John lastname Smith password secretpass
	gam update user jsmith suspended on
	gam.exe update group announcements add member jsmith
	"""

	# Yuck
	ctx.obj = CliState(verbose, json)

@cli.group()
@click.pass_context
def info(ctx):
	"""
	Provides info, requires command
	"""

	# The GAM command string can have a group that is also a command
	# Cases in point:
	# gam info domain gets domain info
	# gam info domain logo <file> 
	# The only way to check it is at the preceeding level... here

	if ctx.args[-1] == 'domain':
		doGetDomainInfo()

@info.command(options_metavar="[options]")
@click.argument('groupname')
@click.pass_obj
def group(obj, groupname):
	doGetGroupInfo(group_name=groupname)

@info.command('user', options_metavar="")   #options implemented different, so don't output "[OPTIONS]"
@click.argument('username')
@click.argument('noaliases', metavar="[noaliases]", default=False)
@click.argument('nogroups', metavar="[nogroups]", default=False)
@click.argument('noschemas', metavar="[noschemas]", default=False)
@click.argument('userview', metavar="[userview]", default=False)
@click.argument('nolicenses', metavar="[nolicenses]", default=False)
@click.pass_obj
def info_user(obj, username, nogroups, noaliases, nolicenses, noschemas, userview):
	"""
	\b
	Get information about the user
	@param USERNAME: username or email address
	"""
	doGetUserInfo(username)

@info.group()
@click.pass_context
def domain(ctx):
	"""
	\b
	By itself, provides info about the domain
	With command following, provides something else
	"""

@cli.group()
@click.pass_context
def create(ctx):
	"""
	Contains commands for creating users, groups, whatever
	"""

@create.command('user', options_metavar="")
@click.argument('username')
@click.argument('firstname')
@click.argument('lastname')
@click.argument('password')
@click.pass_obj
def create_user(obj, username, firstname, lastname, password):
	"""
	Creates a user!
	"""
	doCreateUser()

@domain.command()
@click.argument('logo_file', type=click.File('rb'))
@click.pass_obj
def logo(obj, logo_file):
	"""
	Update the logo, currently not implemented
	"""
	pass

class ImportableGam:
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
			click.echo( python_dict )
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
		self.command(params)

if __name__ == "__main__":
	ig = ImportableGam()
	# ig.command_from_string('gam info domain')
	# ig.command_from_string('gam info user adam.morris nolicenses')

	ig.command_from_string('gam info group it.committee')
