import argparse
import datetime as dt
import os
import sys
sys.path.insert(1, os.path.join(sys.path[0], os.path.join('..', 'src')))

from collections import defaultdict
from multiprocessing import Process

from aliases import AliasesManager
from corpus import CorpusManager
from unigrams import UnigramsManager


"""
Counts the unigrams for each story in the corpus with an identified character
aliases .json file and outputs to a .tsv file (If it doesn't already exist).
"""


def log(s):
    """
    Log string s.
    """

    print "[" + str(dt.datetime.now()) + "] " + s


def main():
	parser_description = ("Counts the unigrams for each story in the corpus "
		"with an identified character aliases .json file and outputs to a .tsv "
		"file (If it doesn't already exist).")
	parser = argparse.ArgumentParser(description=parser_description)

	parser.add_argument('n', help="# worker threads to spawn", type=int)

	args = parser.parse_args()

	aliases_manager = AliasesManager()
	corpus_manager = CorpusManager()
	unigrams_manager = UnigramsManager()

	sid_groups = defaultdict(list)
	for i, sid in enumerate(corpus_manager.get_ids(origin='gen')):
		sid_groups[i % args.n].append(sid)

	def run_count_unigrams(worker_name, sids):
		for sid in sids:
			unigrams_fpath = unigrams_manager.get_fpath(sid)

			# Only counts the ungirams if the saved .tsv file doesn't exist and
			# the corresponding character aliases .json exists.
			if not os.path.exists(unigrams_fpath) and \
				aliases_manager.saved(sid, 'character'):
				log(worker_name + ": Counting unigrams for " + sid +
					" and saving to " + unigrams_fpath + "...")

				unigrams_manager.gen(sid)
			else:
				log(worker_name + ": Skipping " + sid + "...")

	for i, g in sid_groups.iteritems():
		p = Process(target=run_count_unigrams, args=("T%d" % (i + 1), g,))
		p.start()
		 

if __name__ == '__main__':
	main()
