"""
Manages character rank groups of interest.

@author: Hardik
"""

# List of roles.
RANK_GROUPS = [
	# Top character.
	('Top', range(1, 2)),
	# Top 2 characters.
	('Top-2', range(1, 3)),
	# Top 5 characters.
	('Top-5', range(1, 6)),
	# Top 20 characters.
	('All', range(1, 21))
	# Temporarily commented out.
	# # Top 20 characters minus the first.
	# ('2-20', range(2, 21)),
	# # Top 20 characters minus the first two.
	# ('3-20', range(3, 21)),
	# # Top 20 characters minus the top 5.
	# ('5-20', range(6, 21))
]
