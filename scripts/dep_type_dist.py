"""
Computes the dependency type distributions.

@author: Hardik
"""

import argparse
import csv
import logging
import os
import sys
sys.path.insert(1, os.path.join(sys.path[0], os.path.join('..', 'src')))

from collocates import CollocatesManager
from corpus import CorpusManager
from dependency import TYPES
from ranks import RANK_GROUPS
from role import ROLES


# Configure logging
logging.basicConfig(format="%(levelname)s: [%(asctime)s] %(message)s",
	level=logging.INFO)


def main():
	parser_description = ("Computes the dependency type distributions.")
	parser = argparse.ArgumentParser(description=parser_description)

	parser.add_argument('out_dirpath', help="Path to output directory for "
		"generated .tsv files")
	
	args = parser.parse_args()

	collocates_manager = CollocatesManager()
	corpus_manager = CorpusManager()
	
	# Get publication dates for all stories.
	dates = corpus_manager.get_dates()
	# Story Id's.
	sids = dates.keys()

	# Create the output directory if it doesn't already exist.
	if not os.path.exists(args.out_dirpath):
		os.makedirs(args.out_dirpath)

	for rg in RANK_GROUPS:
		rg_name, ranks = rg

		path = os.path.join(args.out_dirpath, '%s.tsv' % (rg_name.lower()))

		logging.info("Calculating for %s... (Outputting to %s)" %
			(rg_name, path))

		with open(path, 'wb') as f:
			writer = csv.writer(f, delimiter='\t', quotechar='"')

			# Write header.
			writer.writerow(['STORY ID', 'PUB. DATE', 'GENRE'] +
				['# %s' % t.upper() for t in TYPES])

			for sid in sids:
				if not collocates_manager.saved(sid, tpe='character'):
					logging.info("Skipping %s..." % sid)
					continue

				genre = (None if sid.startswith('000') else
					corpus_manager.get_genre(sid))
				row = [sid, dates[sid], genre if genre else 'DNE']

				collocates = collocates_manager.get(sid, tpe='character',
					ranks=ranks)

				for t in TYPES:
					row.append(len([coll for coll in collocates
									if coll['type'] == t]))
				
				writer.writerow(row)


if __name__ == '__main__':
	main()
