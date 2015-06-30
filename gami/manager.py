"""

"""
import contextlib, os, sys, json
from collections import defaultdict
import click
import resolver

from gami.const import __pathtogami__

# Local Imports
import googleapiclient.errors
import httplib2
import googleapiclient
import googleapiclient.discovery
import googleapiclient.errors
import googleapiclient.http
import oauth2client.client
import oauth2client.file
import oauth2client.tools
import uritemplate


global true_values, false_values, extra_args, customerId, domain, usergroup_types, is_frozen
is_frozen = getattr(sys, 'frozen', '')
extra_args = {u'prettyPrint': False}
true_values = [u'on', u'yes', u'enabled', u'true', u'1']
false_values = [u'off', u'no', u'disabled', u'false', u'0']
usergroup_types = [u'user', u'users', u'group', u'ou', u'org',
                                     u'ou_and_children', u'ou_and_child', u'query',
                                     u'license', u'licenses', u'file', u'all',
                                     u'cros']


class Key(object):

    def __init__(self, key, builder):
        self.key = key
        self.sub_keys = None
        self.sub_key_post_dict = {}
        self.api = builder.manager.api
        self.service = getattr(builder.manager.service, key)()   # determine service FIXME: validate, send back useful error
        self.builder = builder
        self.default = None
        self.post = None

        # set the defaults
        self.kwargs = self.builder._default_kwargs
        self.resolve_path = builder._default_resolve_path

    def define_sub_keys(self, subkeys):
        self.sub_keys = subkeys
        return self

    def sub_key_post(self, subkey, callback):
        self.sub_key_post_dict[subkey] = callback
        return self

    def define_kwarg(self, key, value):
        self.kwargs[key] = value
        return self

    def define_kwargs(self, **kwargs):
        self.kwargs = kwargs
        return self

    def update_kwarg(self, **kwarg):
        self.kwargs.update(kwarg)
        return self

    def function_list(self):
        self.define_kwarg('function', 'list')

    def function_send(self):
        self.define_kwarg('function', 'send')
        return self

    def set_default(self, value):
        """
        If this value is non-None, indicates that this is what should be returned and no calls are made
        """
        self.default = value
        return self

    def unpack_lambda(self, this_lambda):
        self.unpack = this_lambda
        return self

    def post_callback(self, callback):
        self.post = callback

    def unpack_list(self, lst):
        self._unpack_list = lst
        return self

    def define_resolve_path(self, resolve_path):
        self.resolve_path = resolve_path
        return self


class KeyBuilder(object):

    def __init__(self, manager):
        self.keys = []
        self.manager = manager

    def add_key(self, key):
        item = Key(key, self)
        self.keys.append(item)
        return item

    @contextlib.contextmanager
    def defaults_block(self):
        self._default_kwargs = self.manager.default_kwargs
        self._default_resolve_path = self.manager.default_resolve_path
        yield self

    def define_kwarg(self, key, value):
        self._default_kwargs[key] = value
        return self

    def default_resolve_path(self, path):
        self._default_resolve_path = path
        return self

    def default_kwargs(self, **kwargs):
        self._default_kwargs = kwargs
        return self

    def default_resolve_path(self, path):
        self._default_resolve_path = path
        return self


class Manager(object):
    results_key = 'results'
    error_key = 'errors'
    warning_key = 'warnings'

    def __init__(self, default_resolve_path=None, default_kwargs=None, mock=False):
        self.mock = mock
        self.key_builder = None
        self.credentials = None
        self._path_to_gam = None
        self.result = None
        self.default_resolve_path = default_resolve_path
        self.default_kwargs = default_kwargs
        self.complete_results = {self.results_key:{}, self.error_key:defaultdict(list), self.warning_key:defaultdict(list)}
        self.init()

    def gam_path(self, after):
        """
        Convenience function
        """
        return "{}{}".format(self.path_to_gam, after)

    @property
    def path_to_gam(self):
        """
        Put this in gami.__init__, and import it instead
        """
        if self._path_to_gam is None:
            self._path_to_gam = __pathtogami__
        return self._path_to_gam

    def init(self):
        """
        Sets up self.credentials, self.domain, self.customerId ... and self.http
        TODO: Get rid of global variables
        """

        # Set up common stuff, whether config happens through environ variables or elsewise
        oauth2file = self.gam_path(os.environ.get(u'OAUTHFILE')) if os.environ.get(u'OAUTHFILE') else self.gam_path(u'oauth2.txt')

        storage = oauth2client.file.Storage(oauth2file)
        self.credentials = storage.get()
        if self.credentials is None or self.credentials.invalid:
            # TODO: What about mock siutation?
            doRequestOAuth()
            self.credentials = storage.get()
            #TODO: Change this user agent stuff
            self.credentials.user_agent = u'GAM %s - http://git.io/gam / %s / Python %s.%s.%s %s / %s %s /' % (__version__, __author__,
                       sys.version_info[0], sys.version_info[1], sys.version_info[2], sys.version_info[3],
                       platform.platform(), platform.machine())
        disable_ssl_certificate_validation = False
        if os.path.isfile(self.gam_path('noverifyssl.txt')):
            disable_ssl_certificate_validation = True
        cache = None
        if not os.path.isfile(self.gam_path('nocache.txt')):
            cache = self.gam_path(u'%sgamcache')
        http = httplib2.Http(ca_certs=self.gam_path(u'cacert.pem'), disable_ssl_certificate_validation=disable_ssl_certificate_validation, cache=cache)
        if os.path.isfile(self.gam_path('debug.gam')):
            httplib2.debuglevel = 4
            extra_args[u'prettyPrint'] = True
        if os.path.isfile(self.gam_path(u'extra-args.txt')):
            import ConfigParser
            config = ConfigParser.ConfigParser()
            config.optionxform = str
            config.read(self.gam_path(u'extra-args.txt'))
            extra_args.update(dict(config.items(u'extra-args')))
        self.http = self.credentials.authorize(http)

        if os.environ.get('GA_DOMAIN'):
            # config from environment variables
            # NOTE: I am not sure why we really need this
            self.domain = os.environ[u'GA_DOMAIN']
            version = self.getAPIVer(self.api)

            try:
                service = googleapiclient.discovery.build(self.api, version, http=http)
            except googleapiclient.errors.UnknownApiNameOrVersion:
                disc_file = getGamPath()+u'%s-%s.json' % (self.api, version)
                if os.path.isfile(disc_file):
                    f = file(disc_file, 'rb')
                    discovery = f.read()
                    f.close()
                    service = googleapiclient.discovery.build_from_document(discovery, base=u'https://www.googleapis.com', http=http)
                else:
                    raise
            except httplib2.CertificateValidationUnsupported:
                print u'Error: You don\'t have the Python ssl module installed so we can\'t verify SSL Certificates. You can fix this by installing the Python SSL module or you can live on the edge and turn SSL validation off by creating a file called noverifyssl.txt in the same location as gam.exe / gam.py'
                sys.exit(8)   # nooo

            resp, customerId_result = service._http.request(u'https://www.googleapis.com/admin/directory/v1/users?domain=%s&maxResults=1&fields=users(customerId)' % domain)
            customerId_obj = json.loads(customerId_result)
            self.customerId = customerId_obj[u'users'][0][u'customerId']

        else:
            # config from credentials
            self.domain = self.credentials.id_token.get(u'hd') or u'Unknown'
            self.customerId = u'my_customer'

    def get_result_key(self, key):
        """
        Returns the value of key
        """
        return self.complete_results[self.results_key].get(key)

    def output(self):
        """
        
        """
        pprint = json.dumps(self.complete_results, sort_keys=True, indent=2)
        click.echo(pprint)

    def add_error(self, key, message):
        error_dict = {'error': {key:message}}
        self.complete_results.update(error_dict)

    def getAPIVer(self, api):
        return {
            'directory':'directory_v1',
            'reports':'reports_v1',
            'oauth2':'v2',
            'groupssettings':'v1',
            'calendar':'v3',
            'plus':'v1',
            'plusDomains':'v1',
            'drive':'v2',
            'licensing':'v1',
            'siteVerification':'v1',
            'gmail': 'v1',
            'appsactivity':'v1'
            }.get(api, 'v1')

    def buildGAPIObject(self, api):
        """
        Returns the service used in self.service
        """
        version = self.getAPIVer(api)
        if api in [u'directory', u'reports']:
            api = u'admin'
        try:
            service = googleapiclient.discovery.build(api, version, http=self.http)
        except googleapiclient.errors.UnknownApiNameOrVersion:
            disc_file = self.gam_path('{}-{}.json'.format(api, version))
            if os.path.isfile(disc_file):
                f = file(disc_file, 'rb')
                discovery = f.read()
                f.close()
                service = googleapiclient.discovery.build_from_document(discovery, base=u'https://www.googleapis.com', http=self.http)
            else:
                raise
        except httplib2.CertificateValidationUnsupported:
            print u'Error: You don\'t have the Python ssl module installed so we can\'t verify SSL Certificates. You can fix this by installing the Python SSL module or you can live on the edge and turn SSL validation off by creating a file called noverifyssl.txt in the same location as gam.exe / gam.py'
            sys.exit(8)
        return service

    @contextlib.contextmanager
    def output_block(self):
        yield self
        self.output()

    @contextlib.contextmanager
    def api_block(self, api, pages=False, output_on_close=False):
        """
        Sets up self.service
        yields a key builder which allows dev to build up a list of configuration
        that will be put out to Google APIs
        """
        self.api = api
        self.pages = pages

        self.service = self.buildGAPIObject(self.api)

        self.key_builder = KeyBuilder(self)
        yield self.key_builder

        self._calls = []
        for key in self.key_builder.keys:

            service = getattr(self.service, key.key)()
            self._calls.append( (key, key.kwargs) )

        ret = self.call_and_build()

        if self.results_key in ret:
            self.complete_results[self.results_key].update(ret[self.results_key])
        if self.error_key in ret:
            self.complete_results[self.error_key].update(ret[self.error_key])
        if self.warning_key in ret:
            self.complete_results[self.warning_key].update(ret[self.warning_key])

        if output_on_close:
            self.output()

        self.key_builder = None
        self.iobj = None
        self._calls = []

    def callGAPI(self, service, function=u"get", silent_errors=False, soft_errors=False, throw_reasons=[], retry_reasons=[], **kwargs):
        method = getattr(service, function)
        retries = 10
        parameters = dict(kwargs.items() + extra_args.items())
        for n in range(1, retries+1):
            try:
                return method(**parameters).execute()
            except googleapiclient.errors.HttpError, e:
                try:
                    error = json.loads(e.content)
                except ValueError:
                    if not silent_errors:
                        print u'ERROR: %s' % e.content
                    if soft_errors:
                        return
                    else:
                        sys.exit(5)
                http_status = error[u'error'][u'code']
                message = error[u'error'][u'errors'][0][u'message']
                try:
                    reason = error[u'error'][u'errors'][0][u'reason']
                except KeyError:
                    reason = http_status
                if reason in throw_reasons:
                    raise e
                if n != retries and (reason in [u'rateLimitExceeded', u'userRateLimitExceeded', u'backendError', u'internalError'] or reason in retry_reasons):
                    wait_on_fail = (2 ** n) if (2 ** n) < 60 else 60
                    randomness = float(random.randint(1,1000)) / 1000
                    wait_on_fail = wait_on_fail + randomness
                    if n > 3: sys.stderr.write(u'Temp error %s. Backing off %s seconds...' % (reason, int(wait_on_fail)))
                    time.sleep(wait_on_fail)
                    if n > 3: sys.stderr.write(u'attempt %s/%s\n' % (n+1, retries))
                    continue
                sys.stderr.write(u'Error %s: %s - %s\n\n' % (http_status, message, reason))
                if soft_errors:
                    if n != 1:
                        sys.stderr.write(u' - Giving up.\n')
                    return
                else:
                    sys.exit(int(http_status))
            except oauth2client.client.AccessTokenRefreshError, e:
                sys.stderr.write(u'Error: Authentication Token Error - %s' % e)
                sys.exit(403)
            except httplib2.CertificateValidationUnsupported:
                print u'\nError: You don\'t have the Python ssl module installed so we can\'t verify SSL Certificates.\n\nYou can fix this by installing the Python SSL module or you can live on dangerously and turn SSL validation off by creating a file called noverifyssl.txt in the same location as gam.exe / gam.py'
                sys.exit(8)
            except TypeError, e:
                print u'Error: %s' % e
                sys.exit(4)

    def callGAPIpages(self, service, function="get", items=u'items', nextPageToken=u'nextPageToken', page_message=None, message_attribute=None, **kwargs):
        pageToken = None
        while True:
            this_page = self.callGAPI(service=service, function=function, pageToken=pageToken, **kwargs)
            return this_page

    @property
    def last_result(self):
        """
        Provides a way to grab results for later processing
        TODO: 
        """
        return self.result

    def normalize_value(self, value):
        """
        Detect and see if value is a string, and convert it to python data formats if so
        """
        if not isinstance(value, str) and not isinstance(value, unicode):
            return value
        if value.isdigit():
            return int(value)
        else:
            return {u'true': True, u'false': False}.get(value.lower(), value)

    def call_and_build(self):
        ret = {self.results_key:{}}
        working = ret[self.results_key]
        for key, kwargs in self._calls:
            if self.pages:
                self.result = self.callGAPIpages(key.service, **kwargs)
            else:
                try:
                    self.result = self.callGAPI(key.service, **kwargs)
                except Exception as e:
                    ret['errors']['error':'An error occurred']
                    # TODO: make key name of kind of traceback
                    continue

            if key.sub_keys:
                for k in key.sub_keys:
                    try:
                        value = resolver.resolver(k, self.result)
                    except resolver.NotPresentInValue:
                        continue

                    subkey_post_callable = key.sub_key_post_dict.get(k)
                    if subkey_post_callable:
                        value = subkey_post_callable(value)

                    # Just use the last part of the resolve path
                    key_name = k.split('.')[-1]
                    working[key_name] = self.normalize_value(value)
            else:
                if '.' in key.key:
                    try:
                        value = resolver.resolver(key.key, self.result)
                    except resolver.NotPresentInValue:
                        ret[self.error_key]['notPresentNevermind'].append(key.key)
                        continue
                else:
                    try:
                        value = resolver.resolver(key.resolve_path, self.result)
                    except resolver.NotPresentInValue:
                        ret[self.error_key]['programming': "{} not in self.result, did you forget to set self.default_resolve_path to None?"]
                        continue

                if isinstance(value, dict):
                    working.update({k:self.normalize_value(v) for k,v in value.items()})
                elif isinstance(value, list):
                    working[key.key] = [self.normalize_value(v) for v in value]
                else:
                    if key.post:
                        value = key.post(value)
                    working[key.key] = self.normalize_value(value)
        return ret

class MockServiceCall(object):
    def __init__(self, name):
        self.name = name

    def __call__(self):
        pass

class MockService(object):
    """
    Just a stupid thing
    """
    def __getattr__(self, name):
        self.__dict__[name] = MockServiceCall(name)
        return self.__dict__[name]

class MockManager(Manager):
    def init(self):
        self.domain = 'domain'
        self.customerId = 'customerId'

    def callGAPI(self, service, function=u"get", silent_errors=False, soft_errors=False, throw_reasons=[], retry_reasons=[], **kwargs):
        pass

    def buildGAPIObject(self, api):
        self.api = api
        return MockService()

    def call_and_build(self):
        for key, kwargs in self._calls:
            self.output(key.api, key.key, str(kwargs))     