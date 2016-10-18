"""
Performs pairwise comparisons of story character and non-character collocate
distributions (using KL-divergence) between stories for various categories
(genre and period). All results are saved in .tsv tables (one per category).

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
import xml.etree.ElementTree as ET

from collections import Counter, defaultdict
from itertools import combinations
from multiprocessing import Process
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from scipy.stats import bernoulli

from aliases import AliasesManager
from collocates import CollocatesManager
from corpus import CorpusManager
from distinctiveness import Probability


# Configure logging
logging.basicConfig(format="%(levelname)s: [%(asctime)s] %(message)s",
	level=logging.INFO)


STOPWORDS = set(stopwords.words('english'))

# Filepath to "said" words.
SAID_DICT_PATH = "../resources/said_dict.txt"

# Returns a set of "said" words, lemmatized.
def load_said_words():
	words = []
	with open(SAID_DICT_PATH) as f:
		for line in f:
			words += [p.strip().replace(' ', '-') for p in line.split('\t')]

	lemmatizer = WordNetLemmatizer()

	# Lemmatize and convert to set and add 'say'.
	return set([lemmatizer.lemmatize(w) for w in words] + ['say'])


def main():
	parser_description = ("Performs pairwise comparisons of story character "
		"and non-character collocate distributions (using KL-divergence) "
		"between stories for various categories (genre and period). All "
		"results are saved in .tsv tables (one per category).")
	parser = argparse.ArgumentParser(description=parser_description)

	parser.add_argument('out_dirpath', help="Path to output directory")

	parser.add_argument('sample', help="# pairwise comparisons to sample",
		type=int)

	parser.add_argument('n', help="# worker threads to spawn", type=int)
	
	args = parser.parse_args()

	aliases_manager = AliasesManager()
	collocates_manager = CollocatesManager()
	corpus_manager = CorpusManager()
	
	# Story Id's.
	sids = corpus_manager.get_ids(origin='gen')

	# Story Id's by contemporary genre.
	genre_sids = defaultdict(list)
	for sid in sids:
		if not aliases_manager.saved(sid, tpe='character') or \
			not collocates_manager.saved(sid, tpe='character'):
			continue

		sub = corpus_manager.get_sub(sid)

		if sub == 'contemporary':
			genre = corpus_manager.get_genre(sid)
			if genre != 'ny-times':
				genre_sids[genre].append(sid)

	# Story Id's by period grouping.
	period_sids = defaultdict(list)
	for sid in sids:
		if not aliases_manager.saved(sid, tpe='character') or \
			not collocates_manager.saved(sid, tpe='character'):
			continue

		if sid == 'a-tale-of-two-cities':
			period_sids['vic'].append(sid)
		elif sid == 'pride-and-prejudice':
			period_sids['rom'].append(sid)
		elif sid == 'peregrine-pickle' or sid == 'tristram-shandy':
			period_sids['c18'].append(sid)
		elif sid == 'to-the-lighthouse':
			period_sids['klab'].append(sid)
		else:
			sub = corpus_manager.get_sub(sid)

			if sub == 'contemporary' or sub == 'mfa' or sub == 'ny-times':
				continue
			elif sub == 'period-novels':
				period_sids[corpus_manager.percm.get_period(sid)].append(sid)
			else:
				period_sids[sub].append(sid)

	# Grouping categories for threads.
	cats, i = defaultdict(list), 0
	for cat in genre_sids.keys() + period_sids.keys():
		cats[i % args.n].append(cat)
		i += 1

	# Create the output directory if it doesn't already exist.
	if not os.path.exists(args.out_dirpath):
		os.makedirs(args.out_dirpath)

	# Returns a word (lemma) counter for the given storys' character collocate
	# words.
	def get_char_cntr(sid, stop=False):		
		collocates = collocates_manager.get(sid, tpe='character',
			ranks=range(1, 21))
	
		return Counter(coll['token']['lemma'] for coll in collocates
			if not coll['token']['lemma'].startswith('CHAR-'))

	# Returns a word (lemma) counter for the given story's non-character
	# collocate words.
	def get_non_cntr(sid):
		path = "/home/ndg/project/shared_datasets/narrative/characterization/data/texts/non-lemma/%s.txt" % sid

		with open(path) as f:
			return Counter(f.read().split())
		# path = corpus_manager.get_corenlp_fpath(sid)
		# e = ET.parse(path).getroot()

		# char_collocates = collocates_manager.get(sid, tpe='character',
		# 	ranks=range(1, 21))

		# # Counts all lemmas.
		# cntr = Counter(tok[1].text for tok in e.iter('token'))

		# # Counts all character collocate lemmas.
		# char_coll_cntr = Counter(coll['token']['lemma']
		# 	for coll in char_collocates)
		# # Counts all alias tokens.
		# alias_cntr = Counter(tok for coll in char_collocates
		# 	for tok in coll['alias']['span'].split())

		# # Non-character word (lemma) counter.
		# return cntr - char_coll_cntr - alias_cntr

	# Generates the bag-of-words distribution for the given list of word-count
	# pairs, returning a dictionary from word to probability.
	def gen_dist(wc_pairs):
		num_tokens = float(sum([c for _, c in wc_pairs]))
		return {w: c / num_tokens for w, c in wc_pairs}

	said_words = load_said_words()

	# Worker function.
	def run_calc_divs(worker_name, cats):
		for cat in cats:
			all_sids = genre_sids[cat] if cat in genre_sids else \
				period_sids[cat]

			out_path = os.path.join(args.out_dirpath, '%s.tsv' % cat)

			logging.info(worker_name +
				": Processing for %s... (Outputting to %s)" % (cat, out_path))

			with open(out_path, 'wb') as f:
				writer = csv.writer(f, delimiter='\t', quotechar='"') 

				# Header.
				writer.writerow([
					'STORY A',
					'STORY B',
					'A CHAR. vs. B CHAR. (100)',
					'A CHAR. vs. A NON-CHAR. (100)',
					# 'B CHAR. vs. B NON-CHAR. (100)',
					# 'A NON-CHAR. vs. B NON-CHAR. (100)',
					'A CHAR. vs. B CHAR. (500)',
					'A CHAR. vs. A NON-CHAR. (500)',
					# 'B CHAR. vs. B NON-CHAR. (500)',
					# 'A NON-CHAR. vs. B NON-CHAR. (500)',
					'A CHAR. vs. B CHAR. (1000)',
					'A CHAR. vs. A NON-CHAR. (1000)',
					# 'B CHAR. vs. B NON-CHAR. (1000)',
					# 'A NON-CHAR. vs. B NON-CHAR. (1000)',
					'A CHAR. vs. B CHAR. (3000)',
					'A CHAR. vs. A NON-CHAR. (3000)',
					# 'B CHAR. vs. B NON-CHAR. (3000)',
					# 'A NON-CHAR. vs. B NON-CHAR. (3000)',
					'A CHAR. vs. B CHAR. (5000)',
					'A CHAR. vs. A NON-CHAR. (5000)',
					# 'B CHAR. vs. B NON-CHAR. (5000)',
					# 'A NON-CHAR. vs. B NON-CHAR. (5000)',
					'A CHAR. vs. B CHAR. (10000)',
					'A CHAR. vs. A NON-CHAR. (10000)',
					# 'B CHAR. vs. B NON-CHAR. (10000)',
					# 'A NON-CHAR. vs. B NON-CHAR. (10000)',
					'A CHAR. vs. B CHAR. (ALL)',
					'A CHAR. vs. A NON-CHAR. (ALL)',
					# 'B CHAR. vs. B NON-CHAR. (ALL)',
					# 'A NON-CHAR. vs. B NON-CHAR. (ALL)',
					'A CHAR. vs. B CHAR. (500 w/o stop & comm.)',
					'A CHAR. vs. A NON-CHAR. (500 w/o stop & comm.)',
					# 'B CHAR. vs. B NON-CHAR. (500 w/o stop & comm.)',
					# 'A NON-CHAR. vs. B NON-CHAR. (500 w/o stop & comm.)',
					'A CHAR. vs. B CHAR. (1000 w/o stop & comm.)',
					'A CHAR. vs. A NON-CHAR. (1000 w/o stop & comm.)',
					# 'B CHAR. vs. B NON-CHAR. (1000 w/o stop & comm.)',
					# 'A NON-CHAR. vs. B NON-CHAR. (1000 w/o stop & comm.)',
					'A CHAR. vs. B CHAR. (3000 w/o stop & comm.)',
					'A CHAR. vs. A NON-CHAR. (3000 w/o stop & comm.)',
					# 'B CHAR. vs. B NON-CHAR. (3000 w/o stop & comm.)',
					# 'A NON-CHAR. vs. B NON-CHAR. (3000 w/o stop & comm.)',
					'A CHAR. vs. B CHAR. (5000 w/o stop & comm.)',
					'A CHAR. vs. A NON-CHAR. (5000 w/o stop & comm.)',
					# 'B CHAR. vs. B NON-CHAR. (5000 w/o stop & comm.)',
					# 'A NON-CHAR. vs. B NON-CHAR. (5000 w/o stop & comm.)',
					'A CHAR. vs. B CHAR. (10000 w/o stop & comm.)',
					'A CHAR. vs. A NON-CHAR. (10000 w/o stop & comm.)',
					# 'B CHAR. vs. B NON-CHAR. (10000 w/o stop & comm.)',
					# 'A NON-CHAR. vs. B NON-CHAR. (10000 w/o stop & comm.)',
					'A CHAR. vs. B CHAR. (ALL w/o stop & comm.)',
					'A CHAR. vs. A NON-CHAR. (ALL w/o stop & comm.)',
					# 'B CHAR. vs. B NON-CHAR. (ALL w/o stop & comm.)',
					# 'A NON-CHAR. vs. B NON-CHAR. (ALL w/o stop & comm.)'
				])

				# story_pairs = []
				# for sid1 in all_sids:
				# 	sid2 = random.choice(all_sids)
				# 	while sid1 == sid2:
				# 		sid2 = random.choice(all_sids)

				# 	story_pairs.append((sid1, sid2))

				story_pairs, i = [], 1
				for sid1, sid2 in combinations(all_sids, 2):
					if len(story_pairs) < args.sample:
						story_pairs.append((sid1, sid2))
					else:
						p = float(args.sample) / i
						if bernoulli.rvs(p, size=1)[0] == 1:
							story_pairs = random.sample(story_pairs,
								args.sample - 1)
							story_pairs.append((sid1, sid2))
					
					i += 1

				for sid1, sid2 in story_pairs:
					row = [sid1, sid2]

					char_cntr1 = get_char_cntr(sid1)
					char_cntr2 = get_char_cntr(sid2)

					non_cntr1 = get_non_cntr(sid1)
					non_cntr2 = get_non_cntr(sid2)

					# For top 100, 500, 1000, 3000, 5000, 10000, and all words.
					for num_top in (100, 500, 1000, 3000, 5000, 10000,
						1000000000):
						char_dist1 = gen_dist(char_cntr1.most_common(num_top))
						char_dist2 = gen_dist(char_cntr2.most_common(num_top))
						
						non_dist1 = gen_dist(non_cntr1.most_common(num_top))
						# non_dist2 = gen_dist(non_cntr2.most_common(num_top))

						row += [
							Probability.kl_divergence(char_dist1, char_dist2),
							Probability.kl_divergence(char_dist1, non_dist1)
							# Probability.kl_divergence(char_dist2, non_dist2),
							# Probability.kl_divergence(non_dist1, non_dist2)
						]

					# For top 500, 1000, 3000, 5000, 100000, and all words
					# without stop words.
					for num_top in (500, 1000, 3000, 5000, 10000, 1000000000):
						char_dist1 = gen_dist([(w, c) for w, c
							in char_cntr1.most_common(num_top)
							if w not in STOPWORDS and w not in said_words])
						char_dist2 = gen_dist([(w, c) for w, c
							in char_cntr2.most_common(num_top)
							if w not in STOPWORDS and w not in said_words])

						non_dist1 = gen_dist([(w, c) for w, c
							in non_cntr1.most_common(num_top)
							if w not in STOPWORDS and w not in said_words])
						# non_dist2 = gen_dist([(w, c) for w, c
						# 	in non_cntr2.most_common(num_top)
						# 	if w not in STOPWORDS])

						row += [
							Probability.kl_divergence(char_dist1, char_dist2),
							Probability.kl_divergence(char_dist1, non_dist1)
							# Probability.kl_divergence(char_dist2, non_dist2),
							# Probability.kl_divergence(non_dist1, non_dist2)
						]

					writer.writerow(row)

			logging.info(worker_name + ": Finished!")

	for i, sub_cats in cats.iteritems():
		p = Process(target=run_calc_divs, args=("WORKER %d" % (i + 1),
			sub_cats,))
		p.start()


if __name__ == '__main__':
	main()
