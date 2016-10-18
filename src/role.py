"""
Manages entity roles.

@author: Hardik
"""

# List of roles.
ROLES = ['PREDICATE', 'AGENT', 'PATIENT', 'POSESSOR']


def map_role(rel):
	"""
	Maps a dependency relation type to a role: PREDICATE, AGENT, PATIENT,
	or POSESSOR.
	
	@param rel - Dependency relation type (Outlined in dependency)
	@return Role
	"""

	if rel == 'acomp' or rel == 'amod' or rel == 'appos' or \
		rel == 'nsubj-adj' or rel == 'nsubj-noun' or rel == 'nmod:of':
		return 'PREDICATE'
	elif rel == 'agent' or rel.startswith('nsubj') or rel == 'pobj':
		return 'AGENT'
	elif rel.startswith('dobj') or rel.startswith('iobj'):
		return 'PATIENT'
	elif rel.startswith('poss'):
		return 'POSESSOR'
