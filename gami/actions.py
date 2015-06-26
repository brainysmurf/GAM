"""
Defines all the actions
"""

#TODO: Move this into __init__
__author__ = u'Adam Morris <amorris@mistermorris.com>'
__version__ = u'0.5'
__website__ = 'http://github.com/brainysmurf/gam'
__license__ = u'Apache License 2.0 (http://www.apache.org/licenses/LICENSE-2.0)'

class Actions(object):

    def __init__(self, manager):
        self.manager = manager

    @staticmethod
    def creation_time_callback(creation_time):
        import datetime
        my_date = creation_time[:15]
        my_offset = creation_time[19:]
        return "{} {}".format(datetime.datetime.strptime(my_date, u"%Y%m%dT%H%M%S"), my_offset)

    def doGAMVersion(self):
        """
        No Google calls, so just print out stuff directly
        """
        import struct
        click.echo('GAM Version: {} - {}'.format(__version__, __website__))
        click.echo('Author: {}'.format(__author__))
        click.echo("Python Version: {0.major}.{0.minor}.{0.micro} {1}-bit {0.releaselevel}".format(sys.version_info, struct.calcsize('P')*8))
        click.echo('google-api-python-client: {}'.format(googleapiclient.__version__))
        click.echo('Platform: {}'.format(platform.platform()))
        click.echo('Platform Machine: {}'.format(platform.machine()))
        click.echo("Gam Path: {}".format(getGamPath()))

    def doGetDomainInfo(self):
        """
        Build the Google Calls abstractly and then get the information itemized under Key Builders
        The result will be output to stdout, which happens at close of context manger build_calls
        """
        with self.manager.build_calls('directory', \
                default_kwargs=dict(fields=u'users(customerId)', customer=self.manager.customerId, sortOrder=u'DESCENDING')) \
                as key_builder:

            key_builder('users').\
                function_list().\
                define_resolve_path("users.[0].customerId")

        with self.manager.build_calls(
            'admin-settings', \
                default_kwargs=dict(function=u'get', domainName=self.manager.domain), \
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
                post_callback(self.creation_time_callback)
            key_builder('countryCode')
            key_builder('mxVerification')
            key_builder('ssoGeneral')
            key_builder('ssoSigningKey')
            key_builder('userEmailMigrationEnabled')
            key_builder('outboundGateway')

    def doGetUserInfo(self, user, noaliases, nogroups, noschemas, userview, nolicenses):
        """
        Build the Google Calls abstractly and then get the information itemized under Key Builders
        The result will be output to stdout, which happens at close of context manger build_calls
        TODO: Implement schemas as named parameter
        """
        if user.startswith('uid:'):
            user = user[ len('uid:')+1: ]
        if user == None:
            # This is here for reference, our code can't ever have user as None
            # but this is what GAM did when that occurred.
            user = self.credentials.id_token[u'email']
        elif user.find(u'@') == -1:
            user = u"{}@{}".format(user, self.manager.domain)

        getSchemas = getAliases = getGroups = getLicenses = True
        projection = u'full'
        customFieldMask = viewType = None

        # FIXME: Implement schemas as a named parameter in cli instead
        schemas = False
        projection = 'basic' if noschemas else 'custom' if schemas else 'domain_public' if userview else 'full'
        if projection == 'custom':
            # TODO: Looks like we need to implement a named parameter in case of schemas
            customFieldMask = None

        with self.manager.build_calls(
            'directory', \
                default_kwargs=dict(userKey=user, projection=projection, customFieldMask=customFieldMask, viewType=viewType)
            ) as key_builder:

            key_builder('users').\
                define_sub_keys(['name.givenName', 'name.familyName', 'isAdmin', 'isDelegatedAdmin', 'agreedToTerms', 'ipWhitelisted', 
                'suspended', 'suspensionReason', 'changePasswordAtNextLogin', 'id', 'customerId', 'isMailboxSetup', 'includeInGlobalAddressList',
                'creationTime', 'lastLoginTime', 'orgUnitPath', 'thumbnailPhotoUrl', 'ims', 'addresses', 'organizations', 'phones', 'emails', 
                'relations', 'externalIds', 'customSchemas', 'aliases']).\
                sub_key_post('lastLoginTime', lambda result: 'Never' if result == '1970-01-01T00:00:00.000Z' else result)

