"""
Calculates the abstraction score and objectivity of characters in stories (as
the percentage of collocates that are "abstract" and "physical" words,
respectively), outputting the results to .tsv files.

@author: Hardik
"""

import argparse
import csv
import logging
import os
import sys
sys.path.insert(1, os.path.join(sys.path[0], os.path.join('..', 'src')))

from nltk.stem import WordNetLemmatizer

from collocates import CollocatesManager
from corpus import CorpusManager
from ranks import RANK_GROUPS
from role import ROLES


# Configure logging
logging.basicConfig(format="%(levelname)s: [%(asctime)s] %(message)s",
	level=logging.INFO)


# Filepath to "abstract" words.
ABSTRACT_PATH = "../resources/abstract.txt"
# Filepath to "physical" words.
PHYSICAL_PATH = "../resources/physical.txt"


# Returns a set of words from the file, lemmatized.
def load_words(filepath):
	words = []
	with open(filepath) as f:
		for line in f:
			words.append(line.strip().replace(' ', '-'))

	lemmatizer = WordNetLemmatizer()

	# Lemmatize and convert to set.
	return set([lemmatizer.lemmatize(w) for w in words])


def main():
	parser_description = ("Calculates the sociability of characters in "
		"stories (as the percentage of collocates that are \"said\" words), "
		"outputting the results to .tsv files.")
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

	abstract_words = load_words(ABSTRACT_PATH)
	physical_words = load_words(PHYSICAL_PATH)

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
					'ABSTRACTIVITY', 'OBJECTIVITY'])

				for sid in sids:
					if not collocates_manager.saved(sid, tpe='character'):
						logging.info("Skipping %s..." % sid)
						continue

					genre = (None if sid.startswith('000') else
						corpus_manager.get_genre(sid))
					
					collocates = collocates_manager.get(sid, tpe='character',
						role=role, ranks=ranks)
					
					num_abstract_collocates = len([coll for coll in collocates
						if coll['token']['lemma'] in abstract_words])

					num_physical_collocates = len([coll for coll in collocates
						if coll['token']['lemma'] in physical_words])

					row = [sid, dates[sid] if sid in dates else 'DNE',
						genre if genre else 'DNE',
						float(num_abstract_collocates) / len(collocates)
						if len(collocates) > 0 else 0.0,
						float(num_physical_collocates) / len(collocates)
						if len(collocates) > 0 else 0.0]
						
					writer.writerow(row)
	
if __name__ == '__main__':
	main()
