"""
Calculates the proportion of collocates in stories that are "body", "clothes",
"motion", "physical", "sense", and "value" words, outputting the results to
.tsv files.

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
from role import ROLES


# Configure logging
logging.basicConfig(format="%(levelname)s: [%(asctime)s] %(message)s",
	level=logging.INFO)


# Filepaths to dictionaries.
BODY_DICT_PATH = "../resources/dict_body.csv"
CLOTHES_DICT_PATH = "../resources/dict_clothes.csv"
MOTION_DICT_PATH = "../resources/dict_motion.csv"
PHYSICAL_DICT_PATH = "../resources/dict_physical_attributes.csv"
SENSE_DICT_PATH = "../resources/dict_sense.csv"
VALUES_DICT_PATH = "../resources/dict_values.csv"


# Returns a set of "body" words.
def load_body():
	with open(BODY_DICT_PATH) as f:
		return set([l.strip() for l in f])

# Returns a set of "clothes" words.
def load_clothes():
	with open(CLOTHES_DICT_PATH) as f:
		return set([l.strip() for l in f])

# Returns a set of "motion" words.
def load_motion():
	with open(MOTION_DICT_PATH) as f:
		return set([l.strip() for l in f])

# Returns a set of "physical" words.
def load_physical():
	with open(PHYSICAL_DICT_PATH) as f:
		reader = csv.reader(f, delimiter=',', quotechar='"')

		return set([row[0] for row in reader])

# Returns a set of "sense" words.
def load_sense():
	with open(SENSE_DICT_PATH) as f:
		reader = csv.reader(f, delimiter=',', quotechar='"')

		return set([row[0] for row in reader])

# Returns a set of "value" words.
def load_value():
	with open(VALUES_DICT_PATH) as f:
		return set([l.strip() for l in f])


def main():
	parser_description = ("Calculates the proportion of collocates in stories"
		" that are \"body\", \"clothes\", \"motion\", \"physical\", "
		"\"sense\", and \"value\" words, outputting the results to .tsv files.")
	parser = argparse.ArgumentParser(description=parser_description)

	parser.add_argument('out_dirpath', help="Path to output directory for "
		"generated .tsv files")
	
	args = parser.parse_args()

	# Add None for considering all roles.
	roles = [None] + ROLES

	collocates_manager = CollocatesManager()
	corpus_manager = CorpusManager()
	
	# Get publication dates for all stories.
	dates = corpus_manager.get_dates()
	# Story Id's.
	sids = corpus_manager.get_ids(origin='gen')

	# Create the output directory if it doesn't already exist.
	if not os.path.exists(args.out_dirpath):
		os.makedirs(args.out_dirpath)

	body_words = load_body()
	clothes_words = load_clothes()
	motion_words = load_motion()
	physical_words = load_physical()
	sense_words = load_sense()
	value_words = load_value()

	for rg in RANK_GROUPS:
		for role in roles:
			rg_name, ranks = rg

			role_name = role.lower() if role else 'all'
			path = os.path.join(args.out_dirpath, '%s-%s.tsv' % (role_name,
				rg_name.lower()))

			logging.info("Calculating for %s... (Outputting to %s)" %
				(rg_name, path))

			with open(path, 'wb') as f:
				writer = csv.writer(f, delimiter='\t', quotechar='"')

				# Write header.
				writer.writerow(['STORY ID', 'PUB. DATE', 'GENRE',
					'EMBODIMENT', 'CLOTHES', 'MOTION', 'PHYSICAL', 'PERCEPTION',
					'VALUATION'])

				for sid in sids:
					if not collocates_manager.saved(sid, tpe='character'):
						logging.info("Skipping %s..." % sid)
						continue

					genre = (None if sid.startswith('000') else
						corpus_manager.get_genre(sid))
					
					try:
						collocates = collocates_manager.get(sid, tpe='character',
							role=role, ranks=ranks)

						num_body_collocates = len([coll for coll in collocates
							if coll['token']['word'] in body_words])

						num_clothes_collocates = len([coll for coll in collocates
							if coll['token']['word'] in clothes_words])

						num_motion_collocates = len([coll for coll in collocates
							if coll['token']['word'] in motion_words])

						num_physical_collocates = len([coll for coll in collocates
							if coll['token']['word'] in physical_words])

						num_sense_collocates = len([coll for coll in collocates
							if coll['token']['word'] in sense_words])

						num_value_collocates = len([coll for coll in collocates
							if coll['token']['word'] in value_words])

						if len(collocates) > 0:
							row = [sid, dates[sid] if sid in dates else 'DNE',
								genre if genre else 'DNE',
								float(num_body_collocates) / len(collocates),
								float(num_clothes_collocates) / len(collocates),
								float(num_motion_collocates) / len(collocates),
								float(num_physical_collocates) / len(collocates),
								float(num_sense_collocates) / len(collocates),
								float(num_value_collocates) / len(collocates)]
						else:
							row = [sid, dates[sid] if sid in dates else 'DNE',
								genre if genre else 'DNE'] + ([0.0] * 6)

						writer.writerow(row)
					except IndexError:
						logging.info("Skipping %s..." % sid)
	
if __name__ == '__main__':
	main()
