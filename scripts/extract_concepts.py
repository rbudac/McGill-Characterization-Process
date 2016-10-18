import argparse
import datetime as dt
import os
import sys
sys.path.insert(1, os.path.join(sys.path[0], os.path.join('..', 'src')))

from collections import defaultdict
from multiprocessing import Process

from concepts import ConceptsManager
from corpus import CorpusManager
from unigrams import UnigramsManager


"""
Generates the concepts .json file for each story with unigram count .tsv files
in the corpus (Overwrites it if it already exists).
"""

def log(s):
    """
    Log string s.
    """

    print "[" + str(dt.datetime.now()) + "] " + s


def main():
	parser_description = ("Generates the concepts .json file for each story "
		"with unigram count .tsv files in the corpus (Overwrites it if it "
		"already exists).")
	parser = argparse.ArgumentParser(description=parser_description)

	parser.add_argument('n', help="# worker threads to spawn", type=int)

	args = parser.parse_args()

	concepts_manager = ConceptsManager()
	corpus_manager = CorpusManager()
	unigrams_manager = UnigramsManager()

	sid_groups = defaultdict(list)
	for i, sid in enumerate(corpus_manager.get_ids(origin='gen')):
		sid_groups[i % args.n].append(sid)

	def run_extract_concepts(worker_name, sids):
		for sid in sids:
			concepts_fpath = concepts_manager.get_fpath(sid)

			# Only extracts the concepts if the saved .tsv file doesn't exist
			# and the corresponding unigram counts .tsv file exists.
			if not os.path.exists(concepts_fpath) and \
				unigrams_manager.saved(sid):
				log(worker_name + ": Extracting concepts for " + sid +
					" and saving to " + concepts_fpath + "...")

				concepts_manager.gen(sid)
			else:
				log(worker_name + ": Skipping " + sid + "...")

	for i, g in sid_groups.iteritems():
		p = Process(target=run_extract_concepts, args=("T%d" % (i + 1), g,))
		p.start()
		 

if __name__ == '__main__':
	main()
