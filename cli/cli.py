"""
Defines the interface for the command line
Routes out to handlers
"""

#TODO: Move this into __init__

import click
import sys, re, collections

#from gamlib.legacy import *

from gami.named_param import CreateNamedCmd
from gami.manager import Manager, MockManager

import sys, os, time, datetime, random, socket, csv, platform, re, calendar, base64, hashlib, string

import json
import httplib2
import googleapiclient
import googleapiclient.discovery
import googleapiclient.errors
import googleapiclient.http
import oauth2client.client
import oauth2client.file
import oauth2client.tools
import uritemplate

from gami import const

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
        manager = obj.manager
        import struct
        click.echo('GAM Version: {} - {}'.format(const.__version__, const.__website__))
        click.echo('Author: {}'.format(const.__author__))
        click.echo("Python Version: {0.major}.{0.minor}.{0.micro} {1}-bit {0.releaselevel}".format(sys.version_info, struct.calcsize('P')*8))
        click.echo('google-api-python-client: {}'.format(googleapiclient.__version__))
        click.echo('Platform: {}'.format(platform.platform()))
        click.echo('Platform Machine: {}'.format(platform.machine()))
        click.echo("Gam Path: {}".format(manager.path_to_gam))

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

            with manager.output_block():
                with manager.api_block('directory') as api:
                    with api.defaults_block() as defaults:
                        defaults.\
                            default_kwargs(function="list", fields=u'users(customerId)', customer=manager.customerId, sortOrder=u'DESCENDING').\
                            default_resolve_path("users.[0].customerId")
                    api.add_key('users')

                with manager.api_block('admin-settings') as api:
                    with api.defaults_block() as defaults:
                        defaults.\
                            default_kwargs(function=u'get', domainName=manager.domain).\
                            default_resolve_path("entry.apps$property.[0].value")
                    api.add_key('defaultLanguage')
                    api.add_key('organizationName')
                    api.add_key('maximumNumberOfUsers')
                    api.add_key('currentNumberOfUsers')
                    api.add_key('isVerified')
                    api.add_key('edition')
                    api.add_key('customerPIN')
                    api.add_key('creationTime').\
                        post_callback(creation_time_callback)
                    api.add_key('countryCode')
                    api.add_key('mxVerification')
                    api.add_key('ssoGeneral')
                    api.add_key('ssoSigningKey')
                    api.add_key('userEmailMigrationEnabled')
                    api.add_key('outboundGateway')


@info.command()
@click.argument('logo_file', type=click.File('rb'))
@click.pass_obj
def logo(obj, logo_file):
    """
    Update the logo, currently not implemented
    """
    pass

@info.command('group', options_metavar="[options]")
@click.argument('groupname')
@click.argument('nousers', metavar="[nousers]", default=False)
@click.pass_obj
def info_group(obj, groupname, nousers):
    if obj.legacy:
        from gamlib.legacy import doGetGroupInfo
        doGetGroupInfo(group_name=groupname)
    else:
        manager = obj.manager

        if groupname.startswith('uid:'):
            groupname = groupname[ len('uid:')+1: ]
        elif groupname.find(u'@') == -1:
            groupname = u"{}@{}".format(groupname, manager.domain)

        get_users = not nousers

        with manager.output_block():
            with manager.api_block('directory') as api:
                with api.defaults_block() as defaults:
                    defaults.\
                        default_kwargs(groupKey=groupname).\
                        default_resolve_path(None)
                api.add_key('groups')

            with manager.api_block('groupssettings') as api:
                with api.defaults_block() as defaults:
                    defaults.\
                        default_kwargs(retry_reasons=[u'serviceLimit'], groupUniqueId=manager.get_result_key('email')).\
                        default_resolve_path(None)
                api.add_key('groups')

            if not nousers:
                with manager.api_block('directory', pages=True) as api:
                    with api.defaults_block() as defaults:
                        defaults.\
                            default_kwargs(function='list', items='members', groupKey=groupname).\
                            default_resolve_path(None)
                    api.add_key('members')


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

        with manager.output_block():
            with manager.api_block('directory') as api:
                with api.defaults_block() as defaults:
                    defaults.\
                        default_kwargs(userKey=username, projection=projection, customFieldMask=customFieldMask, viewType=viewType)

                api.add_key('users').\
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
@click.argument('groupname', metavar="<name> | <email>")
@click.pass_context
def update_group(ctx, groupname):
    """
    Update group info
    """
    manager = ctx.obj.manager

    with ctx.command.validate_named(ctx, ['--add', '--user']) as values:
        if ctx.obj.legacy:
            doUpdateGroup()
        else:
            if not(values.add and values.user):
                raise click.UsageError('Add parameter requires user parameter, too', ctx=ctx)

            if values.add:
                which =  [u'add', u'update', u'sync', u'remove']
                if not values.add.lower() in which:
                    raise click.UsageError('Illegal add paremeter "{}", must be one of {}'.format(values.add, which))

                with manager.output_block():
                    with manager.api_block('directory') as api:
                        with api.defaults_block():
                            api.default_kwargs(userKey=user, fields=u'id')
                        api.add_key('users')

            return
            group = sys.argv[3]
            if sys.argv[4].lower() in [u'add', u'update', u'sync', u'remove']:
                cd = buildGAPIObject(u'directory')
                if group[0:3].lower() == u'uid:':
                    group = group[4:]
                elif group.find(u'@') == -1:
                    group = u'%s@%s' % (group, domain)
                if sys.argv[4].lower() in [u'add', u'update']:
                    role = sys.argv[5].upper()
                    i = 6
                    if role not in [u'OWNER', u'MANAGER', u'MEMBER']:
                        role = u'MEMBER'
                        i = 5
                    if sys.argv[i].lower() in usergroup_types:
                        users_email = getUsersToModify(entity_type=sys.argv[i], entity=sys.argv[i+1])
                    else:
                        users_email = [sys.argv[i],]
                    for user_email in users_email:
                        if user_email != u'*' and user_email.find(u'@') == -1:
                            user_email = u'%s@%s' % (user_email, domain)
                        sys.stderr.write(u' %sing %s %s...' % (sys.argv[4].lower(), role.lower(), user_email))
                        try:
                            if sys.argv[4].lower() == u'add':
                                body = {u'role': role}
                                body[u'email'] = user_email 
                                result = callGAPI(service=cd.members(), function=u'insert', soft_errors=True, groupKey=group, body=body)
                            elif sys.argv[4].lower() == u'update':
                                result = callGAPI(service=cd.members(), function=u'update', soft_errors=True, groupKey=group, memberKey=user_email, body={u'email': user_email, u'role': role})
                            try:
                                if str(result[u'email']).lower() != user_email.lower():
                                    print u'added %s (primary address) to group' % result[u'email']
                                else:
                                    print u'added %s to group' % result[u'email']
                            except TypeError:
                                pass
                        except googleapiclient.errors.HttpError:
                            pass
                elif sys.argv[4].lower() == u'sync':
                    role = sys.argv[5].upper()
                    i = 6
                    if role not in [u'OWNER', u'MANAGER', u'MEMBER']:
                        role = u'MEMBER'
                        i = 5
                    users_email = getUsersToModify(entity_type=sys.argv[i], entity=sys.argv[i+1])
                    users_email = [x.lower() for x in users_email]
                    current_emails = getUsersToModify(entity_type=u'group', entity=group, member_type=role)
                    current_emails = [x.lower() for x in current_emails]
                    to_add = list(set(users_email) - set(current_emails))
                    to_remove = list(set(current_emails) - set(users_email))
                    for user_email in to_add:
                        sys.stderr.write(u' adding %s %s\n' % (role, user_email))
                        try:
                            result = callGAPI(service=cd.members(), function=u'insert', soft_errors=True, throw_reasons=[u'duplicate'], groupKey=group, body={u'email': user_email, u'role': role})
                        except googleapiclient.errors.HttpError:
                            result = callGAPI(service=cd.members(), function=u'update', soft_errors=True, groupKey=group, memberKey=user_email, body={u'email': user_email, u'role': role})
                    for user_email in to_remove:
                        sys.stderr.write(u' removing %s\n' % user_email)
                        result = callGAPI(service=cd.members(), function=u'delete', soft_errors=True, groupKey=group, memberKey=user_email)
                elif sys.argv[4].lower() == u'remove':
                    i = 5
                    if sys.argv[i].lower() in [u'member', u'manager', u'owner']:
                        i += 1
                    if sys.argv[i].lower() in usergroup_types:
                        user_emails = getUsersToModify(entity_type=sys.argv[i], entity=sys.argv[i+1])
                    else:
                        user_emails = [sys.argv[i],]
                    for user_email in user_emails:
                        if user_email != u'*' and user_email.find(u'@') == -1:
                            user_email = u'%s@%s' % (user_email, domain)
                        sys.stderr.write(u' removing %s\n' % user_email)
                        result = callGAPI(service=cd.members(), function=u'delete', soft_errors=True, groupKey=group, memberKey=user_email)
            else:
                i = 4
                use_cd_api = False
                use_gs_api = False
                gs_body = dict()
                cd_body = dict()
                while i < len(sys.argv):
                    if sys.argv[i].lower() == u'email':
                        use_cd_api = True
                        cd_body[u'email'] = sys.argv[i+1]
                        i += 2
                    elif sys.argv[i].lower() == u'admincreated':
                        use_cd_api = True
                        cd_body[u'adminCreated'] = sys.argv[i+1].lower()
                        if cd_body[u'adminCreated'] not in true_false:
                            print u'Error: Value for admincreated must be true or false. Got %s' % admin_created
                            sys.exit(9)
                        i += 2
                    else:
                        value = sys.argv[i+1]
                        gs_object = buildDiscoveryObject(u'groupssettings')
                        matches_gs_setting = False
                        for (attrib, params) in gs_object[u'schemas'][u'Groups'][u'properties'].items():
                            if attrib in [u'kind', u'etag', u'email']:
                                continue
                            if sys.argv[i].lower().replace(u'_', u'') == attrib.lower():
                                matches_gs_setting = True
                                if params[u'type'] == u'integer':
                                    try:
                                        if value[-1:].upper() == u'M':
                                            value = int(value[:-1]) * 1024 * 1024
                                        elif value[-1:].upper() == u'K':
                                            value = int(value[:-1]) * 1024
                                        elif value[-1].upper() == u'B':
                                            value = int(value[:-1])
                                        else:
                                            value = int(value)
                                    except ValueError:
                                        print u'Error: %s must be a number ending with M (megabytes), K (kilobytes) or nothing (bytes). Got %s' % value
                                        sys.exit(9)
                                elif params[u'type'] == u'string':
                                    if params[u'description'].find(value.upper()) != -1: # ugly hack because API wants some values uppercased.
                                        value = value.upper()
                                    elif value.lower() in true_values:
                                        value = u'true'
                                    elif value.lower() in false_values:
                                        value = u'false'
                                break
                        if not matches_gs_setting:
                            print u'ERROR: %s is not a valid argument for "gam update group..."' % sys.argv[i]
                            sys.exit(9)
                        gs_body[attrib] = value
                        use_gs_api = True
                        i += 2
                if group[:4].lower() == u'uid:': # group settings API won't take uid so we make sure cd API is used so that we can grab real email.
                    use_cd_api = True
                    group = group[4:]
                elif group.find(u'@') == -1:
                    cd = buildGAPIObject(u'directory')
                    group = u'%s@%s' % (group, domain)
                if use_cd_api:
                    cd = buildGAPIObject(u'directory')
                    try:
                        if cd_body[u'email'].find('@') == -1:
                            cd_body[u'email'] = u'%s@%s' % (cd_body[u'email'], domain)
                    except KeyError:
                        pass
                    cd_result = callGAPI(service=cd.groups(), function=u'patch', groupKey=group, body=cd_body)
                if use_gs_api:
                    gs = buildGAPIObject(u'groupssettings')
                    if use_cd_api:
                        group = cd_result[u'email']
                    gs_result = callGAPI(service=gs.groups(), function=u'patch', retry_reasons=[u'serviceLimit'], groupUniqueId=group, body=gs_body)
                print u'updated group %s' % group




