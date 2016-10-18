"""
Calculates the class similiarity of stories with respect to genre and period
across a range of character rank groups, saving the results in a series of .tsv
files. Class similiarity of a story with respect to a category is calculated as
cosine similarity against the "mean" category vector.

@author: Hardik
"""

import argparse
import csv
import logging
import numpy as np
import os
import sys
sys.path.insert(1, os.path.join(sys.path[0], os.path.join('..', 'src')))

from collections import defaultdict
from multiprocessing import Process
from scipy.spatial.distance import cosine
from sklearn.preprocessing import normalize

from aliases import AliasesManager
from collocates import CollocatesManager
from corpus import CorpusManager
from ranks import RANK_GROUPS


# Configure logging
logging.basicConfig(format="%(levelname)s: [%(asctime)s] %(message)s",
	level=logging.INFO)


def main():
	parser_description = ("Calculates the class similiarity of stories with "
		"respect to genre and period across a range of character rank groups, "
		"saving the results in a series of .tsv files. Class similiarity of a "
		"story with respect to a category is calculated as cosine similarity "
		"against the \"mean\" category vector.")
	parser = argparse.ArgumentParser(description=parser_description)

	parser.add_argument('out_dirpath', help="Path to output directory")

	parser.add_argument('n', help="# worker threads to spawn", type=int)
	
	args = parser.parse_args()

	aliases_manager = AliasesManager()
	collocates_manager = CollocatesManager()
	corpus_manager = CorpusManager()
	
	# Get publication dates for all stories.
	dates = corpus_manager.get_dates()

	# Story Id's by category (genre or period).
	sids = defaultdict(list)
	for sid in corpus_manager.get_ids(origin='gen'):
		if not aliases_manager.saved(sid, tpe='character') or \
			not collocates_manager.saved(sid, tpe='character'):
			continue

		if sid == 'a-tale-of-two-cities':
			sids['vic'].append(sid)
		elif sid == 'pride-and-prejudice':
			sids['rom'].append(sid)
		elif sid == 'peregrine-pickle' or sid == 'tristram-shandy':
			sids['c18'].append(sid)
		elif sid == 'to-the-lighthouse':
			sids['klab'].append(sid)
		else:
			sub = corpus_manager.get_sub(sid)

			if sub == 'contemporary':
				genre = corpus_manager.get_genre(sid)
				if genre == 'ny-times':
					continue
				else:
					sids[genre].append(sid)
			# Skip.
			elif sub == 'mfa' or sub == 'ny-times':
				continue
			elif sub == 'period-novels':
				sids[corpus_manager.percm.get_period(sid)].append(sid)
			else:
				sids[sub].append(sid)

	# Group parameter settings for each worker process.
	param_groups, i = defaultdict(list), 0
	for rg in RANK_GROUPS:
		for cat in sids.keys():
			param_groups[i % args.n].append((rg, cat))
			i += 1

	# Create the output directory if it doesn't already exist.
	if not os.path.exists(args.out_dirpath):
		os.makedirs(args.out_dirpath)

	def run_class_sim_calc(worker_name, params):
		for rg, cat in params:
			rg_name, ranks = rg

			out_path = os.path.join(args.out_dirpath, rg_name.lower())

			# Create the sub-directory if it doesn't already exist.
			if not os.path.exists(out_path):
				os.makedirs(out_path)

			out_path = os.path.join(out_path, '%s.tsv' % cat)

			logging.info(worker_name +
				": Calculating for %s and %s... (Outputting to %s)" %
				(rg_name, cat, out_path))
		
			dtmat, count_vect = collocates_manager.get_dtmatrix(sids[cat],
				tpe='character', ranks=ranks, normal=True)
			
			mean_vec = dtmat.mean(axis=0)

			with open(out_path, 'wb') as f:
				writer = csv.writer(f, delimiter='\t', quotechar='"')

				# Write header.
				writer.writerow(['STORY ID', 'PUB. DATE', 'CLASS SIMILIARTY'])

				for sid in sids[cat]:
					collocates = collocates_manager.get(sid, tpe='character',
						ranks=ranks)

					vec = count_vect.transform([' '.join([coll['token']['lemma']
						for coll in collocates])]).astype(float)
					vec = normalize(vec).todense()

					writer.writerow([sid, dates[sid] if sid in dates else 'DNE',
						1 - cosine(vec, mean_vec)])
			
			logging.info(worker_name + ": Finished!")	
	
	for i, params in param_groups.iteritems():
		p = Process(target=run_class_sim_calc,
			args=("T%d" % (i + 1), params,))
		p.start()

if __name__ == '__main__':
	main()
