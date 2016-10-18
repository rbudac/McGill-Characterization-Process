"""
Parses the character, concept, or noun collocates for each story with
BookNLP and CoreNLP .xml files in the corpus and outputs to a .tsv file.

@author: Hardik
"""

import argparse
import logging
import os
import sys
sys.path.insert(1, os.path.join(sys.path[0], os.path.join('..', 'src')))

from collections import defaultdict
from multiprocessing import Process

from aliases import AliasesManager
from collocates import CollocatesManager
from corpus import CorpusManager


# Configure logging
logging.basicConfig(format="%(levelname)s: [%(asctime)s] %(message)s",
	level=logging.INFO)


def main():
	parser_description = ("Parses the character, concept, or noun "
		"collocates for each story with BookNLP and CoreNLP .xml files in the "
		"corpus and outputs to a .tsv file (If it doesn't already exist).")
	parser = argparse.ArgumentParser(description=parser_description)

	parser.add_argument('tpe', help="Identify 'character', 'concept', or "
		"'noun' aliases")
	parser.add_argument('n', help="# worker threads to spawn", type=int)

	parser.add_argument('-f', '--force', dest='force', action='store_true',
		help="Force re-identification")

	args = parser.parse_args()

	aliases_manager = AliasesManager()
	collocates_manager = CollocatesManager()
	corpus_manager = CorpusManager()

	sid_groups = defaultdict(list)
	for i, sid in enumerate(corpus_manager.get_ids(origin='gen')):
		sid_groups[i % args.n].append(sid)

	def run_parse_collocates(worker_name, sids):
		for sid in sids:
			collocates_path = collocates_manager.get_fpath(sid, args.tpe)

			# Only parse the collocates if the force option is specified or
			# saved .tsv file doesn't exist and the corresponding identified
			# aliases .json exists.
			if aliases_manager.saved(sid, args.tpe) and (args.force or
				not os.path.exists(collocates_path)):
				logging.info(worker_name + ": Finding " + args.tpe +
					" collocates for " + sid + " and saving to " +
					collocates_path + "...")

				collocates_manager.parse(sid, args.tpe)
			else:
				logging.info(worker_name + ": Skipping " + sid + "...")

	for i, g in sid_groups.iteritems():
		p = Process(target=run_parse_collocates, args=("T%d" % (i + 1), g,))
		p.start()
		 

if __name__ == '__main__':
	main()
