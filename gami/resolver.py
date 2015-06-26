"""
Resolver

Take a string 'resolve' and a value and resolve it, duh

"""
class NotPresentInValue(Exception):
	pass

import re
BRACESSTARTEND = '^\[(.*)\]$'

def resolver(resolve_keys, value):
	split = resolve_keys.split('.')
	for substring in split:
		match = re.match(BRACESSTARTEND, substring)
		if match:
			inside = match.group(1)
			if inside.isdigit():
				value = value[int(match.group(1))]
			else:
				value = value[match.group(1)]   # TODO throw error instead: resolver expects [blah] blah to be an int"
		else:
			try:
				value = value[substring]
			except KeyError:
				raise NotPresentInValue('key {} is not contained in the value {}'.format(substring, value))
	return value

if __name__ == "__main__":

	value = resolve('name.do.this.[0]', {'name':{'do':{'this':['value']}}})
	# value = 'value'