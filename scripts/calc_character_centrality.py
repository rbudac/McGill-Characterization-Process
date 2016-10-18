"""
Calculates character-based centrality measure for each story, saving the
results in a .tsv file.

@author: Hardik
"""

import argparse
import csv
import logging
import os
import sys
sys.path.insert(1, os.path.join(sys.path[0], os.path.join('..', 'src')))

from collections import Counter
from scipy import stats

from aliases import AliasesManager
from corpus import CorpusManager

# Configure logging
logging.basicConfig(format="%(levelname)s: [%(asctime)s] %(message)s",
	level=logging.INFO)


# Returns a counter of the number of mentions for the top 20 characters.
def get_alias_cnts(aliases):
	cntr = Counter()

	for alias in aliases:
		rank = alias['entity']['rank']
		if rank > 20:
			continue

		cntr[rank] += 1

	return cntr


def main():
	parser_description = ("Calculates character-based centrality measure for "
		"each story, saving the results in a .tsv file.")
	parser = argparse.ArgumentParser(description=parser_description)

	parser.add_argument('out_path', help="Output path to data .tsv file")

	args = parser.parse_args()

	aliases_manager = AliasesManager()
	corpus_manager = CorpusManager()
	
	logging.info("Getting story Id's and pub. dates...")
	# Get publication dates for all stories.
	dates = corpus_manager.get_dates()
	# Story Id's.
	sids = corpus_manager.get_ids(origin='gen')

	with open(args.out_path, 'wb') as f:
		writer = csv.writer(f, delimiter='\t', quotechar='"')

		# Write header.
		writer.writerow(['STORY ID', 'PUB. DATE', 'GENRE',
			'FIRST/SECOND RATIO', 'MAX. DIFF. RANK', 'MENTIONS SKEW'])
		
		for sid in sids:
			if not aliases_manager.saved(sid, tpe='character'):
				logging.info("Skipping %s..." % sid)
				continue
			
			genre = (None if sid.startswith('000') else
					corpus_manager.get_genre(sid, pretty=True))
			row = [sid, dates[sid] if sid in dates else 'DNE',
				genre if genre else 'DNE']

			aliases = aliases_manager.get_aliases(sid, tpe='character')
			cntr = get_alias_cnts(aliases)

			num_characters = len(cntr)

			ratio, max_diff_rank, skew = 'DNE', 'DNE', 'DNE'
			if num_characters > 1:
				# List of counts in order of character rank.
				cnts = [cnt for _, cnt
						in sorted(cntr.items(), key=lambda i: -i[1])]

				# Ratio of # mentions between the first and second
				# characters.
				ratio = (float(cnts[0]) / float(cnts[1]))

				# Rank of the maximum difference in mentions between
				# characters (in top 20, and not including the first character).
				max_diff_rank, max_diff = None, 0
				for i in range(1, num_characters - 1):
					diff = (cnts[i] - cnts[i + 1])

					if max_diff < diff:
						max_diff_rank, max_diff = i + 1, diff

				# Skew of the mention distribution of the top 20
				# characters.
				skew = stats.skew(cnts)

			row += [ratio, max_diff_rank, skew]

			writer.writerow(row)
		

if __name__ == '__main__':
	main()
