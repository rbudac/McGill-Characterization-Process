"""
Calculates the # of character mentions and scaled characters for various ranking
groups for stories, outputting the results to .tsv files.

@author: Hardik
"""

import argparse
import csv
import logging
import os
import sys
sys.path.insert(1, os.path.join(sys.path[0], os.path.join('..', 'src')))

from collections import Counter

from aliases import AliasesManager
from corpus import CorpusManager
from ranks import RANK_GROUPS


# Configure logging
logging.basicConfig(format="%(levelname)s: [%(asctime)s] %(message)s",
	level=logging.INFO)


# Returns a the number of mentions for characters with the given ranks.
def get_num_mentions(aliases, ranks):
	ranks = set(ranks)
	return len([al for al in aliases if al['entity']['rank'] in ranks])


def main():
	parser_description = ("Calculates the # of character mentions and scaled "
		"characters for various ranking groups for stories, outputting the "
		"results to .tsv files.")
	parser = argparse.ArgumentParser(description=parser_description)

	parser.add_argument('out_dirpath', help="Path to output directory for "
		"generated .tsv files")

	args = parser.parse_args()

	aliases_manager = AliasesManager()
	corpus_manager = CorpusManager()
	
	# Get word counts for all stories.
	logging.info("Getting word counts...")
	wcs = corpus_manager.get_wcs()
	# Story Id's.
	sids = wcs.keys()

	# Create the output directory if it doesn't already exist.
	if not os.path.exists(args.out_dirpath):
		os.makedirs(args.out_dirpath)

	for rg in RANK_GROUPS:
		rg_name, ranks = rg

		path = os.path.join(args.out_dirpath, '%s.tsv' % rg_name.lower())

		logging.info("Calculating for %s... (Outputting to %s)" %
			(rg_name, path))

		with open(path, 'wb') as f:
			writer = csv.writer(f, delimiter='\t', quotechar='"')

			# Write header.
			writer.writerow(['STORY ID', '# MENTIONS PER 100000 WORDS',
				'# CHAR. PER 100000 WORDS'])

			for sid in sids:
				if not aliases_manager.saved(sid, tpe='character'):
					logging.info("Skipping %s..." % sid)
					continue

				aliases = aliases_manager.get_aliases(sid, tpe='character')

				row = [sid,
					get_num_mentions(aliases, ranks) * 100000 / float(wcs[sid]),
					float(len(ranks)) * 100000 / wcs[sid]]
				
				writer.writerow(row)


if __name__ == '__main__':
	main()
