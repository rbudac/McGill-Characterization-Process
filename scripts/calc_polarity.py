"""
Calculates the polarity of stories (as the difference in sentiment scores of
most positive and most negative characters), outputting the
results to .tsv files.

@author: Hardik
"""

import argparse
import csv
import logging
import os
import sys
sys.path.insert(1, os.path.join(sys.path[0], os.path.join('..', 'src')))

from collections import defaultdict
from nltk.corpus import sentiwordnet as swn

from collocates import CollocatesManager
from corpus import CorpusManager
from ranks import RANK_GROUPS


# Configure logging
logging.basicConfig(format="%(levelname)s: [%(asctime)s] %(message)s",
	level=logging.INFO)


# Calculates the polarity between the lists of collocates as the difference
# between sentiment scores of the most positive collocate in the first list to
# the most negative collocate in the second.
def calc_polarity(collocates1, collocates2):
	# Returns the total sentiment scores for each character (as rank).
	def get_sentiment_dict(collocates):
		sentiments = defaultdict(float)
		for coll in collocates:
			try:
				sentisyns = swn.senti_synsets(coll['token']['lemma'])

				if len(sentisyns) == 0:
					continue

				sentiments[coll['alias']['entity']['rank']] = \
					(sentisyns[0].pos_score() - sentisyns[0].neg_score())
			except UnicodeDecodeError:
				pass

		return sentiments

	sentiments1 = get_sentiment_dict(collocates1)
	sentiments2 = get_sentiment_dict(collocates2)

	polarity = 0.0
	for rank1, sentiment1 in sentiments1.iteritems():
		for rank2, sentiment2 in sentiments2.iteritems():
			diff = abs(sentiment1 - sentiment2)

			if polarity < diff:
				polarity = diff

	return polarity


def main():
	parser_description = ("Calculates the polarity of stories (as the "
		"difference in sentiment scores of most positive and most negative "
		"characters), outputting the results to .tsv files.")
	parser = argparse.ArgumentParser(description=parser_description)

	parser.add_argument('out_dirpath', help="Path to output directory for "
		"generated .tsv files")

	args = parser.parse_args()

	collocates_manager = CollocatesManager()
	corpus_manager = CorpusManager()
	
	# Get publication dates for all stories.
	dates = corpus_manager.get_dates()
	# Story Id's.
	sids = corpus_manager.get_ids(origin='gen')

	# Create the output directory if it doesn't already exist.
	if not os.path.exists(args.out_dirpath):
		os.makedirs(args.out_dirpath)

	for rg in RANK_GROUPS:
		rg_name, ranks = rg

		# Only consider the following rank groupings.
		if rg_name != 'Top' and rg_name != 'Top-2' and rg_name != 'Top-5':
			continue

		path = os.path.join(args.out_dirpath, '%s.tsv' % rg_name.lower())

		logging.info("Calculating for %s... (Outputting to %s)" %
			(rg_name, path))

		other_ranks = [r for r in range(1, 6) if r not in ranks]

		with open(path, 'wb') as f:
			writer = csv.writer(f, delimiter='\t', quotechar='"')

			# Write header.
			writer.writerow(['STORY ID', 'PUB. DATE', 'GENRE', 'POLARITY'])

			for sid in sids:
				if not collocates_manager.saved(sid, tpe='character'):
					logging.info("Skipping %s..." % sid)
					continue

				collocates1 = collocates_manager.get(sid, tpe='character',
					ranks=ranks)

				# Always compare against the remaining ranks in the top 5
				# grouping.
				collocates2 = collocates_manager.get(sid, tpe='character',
					ranks=other_ranks)

				genre = (None if sid.startswith('000') else
					corpus_manager.get_genre(sid))
				row = [sid, dates[sid] if sid in dates else 'DNE',
					genre if genre else 'DNE',
					calc_polarity(collocates1, collocates2)]
					
				writer.writerow(row)
	
if __name__ == '__main__':
	main()
