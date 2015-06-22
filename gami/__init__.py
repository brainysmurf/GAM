from output_parser import IndentedTextParser
from gami import RunGami

def run_gami_from_string(command_string, jsonify=True, *args, **kwargs):
	"""
	Runs the command, and, by default, returns the result as a useful pyton dictionary
	"""
	r = RunGami(jsonify=jsonify, *args, **kwargs)
	return r.command_from_string(command_string)


__all__ = [RunGami, IndentedTextParser]