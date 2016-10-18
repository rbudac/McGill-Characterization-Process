"""
Identifies the (character, concept, or noun) aliases for each story with BookNLP
and CoreNLP .xml files in the corpus and outputs to a .json file.

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
from characters import CharactersManager
from concepts import ConceptsManager
from corpus import CorpusManager
from nouns import NounsManager


# Configure logging
logging.basicConfig(format="%(levelname)s: [%(asctime)s] %(message)s",
	level=logging.INFO)


def main():
	parser_description = ("Identifies the (character, concept, noun) aliases "
		"for each story with BookNLP and CoreNLP .xml files in the corpus and "
		"outputs to a .json file (If it doesn't already exist).")
	parser = argparse.ArgumentParser(description=parser_description)

	parser.add_argument('tpe', help="Identify 'character', 'concept', or "
		"'noun' aliases")
	parser.add_argument('n', help="# worker threads to spawn", type=int)

	parser.add_argument('-f', '--force', dest='force', action='store_true',
		help="Force re-identification")

	args = parser.parse_args()

	if args.tpe == 'character':
		entities_manager = CharactersManager()
	elif args.tpe == 'concept':
		entities_manager = ConceptsManager()
	elif args.tpe == 'noun':
		entities_manager = NounsManager()
	else:
		raise ValueError("tpe must be 'character', 'concept', or 'noun'.")

	aliases_manager = AliasesManager()
	
	corpus_manager = CorpusManager()

	sid_groups = defaultdict(list)
	for i, sid in enumerate(corpus_manager.get_ids(origin='gen')):
		sid_groups[i % args.n].append(sid)

	def run_ident_aliases(worker_name, sids):
		for sid in sids:
			aliases_fpath = aliases_manager.get_fpath(sid, args.tpe)

			# Only identify the aliases if the force option is specified or the
			# saved .json file doesn't exist and the corresponding entities
			# .json exists.
			if entities_manager.saved(sid) and (args.force or
				not os.path.exists(aliases_fpath)):
				logging.info("(" + worker_name + ") Identifying " + args.tpe +
					" aliases for " + sid + " and saving to " + aliases_fpath +
					"...")

				aliases_manager.ident(sid, args.tpe)
			else:
				logging.info("(" + worker_name + ") Skipping " + sid + "...")

	for i, g in sid_groups.iteritems():
		p = Process(target=run_ident_aliases, args=("T%d" % (i + 1), g,))
		p.start()
		 

if __name__ == '__main__':
	main()
