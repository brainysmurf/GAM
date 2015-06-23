import click
import contextlib, collections

class CreateNamedCmd(click.Command):
	"""
	Implements named parameters after this command
	Works by turning on "allow_extra_args" and then processing
	Requires some boilerplate in the callback, but that works for us so far

	Can make required or optional named parameters
	"--" in front of name indicates it is optional

	Values of named parameters are accessible via returned "values" named tuple
	"""
	def __init__(self, **kwargs):
		if not 'context_settings' in kwargs:
			kwargs['context_settings'] = {}
		kwargs['context_settings']['allow_extra_args'] = True
		super(CreateNamedCmd, self).__init__(**kwargs)

	@contextlib.contextmanager
	def validate_named(self, ctx, extras=[]):
		values = collections.namedtuple('Extras', [e.lstrip('--') for e in extras])
		for extra in extras:
			is_optional = extra.startswith('--')
			key = extra.lstrip('--')
			try:
				where = ctx.args.index(extra) + 1
				setattr(values, key, ctx.args[where])
			except ValueError:
				if not is_optional:
					raise click.UsageError("Named parameter '{}' is required".format(extra), ctx=ctx)
				else:
					setattr(values, key, None)
		yield values