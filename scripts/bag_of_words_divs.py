"""
Calculates the KL-divergence between bag-of-word distribtuions (total,
character, and non-character) for each story, outputting the results to a series
of .tsv files.

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
from multiprocessing import Process
from nltk.corpus import stopwords

from aliases import AliasesManager
from collocates import CollocatesManager
from corpus import CorpusManager, BothTextsMinusShakesCorpusManager
from distinctiveness import Probability


# Configure logging
logging.basicConfig(format="%(levelname)s: [%(asctime)s] %(message)s",
	level=logging.INFO)


STOPWORDS = set(stopwords.words('english'))


# TODO: Temporary.
def write_dist(dist, path):
	with open(path, 'wb') as out:
		writer = csv.writer(out, delimiter='\t', quotechar='"')

		writer.writerow(['WORD', 'PROB.'])

		for word, prob in sorted(dist.items(), key=lambda i: -i[1]):
			writer.writerow([word, prob])


def main():
	parser_description = ("Calculates the KL-divergence between bag-of-word "
		"distribtuions (total, character, and non-character) for each story, "
		"outputting the results to a series of .tsv files.")
	parser = argparse.ArgumentParser(description=parser_description)

	parser.add_argument('out_dirpath', help="Path to output directory")

	parser.add_argument('n',
		help="# worker threads to spawn (Must be at least 2)", type=int)
	
	args = parser.parse_args()

	aliases_manager = AliasesManager()
	collocates_manager = CollocatesManager()
	corpus_manager = CorpusManager()
	
	# Get publication dates for all stories.
	dates = corpus_manager.get_dates()
	# Story Id's.
	# sids = corpus_manager.get_ids(origin='gen')
	sids = BothTextsMinusShakesCorpusManager().get_ids(origin='gen')

	# Story Id's by contemporary genre.
	genre_sids = defaultdict(list)
	# for sid in sids:
	# 	if not aliases_manager.saved(sid, tpe='character') or \
	# 		not collocates_manager.saved(sid, tpe='character'):
	# 		continue

	# 	sub = corpus_manager.get_sub(sid)

	# 	if sub == 'contemporary':
	# 		genre = corpus_manager.get_genre(sid)
	# 		if genre != 'ny-times':
	# 			genre_sids[genre].append(sid)

	# Story Id's by period (minus the recent shiz).
	period_sids = defaultdict(list)
	for sid in sids:
		if not aliases_manager.saved(sid, tpe='character') or \
			not collocates_manager.saved(sid, tpe='character'):
			continue


		# I can't even -Rob
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

	cats, i = defaultdict(list), 0
	for cat in genre_sids.keys() + period_sids.keys():
		cats[i % (args.n - 1)].append(cat)
		i += 1

	# Create the output directory if it doesn't already exist.
	if not os.path.exists(args.out_dirpath):
		os.makedirs(args.out_dirpath)

	# Returns a word (lemma) counter for the given story's text.
	def get_lemma_cntr(sid):
		path = corpus_manager.get_corenlp_fpath(sid)
		e = ET.parse(path).getroot()

		return Counter(tok[1].text for tok in e.iter('token'))
	
	# Returns a word (lemma) counter for the given story's character collocate
	# words.
	def get_char_cntr(sid):
		collocates = collocates_manager.get(sid, tpe='character',
			# TODO: Temporary
			ranks=range(1, 21))
			# ranks=range(1, 2))
			# ranks=range(1, 3))
			# ranks=range(1, 6))

		return Counter(coll['token']['lemma'] for coll in collocates)

	# Returns a word (lemma) counter for the given story's non-character
	# collocate words.
	def get_non_cntr(sid):
		# path = "/home/ndg/project/shared_datasets/narrative/characterization/data/texts/non-lemma/%s.txt" % sid
		# path = "/home/ndg/project/shared_datasets/narrative/characterization/data/texts/non-lemma-top/%s.txt" % sid
		path = "/home/ndg/project/shared_datasets/narrative/characterization/data/texts/both_texts_minus_shakes/non-lemma/%s.txt" % sid

		with open(path) as f:
			return Counter(f.read().split())

		# path = corpus_manager.get_corenlp_fpath(sid)
		# e = ET.parse(path).getroot()

		# char_collocates = collocates_manager.get(sid, tpe='character',
		# 	# TODO: Temporary
		# 	# ranks=range(1, 21))
		# 	ranks=range(1, 2))

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

	# Generates the bag-of-words distribution for the given word counter,
	# returning a dictionary from word to probability.
	# def gen_dist(cntr):
	# 	num_tokens = float(sum(cntr.values()))
	# 	return {word: cnt / num_tokens for word, cnt in cntr.iteritems()}

	# TODO: Temporary.
	# Generates the bag-of-words distribution for the given list of word-count
	# pairs, returning a dictionary from word to probability.
	def gen_dist(wc_pairs):
		num_tokens = float(sum([c for _, c in wc_pairs]))
		return {w: c / num_tokens for w, c in wc_pairs}

	def run_calc_divergences(worker_name, cats):
		for cat in cats:
			sids = genre_sids[cat] if cat in genre_sids else period_sids[cat]

			out_path = os.path.join(args.out_dirpath, '%s.tsv' % cat)

			logging.info(worker_name +
				": Processing for %s... (Outputting to %s)" % (cat, out_path))

			with open(out_path, 'wb') as f:
				writer = csv.writer(f, delimiter='\t', quotechar='"') 

				# Header.
				# writer.writerow(['STORY ID', 'BOW vs. NON-CHAR. DIV.',
				# 	'BOW vs. CHAR. DIV.', 'NON-CHAR. VS. CHAR. DIV.'])

				writer.writerow(['STORY ID', 'NON-CHAR. VS. CHAR. DIV. (500)',
					'NON-CHAR. VS. CHAR. DIV. (500 w/o stop)'])

				for sid in sids:
					# dist = gen_dist(get_lemma_cntr(sid))

					# char_cntr = get_char_cntr(sid)
					# char_dist = gen_dist(char_cntr)

					# non_cntr = get_non_cntr(sid)
					# non_dist = gen_dist(non_cntr)

					# non_words = list(non_cntr.elements())
					# num_char_words = sum(char_cntr.values())

					# if num_char_words < len(non_words):
					# 	non_sampled_cntr = Counter(random.sample(non_words,
					# 		num_char_words))
					# 	non_sampled_dist = gen_dist(non_sampled_cntr)

					# 	row = [
					# 		sid,
					# 		Probability.kl_divergence(non_dist, dist),
					# 		Probability.kl_divergence(char_dist, dist),
					# 		Probability.kl_divergence(char_dist,
					# 			non_sampled_dist)
					# 	]
					# else:
					# 	row = [
					# 		sid,
					# 		Probability.kl_divergence(non_dist, dist),
					# 		Probability.kl_divergence(char_dist, dist),
					# 		Probability.kl_divergence(char_dist,
					# 			non_dist)
					# 	]

					row = [sid]

					char_cntr = get_char_cntr(sid)
					non_cntr = get_non_cntr(sid)

					char_dist = gen_dist(char_cntr.most_common(500))
					non_dist = gen_dist(non_cntr.most_common(500))

					# write_dist(char_dist, "/home/ndg/project/shared_datasets/narrative/characterization/data/probs/char/all/" + sid + ".tsv")
					# write_dist(non_dist, "/home/ndg/project/shared_datasets/narrative/characterization/data/probs/non/all/" + sid + ".tsv")

					row.append(Probability.kl_divergence(char_dist, non_dist))			

					char_dist = gen_dist([(w, c) for w, c
						in char_cntr.most_common(500) if w not in STOPWORDS])
			
					non_dist = gen_dist([(w, c) for w, c
						in non_cntr.most_common(500) if w not in STOPWORDS])

					# write_dist(char_dist, "/home/ndg/project/shared_datasets/narrative/characterization/data/probs/char-nostop/all/" + sid + ".tsv")
					# write_dist(non_dist, "/home/ndg/project/shared_datasets/narrative/characterization/data/probs/non-nostop/all/" + sid + ".tsv")

					row.append(Probability.kl_divergence(char_dist, non_dist))

					writer.writerow(row)

			logging.info(worker_name + ": Finished!")

	def run_calc_aggregated(worker_name):
		out_path = os.path.join(args.out_dirpath, 'aggregated.tsv')

		logging.info(worker_name +
			": Processing aggregated... (Outputting to %s)" % out_path)

		# Table with values aggregated by category (both genre and period).
		with open(out_path, 'wb') as f:
			writer = csv.writer(f, delimiter='\t', quotechar='"') 

			# Header.
			writer.writerow(['CATEGORY', 'BOW vs. NON-CHAR. DIV.',
				'NON-CHAR. VS. CHAR. DIV.'])

			for cat, sids in genre_sids.items() + period_sids.items():
				cntr, char_cntr, non_cntr = Counter(), Counter(), Counter() 
				non_sampled_cntr = Counter()
				for sid in sids:
					cntr += get_lemma_cntr(sid)

					sub_char_cntr = get_char_cntr(sid)
					char_cntr += sub_char_cntr

					sub_non_cntr = get_non_cntr(sid)
					non_cntr += sub_non_cntr

					non_words = list(sub_non_cntr.elements())
					num_char_words = sum(sub_char_cntr.values())

					if num_char_words < len(non_words):
						non_sampled_cntr += Counter(random.sample(non_words,
							num_char_words))
					else:
						non_sampled_cntr += sub_non_cntr

				dist = gen_dist(cntr)
				char_dist = gen_dist(char_cntr)
				non_dist = gen_dist(non_cntr)
				non_sampled_dist = gen_dist(non_sampled_cntr)

				writer.writerow([
					cat,
					Probability.kl_divergence(non_dist, dist),
					Probability.kl_divergence(non_dist, dist),
					Probability.kl_divergence(char_dist, non_sampled_dist)
				])

		logging.info(worker_name + ": Finished!")

	for i, sub_cats in cats.iteritems():
		p = Process(target=run_calc_divergences, args=("T%d" % (i + 1),
			sub_cats,))
		p.start()

	# TODO: Temporary.
	# p = Process(target=run_calc_aggregated, args=("T%d" % (len(cats) + 1),))
	# p.start()


if __name__ == '__main__':
	main()
