"""
Defines the interface for the command line
Routes out to handlers
"""

#TODO: Move this into __init__
__author__ = u'Adam Morris <amorris@mistermorris.com>'
__version__ = u'0.5'
__website__ = 'http://github.com/brainysmurf/gam'
__license__ = u'Apache License 2.0 (http://www.apache.org/licenses/LICENSE-2.0)'

import click
import sys, re, collections

#from gamlib.legacy import *

from gami import CreateNamedCmd
from gami import Manager, MockManager


BACKSPACE = '\b'

class CliState:
    """
    Holds state information that is available for each cli command
    """
    def __init__(self, verbose, json, mock=False, legacy=False):
        self.verbose = verbose
        self.json = json
        self.legacy = legacy
        self.mock = mock

        # Set up manager
        # The manager holds the code
        if self.mock:
            self.manager_cls = MockManager
        else:
            self.manager_cls = Manager

        self.manager = self.manager_cls()

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
@click.option('--legacy/--nolegacy', default=False, help="use legacy code from original ditto gam")
@click.option('--mock/--nomock', default=False, help="used for testing, make mock items instead of network calls")
#FIXME: Raise NotImplemented if --nolegacy passed but not implemented
@click.pass_context
def cli(ctx, verbose, json, mock, legacy):
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
    ctx.obj = CliState(verbose, json, mock=mock, legacy=legacy)

@cli.command('version')
@click.pass_obj
def cli_version(obj):
    """
    Output the version information
    """
    if obj.legacy:
        from gamlib.legacy import doGAMVersion
        doGAMVersion()

    else:
        import struct
        click.echo('GAM Version: {} - {}'.format(__version__, __website__))
        click.echo('Author: {}'.format(__author__))
        click.echo("Python Version: {0.major}.{0.minor}.{0.micro} {1}-bit {0.releaselevel}".format(sys.version_info, struct.calcsize('P')*8))
        click.echo('google-api-python-client: {}'.format(googleapiclient.__version__))
        click.echo('Platform: {}'.format(platform.platform()))
        click.echo('Platform Machine: {}'.format(platform.machine()))
        click.echo("Gam Path: {}".format(getGamPath()))



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
        from gamlib.legacy import doPrintUsers
        doPrintUsers()
    else:
        obj.actions.doPrintUsers()



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
        from gamlib.legacy import doPrintGroups
    else:
        from gamlib.lib import doPrintGroups

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
        from gamlib.legacy import doPrintOrgs
    else:
        from gamlib.lib import doPrintOrgs

    doPrintOrgs()

@cli_print.command('resources', options_metavar=BACKSPACE)
@click.argument('id', metavar="[id]", default=False)
@click.argument('description', metavar="[description]", default=False)
@click.argument('email', metavar="[email]", default=False)
@click.pass_obj
def print_resources(obj, id, description, email):
    if obj.legacy:
        from gamlib.legacy import doPrintResources
    else:
        from gamlib.lib import doPrintResources

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
        from gamlib.legacy import doPrintAliases
    else:
        from gamlib.lib import doPrintAliases

    doPrintAliases()

def creation_time_callback(creation_time):
    import datetime
    my_date = creation_time[:15]
    my_offset = creation_time[19:]
    return "{} {}".format(datetime.datetime.strptime(my_date, u"%Y%m%dT%H%M%S"), my_offset)


@cli.group('info')
@click.pass_context
def info(ctx):
    """
    No Google calls, so just print out stuff directly
    """

    # The GAM command string has incompatibility with click
    # Cases in point:
    #   gam info domain
    #   gam info domain logo <file> 
    # Notice that domain is a command, whereas it can also be a group
    # We work around this limitation by defining domain domain as a command
    # but checking at the group-level -- here -- by inspecting arugments,
    # thereby short-circuting it.
    manager = ctx.obj.manager

    if ctx.args[-1] == 'domain':
        if ctx.obj.legacy:
            from gamlib.legacy import doGetDomainInfo
            doGetDomainInfo()
        else:
            with manager.build_calls('directory', \
                    default_kwargs=dict(fields=u'users(customerId)', customer=manager.customerId, sortOrder=u'DESCENDING')) \
                    as key_builder:

                key_builder('users').\
                    function_list().\
                    define_resolve_path("users.[0].customerId")

            with manager.build_calls(
                'admin-settings', \
                    default_kwargs=dict(function=u'get', domainName=manager.domain), \
                    default_resolve_path="entry.apps$property.[0].value"
                ) as key_builder:

                key_builder('defaultLanguage')
                key_builder('organizationName')
                key_builder('maximumNumberOfUsers')
                key_builder('currentNumberOfUsers')
                key_builder('isVerified')
                key_builder('edition')
                key_builder('customerPIN')
                key_builder('creationTime').\
                    post_callback(creation_time_callback)
                key_builder('countryCode')
                key_builder('mxVerification')
                key_builder('ssoGeneral')
                key_builder('ssoSigningKey')
                key_builder('userEmailMigrationEnabled')
                key_builder('outboundGateway')

@info.command()
@click.argument('logo_file', type=click.File('rb'))
@click.pass_obj
def logo(obj, logo_file):
    """
    Update the logo, currently not implemented
    """
    pass

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

    \b
    USERNAME: username or email address, or uid:<id>
          if username is passed, automatically expanded using domain info
    """
    manager = obj.manager
    if obj.legacy:
        from gamlib.legacy import doGetUserInfo
        doGetUserInfo()
    else:
        if username.startswith('uid:'):
            username = username[ len('uid:')+1: ]
        if username == None:
            # This is here for reference, our code can't ever have user as None
            # but this is what GAM did when that occurred.
            username = self.credentials.id_token[u'email']
        elif username.find(u'@') == -1:
            username = u"{}@{}".format(username, manager.domain)

        getSchemas = getAliases = getGroups = getLicenses = True
        projection = u'full'
        customFieldMask = viewType = None

        # FIXME: Implement schemas as a named parameter in cli instead
        schemas = False
        projection = 'basic' if noschemas else 'custom' if schemas else 'domain_public' if userview else 'full'
        if projection == 'custom':
            # TODO: Looks like we need to implement a named parameter in case of schemas
            customFieldMask = None

        with manager.build_calls(
            'directory', \
                default_kwargs=dict(userKey=username, projection=projection, customFieldMask=customFieldMask, viewType=viewType)
            ) as key_builder:

            key_builder('users').\
                define_sub_keys(['name.givenName', 'name.familyName', 'isAdmin', 'isDelegatedAdmin', 'agreedToTerms', 'ipWhitelisted', 
                'suspended', 'suspensionReason', 'changePasswordAtNextLogin', 'id', 'customerId', 'isMailboxSetup', 'includeInGlobalAddressList',
                'creationTime', 'lastLoginTime', 'orgUnitPath', 'thumbnailPhotoUrl', 'ims', 'addresses', 'organizations', 'phones', 'emails', 
                'relations', 'externalIds', 'customSchemas', 'aliases']).\
                sub_key_post('lastLoginTime', lambda result: 'Never' if result == '1970-01-01T00:00:00.000Z' else result)

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
            from gamlib.legacy import doCreateUser
            doCreateUser()
        else:
            ctx.obj.actions.create_user(username)

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
        if ctx.legacy:
            doUpdateGroup()




