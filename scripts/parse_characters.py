"""
Generates the characters .json file for each story with BookNLP and CoreNLP .xml
files in the corpus.

@author: Hardik
"""

import argparse
import logging
import os
import sys
sys.path.insert(1, os.path.join(sys.path[0], os.path.join('..', 'src')))

from collections import defaultdict
from multiprocessing import Process

from characters import CharactersManager
from corpus import CorpusManager


# Configure logging
logging.basicConfig(format="%(levelname)s: [%(asctime)s] %(message)s",
	level=logging.INFO)


def main():
	parser_description = ("Generates the characters .json file for each story "
		"with BookNLP and CoreNLP .xml files in the corpus.")
	parser = argparse.ArgumentParser(description=parser_description)

	parser.add_argument('n', help="# worker threads to spawn", type=int)

	parser.add_argument('-f', '--force', dest='force', action='store_true',
		help="Force re-parsing")

	args = parser.parse_args()

	corpus_manager = CorpusManager()
	characters_manager = CharactersManager()

	sid_groups = defaultdict(list)
	for i, sid in enumerate(corpus_manager.get_ids(origin='gen')):
		sid_groups[i % args.n].append(sid)

	def run_parse_characters(worker_name, sids):
		for sid in sids:
			characters_path = characters_manager.get_fpath(sid)
			# Only parses the characters if  the force option is specified or
			# the saved .json file doesn't exist.
			if args.force or (not os.path.exists(characters_path)):
				logging.info(worker_name + ": Parsing characters for " + sid +
					" and saving to " + characters_path + "...")

				characters_manager.gen(sid)
			else:
				logging.info(worker_name + ": Skipping " + sid + "...")

	for i, g in sid_groups.iteritems():
		p = Process(target=run_parse_characters, args=("T%d" % (i + 1), g,))
		p.start()


if __name__ == '__main__':
	main()
