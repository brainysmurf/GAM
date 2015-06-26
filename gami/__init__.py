from output_parser import IndentedTextParser
from named_param import CreateNamedCmd
from actions import Actions
from manager import Manager, MockManager
from resolver import resolver

def run_gami_from_string(command_string, jsonify=True, *args, **kwargs):
	"""
	Runs the command, and, by default, returns the result as a useful pyton dictionary
	"""
	from gami import RunGami
	r = RunGami(jsonify=jsonify, *args, **kwargs)
	return r.command_from_string(command_string)

__all__ = [IndentedTextParser, CreateNamedCmd]