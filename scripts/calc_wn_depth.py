"""
Calculates the WordNet-based depth for each story across a range of roles and
character rank groups, saving the results in a series of .tsv files.

@author: Hardik
"""

import argparse
import csv
import logging
import numpy as np
import os
import random
import sys
sys.path.insert(1, os.path.join(sys.path[0], os.path.join('..', 'src')))

from collections import defaultdict
from multiprocessing import Process

from aliases import AliasesManager
from collocates import CollocatesManager
from corpus import CorpusManager
from depth import WordNetDepthCalculator
from ranks import RANK_GROUPS
from role import ROLES


# Configure logging
logging.basicConfig(format="%(levelname)s: [%(asctime)s] %(message)s",
	level=logging.INFO)


def main():
	parser_description = ("Calculates the vector-based depth for each story "
		"across a range of roles and character rank groups, saving the "
		"results in a series of .tsv files.")
	parser = argparse.ArgumentParser(description=parser_description)

	parser.add_argument('out_dirpath', help="Path to output directory")

	parser.add_argument('n', help="# worker threads to spawn", type=int)
	
	args = parser.parse_args()

	# Add None for considering all roles.
	roles = [None] + ROLES

	aliases_manager = AliasesManager()
	collocates_manager = CollocatesManager()
	corpus_manager = CorpusManager()
	
	# Story Id's.
	sids = corpus_manager.get_ids(origin='gen')
	# Get publication dates for all stories.
	dates = corpus_manager.get_dates()

	# Group parameter settings for each worker process.
	param_groups, i = defaultdict(list), 0
	for rg in RANK_GROUPS:
		for role in roles:
			param_groups[i % args.n].append((rg, role))
			i += 1

	# Create the output directory if it doesn't already exist.
	if not os.path.exists(args.out_dirpath):
		os.makedirs(args.out_dirpath)

	def run_depth_calc(worker_name, params):
		for rg, role in params:
			rg_name, ranks = rg[0], rg[1]

			role_name = role.lower() if role else 'all'
			out_path = os.path.join(args.out_dirpath, '%s-%s.tsv' % (role_name,
				rg_name.lower()))

			logging.info(worker_name + ": Processing... (Outputting to %s)" %
				out_path)
		
			wndepth_calculator = WordNetDepthCalculator(role=role, ranks=ranks)

			with open(out_path, 'wb') as f:
				writer = csv.writer(f, delimiter='\t', quotechar='"')

				# Write header.
				writer.writerow(['STORY ID', 'PUB. DATE', 'DEPTH'])

				for sid in sids:
					if not aliases_manager.saved(sid, tpe='character') or \
						not collocates_manager.saved(sid, tpe='character'):
						logging.info(worker_name + ": Skipping %s..." % sid)
						continue
					
					writer.writerow([sid, dates[sid],
						wndepth_calculator.calc(sid)])
			
			logging.info(worker_name + ": Finished!")	
	
	for i, params in param_groups.iteritems():
		p = Process(target=run_depth_calc, args=("T%d" % (i + 1), params,))
		p.start()

if __name__ == '__main__':
	main()
