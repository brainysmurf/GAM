"""
Defines the interface for the command line
"""

import click
import sys, re, collections

from gamlib.legacy import *

from gami import CreateNamedCmd

BACKSPACE = '\b'

class CliState:
	"""
	Holds state information that is available for each cli command
	"""
	def __init__(self, verbose, json, legacy=True):
		self.verbose = verbose
		self.json = json
		self.legacy = legacy

class ArgOptName(click.ParamType):
	"""

	"""
	def __init__(self, name, info):
		self.name = name
		self.info = info
		self.times_called = 0

	def get_metavar(self, param):
		return "{} <{}>".format(self.name, self.info)

	def convert(self, value, param, ctx):
		self.times_called += 1
		if self.times_called == 1:
			self._first_value = value
		if self.times_called == 2:
			return 

@click.group(context_settings=dict(max_content_width=200))
@click.option('--verbose/--notverbose', default=False, help="print out stuff")
@click.option('--json/--nojson', default=True, help="normalize output into a pytong dict")
@click.option('--legacy/--nolegacy', default=True, help="use legacy code from original ditto gam")
#FIXME: Raise NotImplemented if --nolegacy passed but not implemented
@click.pass_context
def cli(ctx, verbose, json, legacy):
	"""
	GAMi. GAM improved, importable, installable-into-virtualenv

	Piggybacks from GAM
	Retrieve or set Google Apps domain,
	user, group and alias settings. Exhaustive list of commands
	can be found at: https://github.com/jay0lee/GAM/wiki 
	Although at the moment, only limited set is implemented

	\b
	Legacy Examples:
	python gam.py info domain
	python gam.py create user jsmith firstname John lastname Smith password secretpass

	\b 
	New Examples (follows same command structure):
	gami info domain
	gami create user jsmith firstname John lastname Smith password secretpass

	\b
	Import from python?
	from gami import run_from_command_string
	run_from_command_string('gami info domain')
	"""
	ctx.obj = CliState(verbose, json, legacy)

@cli.command('version')
@click.pass_obj
def cli_version(obj):
	"""
	Output the version information
	"""
	if obj.legacy:
		doGAMVersion()

@cli.command('batch', options_metavar=BACKSPACE)
@click.argument('file', type=click.File('r'), metavar='<filename.ext>')
def cli_batch():
	"""
	\b
	Run a bunch of batch operations contained in a text file
	Not currently supported because must investigate threads
	"""

@cli.command('csv')
@click.argument('source', type=click.File('r'), metavar="<filename.ext>")
def cli_csv():
	"""
	Reads in a csv file, with headers, and performs actions on them
	TODO: How to implement this? recurse?
	"""

@cli.command('loop')
def cli_loop():
	"""
	Can't find documentation on this...
	"""

@cli.group('print')
@click.pass_context
def cli_print(ctx):
	"""
	Commands to print all users | groups 
	"""

@cli_print.command('users', options_metavar="\b")
@click.argument('firstname', metavar="[firstname]", default=False)
@click.argument('lastname', metavar="[lastname]", default=False)
@click.argument('username', metavar="[username]", default=False)
@click.argument('ou', metavar="[ou]", default=False)
@click.argument('suspended', metavar="[suspended]", default=False)
@click.argument('changepassword', metavar="[changepassword]", default=False)
@click.argument('agreedtoterms', metavar="[agreedtoterms]", default=False)
@click.argument('admin', metavar="[admin]", default=False)
@click.argument('aliases', metavar="[aliases]", default=False)
@click.argument('groups', metavar="[groups]", default=False)
@click.pass_obj
def print_users(obj, firstname, lastname, username, ou, suspended, changepassword, agreedtoterms, admin, aliases, groups):
	"""
	\b
	Outputs all users as a CSV with header information
	Arguments in [brackets] add headers
	Note: Adding headers increases time for completion
	TODO: Queries? Order by?
	"""
	if obj.legacy:
		doPrintUsers()

@cli_print.command('groups', options_metavar=BACKSPACE)
@click.argument('name', metavar="[name]", default=False)
@click.argument('description', metavar="[description]", default=False)
@click.argument('members', metavar="[members]", default=False)
@click.argument('managers', metavar="[managers]", default=False)
@click.argument('owners', metavar="[owners]", default=False)
@click.argument('settings', metavar="[settings]", default=False)
@click.argument('admincreated', metavar="[admincreated]", default=False)
@click.argument('id', metavar="[id]", default=False)
@click.argument('aliases', metavar="[aliases]", default=False)
@click.argument('todrive', metavar="[todrive]", default=False)
@click.pass_obj
def print_groups(obj, name, description, members, managers, owners, settings, admincreated, id, aliases, todrive):
	"""
	\b
	Outputs all users as a CSV with header information
	Arguments in [brackets] add headers
	Note: Adding headers increases time for completion
	TODO: [domain] not yet implemented
	"""
	if obj.legacy:
		doPrintGroups()

@cli_print.command('orgs', options_metavar=BACKSPACE)
@click.argument('name', metavar="[name]", default=False)
@click.argument('description', metavar="[description]", default=False)
@click.argument('parent', metavar="[parent]", default=False)
@click.argument('inherit', metavar="[inherit]", default=False)
@click.pass_obj
def print_orgs(obj, name, description, parent, inherit):
	"""
	Prints a CSV file of all organizational units in the Google Apps account
	"""
	if obj.legacy:
		doPrintOrgs()

@cli_print.command('resources', options_metavar=BACKSPACE)
@click.argument('id', metavar="[id]", default=False)
@click.argument('description', metavar="[description]", default=False)
@click.argument('email', metavar="[email]", default=False)
@click.pass_obj
def print_resources(obj, id, description, email):
	if obj.legacy:
		doPrintResources()

@cli_print.command('report', options_metavar=BACKSPACE)
def print_report(obj):
	"""
	Not yet implemented, not working on my domain? No error, just not working
	"""




@cli_print.command('aliases', options_metavar=BACKSPACE)
@click.argument('todrive', metavar="[todrive]", default=False)
@click.pass_obj
def print_aliases(obj, todrive):
	"""
	Print all aliases
	"""
	if obj.legacy:
		doPrintAliases()

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
		if ctx.obj.legacy:
			doGetDomainInfo()

@info.command(options_metavar="[options]")
@click.argument('groupname')
@click.pass_obj
def group(obj, groupname):
	if obj.legacy:
		doGetGroupInfo(group_name=groupname)

@info.command('user', options_metavar=BACKSPACE)   #options implemented different, so don't output "[OPTIONS]"
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
	if obj.legacy:
		doGetUserInfo(username)

@info.group('domain')
@click.pass_context
def info_domain(ctx):
	"""
	\b
	By itself, provides info about the domain
	With command following, provides something else
	"""

@cli.group('create')
@click.pass_context
def cli_create(ctx):
	"""
	Contains commands for creating users, groups, whatever
	"""

@cli_create.command('user', cls=CreateNamedCmd, options_metavar=BACKSPACE)
@click.argument('username')
@click.pass_context
def create_user(ctx, username):
	"""
	Creates a user!
	"""
	with ctx.command.validate_named(ctx, ['firstname', 'lastname', '--password', '--changepassword', '--gal', 'org', '--type', '--externalid']) as values:
		if ctx.obj.legacy:
			doCreateUser()
		else:
			click.echo(values)

@cli_create.command('group', cls=CreateNamedCmd, options_metavar=BACKSPACE)
@click.argument('email', metavar="<email>")
@click.pass_context
def create_group(ctx, email):
	"""
	Creates a group!	
	"""
	with ctx.command.validate_named(ctx, ['name', '--description']) as values:
		# do something here in future, we have the values
		if ctx.obj.legacy:
			doCreateGroup()
		else:
			click.echo(values)

@cli.group('update')
@click.pass_context
def cli_update(ctx):
	"""
	Updates
	"""	

@cli_update.command('group', cls=CreateNamedCmd, options_metavar=BACKSPACE)
@click.argument('group_email', metavar="<email>")
@click.pass_context
def update_group(ctx, group_email):
	"""
	Update group info
	"""
	with ctx.command.validate_named(ctx, ['--add', '--user']) as values:
		if ctx.obj.legacy:
			doUpdateGroup()

@info_domain.command()
@click.argument('logo_file', type=click.File('rb'))
@click.pass_obj
def logo(obj, logo_file):
	"""
	Update the logo, currently not implemented
	"""
	pass



