"""
Generates the nouns .json file for each story with a CoreNLP .xml and character
aliases .json file, in the corpus.

@author: Hardik
"""

import argparse
import logging
import os
import sys
sys.path.insert(1, os.path.join(sys.path[0], os.path.join('..', 'src')))

from collections import defaultdict
from multiprocessing import Process

from corpus import CorpusManager
from nouns import NounsManager


# Configure logging
logging.basicConfig(format="%(levelname)s: [%(asctime)s] %(message)s",
	level=logging.INFO)


# Global corpus manager.
corpus_manager = CorpusManager()


def aliases_saved(sid):
	"""
	Checks if the character aliases for the given story have been generated.

	@param sid - Story id of story
	@return True if the character aliases .json exists and False otherwise
	"""

	if not corpus_manager.belongs(sid):
		raise ValueError(sid +
			" does not correspond to a story in the corpus.")

	dirpath = corpus_manager.get_dirpath(sid)
	aliases_dirpath = os.path.join(dirpath, 'aliases')

	# Ripping this out. Note: disabling sub corpus stuff. -Rob
	#if sid == 'a-tale-of-two-cities' or sid == 'peregrine-pickle' or \
	#	sid == 'pride-and-prejudice' or sid == 'to-the-lighthouse' or \
	#	sid == 'tristram-shandy':
	return os.path.exists(os.path.join(aliases_dirpath, 'character.json'))
	# Assume story is in piper corpus.
	#else:
	#	return os.path.exists(os.path.join(os.path.join(aliases_dirpath,
	#		'character'), sid + '.json'))


def main():
	parser_description = ("Generates the nouns .json file for each story with "
		"a CoreNLP .xml and character aliases .json file, outputting to a.json "
		"file (If it doesn't already exist).")
	parser = argparse.ArgumentParser(description=parser_description)

	parser.add_argument('n', help="# worker threads to spawn", type=int)

	parser.add_argument('-f', '--force', dest='force', action='store_true',
		help="Force re-extraction")

	args = parser.parse_args()

	nouns_manager = NounsManager()

	sid_groups = defaultdict(list)
	for i, sid in enumerate(corpus_manager.get_ids(origin='gen')):
		sid_groups[i % args.n].append(sid)

	def run_extract_nouns(worker_name, sids):
		for sid in sids:
			nouns_fpath = nouns_manager.get_fpath(sid)

			# Only extracts the nouns if the force option is specified or the
			# saved .json file doesn't exist and the corresponding character
			# aliases .json file exists.
			if args.force or (not os.path.exists(nouns_fpath) and \
				aliases_saved(sid)):
				logging.info(worker_name + ": Extracting nouns for " + sid +
					" and saving to " + nouns_fpath + "...")

				nouns_manager.gen(sid)
			else:
				logging.info(worker_name + ": Skipping " + sid + "...")

	for i, g in sid_groups.iteritems():
		p = Process(target=run_extract_nouns, args=("T%d" % (i + 1), g,))
		p.start()
		 

if __name__ == '__main__':
	main()
