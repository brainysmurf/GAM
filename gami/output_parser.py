
import re, collections

LineParser = collections.namedtuple('LineParser', ['label', 'value', 'level'])

class IndentedTextParser(object):
	sep = ":"
	SPLITPATTERN= '^\W*(.*?)\W*' + sep + '\W*(.*?)$'
	WHITESPACEATSTART = '^\W*'

	@classmethod
	def dict_insert(cls, adict, key, val):
	    """
	    """
	    if key in adict:
	    	if key and val:
	    		if not isinstance(adict[key], list):
		    		# make it a list
		    		adict[key] = [adict[key]]
		        adict[key].append(val)
	    else:
	        adict[key] = val

	@classmethod
	def ttree_to_json(cls, ttree, level=0):
	    result = {}
	    for i in range(0, len(ttree)):
	        node = ttree[i]
	        try:
	            next_node  = ttree[i+1]
	        except IndexError:
	            next_node = LineParser(node.label, node.value, "-1")

	        # Edge cases
	        if node.level > level:
	            continue
	        if node.level < level:
	            return result

	        # Recursion
	        if next_node.level == level:
	            cls.dict_insert(result, node.label, node.value)
	        elif next_node.level > level:
	            rr = cls.ttree_to_json(ttree[i+1:], level=next_node.level)
	            cls.dict_insert(result, node.label, rr)
	        else:
	            cls.dict_insert(result, node.label, node.value)
	            return result
	    return result

	@staticmethod
	def convert_from_camel_case(name):
	    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
	    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower().replace(' ', '')

	def parse(self, string):
		"""
		Convert indented, colon-separated
		"""

		# First pass gives us a ttree
		ttree = []
		for line in string.split('\n'):
			if not line:
				continue
			if ':' in line:
				_, label, value, _ = re.split(self.SPLITPATTERN, line)
			else:
				label = line
				value = ""

			# determine level by the number of spaces at start
			# FIXME: Could use regex WHITEESPACESTART for whitespace/tabs, but this is much simpler
			#level = len(line)- len(line.lstrip(' '))
			whitespace_start = re.search(self.WHITESPACEATSTART, line)
			if whitespace_start:
				# since the regex pattern includes start of newline ^ character
				# we can assume that end() is the level
				level = whitespace_start.end()
			else:
				level = 0

			# make the label python-friendly as a key
			label = self.convert_from_camel_case(label)
			# make the value python-friendly as a value
			if value == "":
				value = None
			elif value.lower() == 'true':
				value = True
			elif value.lower() == 'false':
				value = False
			elif value.isdigit():
				value = int(value)

			# append
			ttree.append( LineParser(label, value, level) )

		# TODO: Validate that the levels are mathematically okay

		return self.__class__.ttree_to_json(ttree)

if __name__ == "__main__":

	s = """
Group Settings:
 nonEditableAliases:
  it.committee@example.com.test-google-a.com
 name: IT Committee
 adminCreated: True
 directMembersCount: 4
 email: it.committee@example.com
 id: 02dlolyb3m3n0ki
 description: AC, AM, GD, JC, SH
 allowExternalMembers: false
 whoCanJoin: CAN_REQUEST_TO_JOIN
 whoCanViewMembership: ALL_IN_DOMAIN_CAN_VIEW
 defaultMessageDenyNotificationText:
 includeInGlobalAddressList: true
 archiveOnly: false
 isArchived: true
 membersCanPostAsTheGroup: false
 allowWebPosting: true
 messageModerationLevel: MODERATE_NONE
 replyTo: REPLY_TO_IGNORE
 customReplyTo:
 sendMessageDenyNotification: false
 whoCanContactOwner: ANYONE_CAN_CONTACT
 messageDisplayFont: DEFAULT_FONT
 whoCanLeaveGroup: ALL_MEMBERS_CAN_LEAVE
 whoCanPostMessage: ALL_IN_DOMAIN_CAN_POST
 whoCanInvite: ALL_MEMBERS_CAN_INVITE
 spamModerationLevel: MODERATE
 whoCanViewGroup: ALL_IN_DOMAIN_CAN_VIEW
 showInGroupDirectory: false
 maxMessageBytes: 5M
 allowGoogleCommunication: false
Members:
 member: someone@example.com (user)
 member: someoneelse@example.com (user)
 member: xsomeone@example.com (user)
 member: ysomeone@example.com (user)
	"""
	i = IndentedTextParser()
	r = i.parse(s)
	from IPython import embed
	embed()