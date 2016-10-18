"""
Calculates the homogeneity of stories as the pairwise cosine similarity of the
vectors corresponding to the top 5 characters, saving the results to a .tsv
file.

@author: Hardik
"""

import argparse
import csv
import itertools as it
import logging
import numpy as np
import os
import sys
sys.path.insert(1, os.path.join(sys.path[0], os.path.join('..', 'src')))

from nltk.corpus import stopwords
from scipy.spatial.distance import cosine
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.preprocessing import normalize

from aliases import AliasesManager
from collocates import CollocatesManager
from corpus import CorpusManager
from ranks import RANK_GROUPS


# Configure logging
logging.basicConfig(format="%(levelname)s: [%(asctime)s] %(message)s",
	level=logging.INFO)


STOPWORDS = stopwords.words('english')


def main():
	parser_description = ("Calculates the homogeneity of stories as the "
		"pairwise cosine similarity of the vectors corresponding to the top 5 "
		"characters, saving the results to a .tsv file.")
	parser = argparse.ArgumentParser(description=parser_description)

	parser.add_argument('out_path', help="Path to output .tsv file")
	
	args = parser.parse_args()

	aliases_manager = AliasesManager()
	collocates_manager = CollocatesManager()
	corpus_manager = CorpusManager()
	
	# Story Id's
	sids = corpus_manager.get_ids(origin='gen')
	
	with open(args.out_path, 'wb') as f:
		writer = csv.writer(f, delimiter='\t', quotechar='"')

		# Write header.
		writer.writerow(['STORY ID', 'HOMOGENEITY'])

		for sid in sids:
			if not aliases_manager.saved(sid, tpe='character') or \
				not collocates_manager.saved(sid, tpe='character'):
				logging.info("Skipping %s..." % sid)
				continue

			logging.info("For %s" % sid)

			try:
				collocates = collocates_manager.get(sid, tpe='character',
					ranks=range(1, 6))

				keyfunc = lambda c: c['alias']['entity']['rank']
				collocates = sorted(collocates, key=keyfunc)
				
				grouped_collocates = {r: list(cs) for r, cs
					in it.groupby(collocates, key=keyfunc)}

				count_vect = CountVectorizer(stop_words=STOPWORDS)
				count_vect.fit([' '.join([c['token']['lemma'] for c in cs])
					for _, cs in grouped_collocates.iteritems()])

				vecs = []
				for rank, colls in grouped_collocates.iteritems():
					vec = count_vect.transform([' '.join([coll['token']['lemma']
						for coll in colls])]).astype(float)
					vecs.append(normalize(vec).todense())

				pairwise_sims = [1 - cosine(vec1, vec2) for vec1, vec2
					in it.combinations(vecs, 2)]
					
				writer.writerow([sid, np.mean(pairwise_sims)])
			except (IndexError, ValueError):
				logging.info("Skipping %s" % sid)


if __name__ == '__main__':
	main()
