"""
Defines the interface for the command line
"""

import click
import sys, re

from gamlib.legacy import *

class CliState:
	"""
	Holds state information that is available for each cli command
	"""
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

@cli.command('version')
def cli_version():
	"""
	Output the version information
	"""
	doGAMVersion()

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



