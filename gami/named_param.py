"""
GAM has a lot of "Named Parameters"
where the label and value is defined by separation of spaces
this wreaks havoc on our parser :(
hence the need to find a workaround
"""

import click
import contextlib, collections

class CreateNamedCmd(click.Command):
	"""
	Implements named parameters after this command
	Works by turning on "allow_extra_args" and then processing
	Requires some boilerplate in the callback, but that works for us so far

	Values of named parameters are accessible via returned "values" named tuple
	"""
	required_param_upper = True

	def __init__(self, named_params, **kwargs):
		self.named_params = named_params
		if not 'context_settings' in kwargs:
			kwargs['context_settings'] = {}
		kwargs['context_settings']['allow_extra_args'] = True
		super(CreateNamedCmd, self).__init__(**kwargs)

		# Here change help stuff
		# Have to do it by monkey-patching
		if self.params:
			last_param = self.params[-1]
			self.save_metavar = last_param.make_metavar()
			last_param.make_metavar = self.monkey_patch_metavar


	def monkey_patch_metavar(self):
		ret = []
		for param in self.named_params:	
			if not ':' in param:
				if self.required_param_upper and param == param.lstrip('-'):
					param = param.upper()

				ret.append(param + " <{}>".format(param.lstrip('-').lower()))
			else:
				param, tbd = param.split(':')     # tbd = to be decided, need to process what is there
				if tbd in ['+','-']:
					# it's a boolean
					ret.append( param + " <{}|{}>".format('ON' if tbd == "+" else 'on', 'OFF' if tbd == '-' else "off") )
				elif ',' in tbd:
					ret.append( param + " <{}>".format("|".join(tbd.split(','))))

		return "{} {}".format(self.save_metavar, " ".join(ret))

		return self.save_metavar + " " + " ".join(param for param in self.named_params)

	@staticmethod
	def truthy(key, value, default_value):
		"""
		Validates and return normalized value: True for every accepted "true" value, false for every accepted false value
		Also returns default_value if value is None...
		"""
		if value == None:
			return default_value
		value = value.lower().strip()
		ret1 = value in ['on', 'yes', 'true']
		ret2 = value in ['off', 'no', 'false']
		if ret1:
			return True
		if ret2:
			return False
		raise click.UsageError('Parameter "{}" was passed unrecognized value "{}"'.format(key, value))

	@staticmethod
	def oneof(key, value, canbe=[]):
		"""
		Validates and returns normalized value
		"""
		if value is None:
			return None
		value = value.lower().strip()
		if not value in canbe:
			raise click.UsageError('Parameter "{}" is "{}", but needs to be one of "{}"'.format(key, value, str(canbe)))
		return value

	@staticmethod
	def strip_extra(extra):
		e = extra[:]
		e = e.lstrip('-')
		if ':' in e:
			e, _ = e.split(':')
		return e

	@contextlib.contextmanager
	def validate_params(self, ctx):
		"""
		"""	

		values = collections.namedtuple('Extras', [self.strip_extra(e) for e in self.named_params])
		for param in self.named_params:

			# process the keys
			is_optional = param.startswith('--')
			key = self.strip_extra(param)

			try:
				where = ctx.args.index(key) + 1
				value = ctx.args[where]
			except ValueError:
				# Key is not located withing ctx.args
				if not is_optional:
					raise click.UsageError("Named parameter '{}' is required".format(param), ctx=ctx)
				else:
					value = None

			if ':' in param:
				_, tbd = param.split(':')     # tbd = to be decided, need to process what is there
				if tbd in ['+','-']:
					# it's a boolean
					value = self.truthy(key, value, {'+':True, '-':False}.get(tbd, False))
				elif ',' in tbd:
					value = self.oneof(key, value, tbd)

			setattr(values, key, value)


		# for item in truthy:
		# 	setattr(values, item, self.truthy(item, getattr(values, item)))
		# for key, canbe in oneof:
		# 	value = getattr(values, key)
		# 	self.oneof(key, value, canbe)
		yield values