"""
Marginalizes the character, concept, and/or noun collocates for each story with
BookNLP and CoreNLP .xml files in the corpus and outputs to a .tsv file for each
story (If the .tsv file doesn't already exist).

@author: Hardik
"""

import argparse
import logging
import os
import sys
sys.path.insert(1, os.path.join(sys.path[0], os.path.join('..', 'src')))

from collections import defaultdict
from multiprocessing import Process

from collocates import CollocatesManager, MarginalizedCollocatesManager
from corpus import CorpusManager


# Configure logging
logging.basicConfig(format="%(levelname)s: [%(asctime)s] %(message)s",
	level=logging.INFO)


def main():
	parser_description = ("Marginalizes the character, concept, and/or noun "
		"collocates for each story with BookNLP and CoreNLP .xml files in the "
		"corpus and outputs to a .tsv file for each story (If the .tsv file "
		"doesn't already exist).")
	parser = argparse.ArgumentParser(description=parser_description)

	parser.add_argument('n', help="# worker threads to spawn", type=int)
	parser.add_argument('-t', '--tpe', help="Type to marginalize "
		"('character', 'concept', or 'noun'). If not specified, then all "
		"collocates are marginalized.")
	parser.add_argument('-r', help="To output characters as ranks.",
		dest='as_rank', action='store_true')

	args = parser.parse_args()

	if args.tpe is not None and args.tpe != 'character' and \
		args.tpe != 'concept' and args.tpe != 'noun':
		raise ValueError("'tpe' must be 'character', 'concept', or "
			"'noun'.")

	mcollocates_manager = MarginalizedCollocatesManager()
	collocates_manager = CollocatesManager()
	corpus_manager = CorpusManager()

	sid_groups = defaultdict(list)
	for i, sid in enumerate(corpus_manager.get_ids(origin='gen')):
		sid_groups[i % args.n].append(sid)

	def run_marginalize_collocates(worker_name, sids):
		if args.tpe is None:
			params = ((sid, tpe, character, t, args.as_rank) for sid in sids
				for tpe in ('character', 'concept', 'noun')
				for character in (False, True) for t in range(1, 6)
				if not (character and args.as_rank))
		else:
			params = ((sid, args.tpe, character, t, args.as_rank)
				for sid in sids for character in (False, True)
				for t in range(1, 6) if not (character and args.as_rank))

		for sid, tpe, character, t, as_rank in params:

			mcollocates_path = mcollocates_manager.get_fpath(sid, tpe,
				character, t, as_rank)

			# Only marginalizes the collocates if the saved .tsv file doesn't
			# exist and the corresponding collocates .tsv exists.
			if not os.path.exists(mcollocates_path) and \
				collocates_manager.saved(sid, tpe):
				logging.info(worker_name + ": Marginalizing " + tpe +
					" collocates for " + sid +
					(" (including character)" if character else "") +
					", with threshold " + str(t) + ", and saving to " +
					mcollocates_path + "...")

				mcollocates_manager.marginalize(sid, tpe, character, t, as_rank)
			else:
				logging.info(worker_name + ": Skipping marginalization of " +
					tpe + " collocates for " + sid +
					(" (including character)" if character else "") +
					", with threshold " + str(t) + ", ...")

	for i, g in sid_groups.iteritems():
		p = Process(target=run_marginalize_collocates,
			args=("T%d" % (i + 1), g,))
		p.start()
		 

if __name__ == '__main__':
	main()
