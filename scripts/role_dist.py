"""
Computes the role distributions.

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
from ranks import RANK_GROUPS
from role import map_role, ROLES


# Configure logging
logging.basicConfig(format="%(levelname)s: [%(asctime)s] %(message)s",
	level=logging.INFO)


def main():
	parser_description = ("Computes the role distributions.")
	parser = argparse.ArgumentParser(description=parser_description)

	parser.add_argument('out_dirpath', help="Path to output directory for "
		"generated .tsv files")
	
	args = parser.parse_args()

	collocates_manager = CollocatesManager()
	corpus_manager = CorpusManager()
	
	# Get publication dates for all stories.
	dates = corpus_manager.get_dates()
	# Story Id's.
	sids = corpus_manager.get_ids(origin='gen')

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
				['# %s' % r for r in ROLES])

			for sid in sids:
				if not collocates_manager.saved(sid, tpe='character'):
					logging.info("Skipping %s..." % sid)
					continue

				genre = (None if sid.startswith('000') else
					corpus_manager.get_genre(sid))
				row = [sid, dates[sid] if sid in dates else 'DNE',
					genre if genre else 'DNE']

				try:
					collocates = collocates_manager.get(sid, tpe='character',
						ranks=ranks)

					for role in ROLES:
						row.append(len([coll for coll in collocates
										if map_role(coll['type']) == role]))
										
					writer.writerow(row)
				except IndexError:
					logging.info("Skipping %s..." % sid)
					continue
	
if __name__ == '__main__':
	main()
