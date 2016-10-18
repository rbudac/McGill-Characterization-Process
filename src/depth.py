"""
Calculates Depth of stories.

@author: Hardik
"""

import os
import numpy as np
import sys

from gensim.models import Word2Vec
from itertools import combinations
from nltk.corpus import wordnet as wn

from collocates import CollocatesManager
from corpus import DATA_DIRPATH, CorpusManager
from role import map_role


# Global collocates manager.
collocates_manager = CollocatesManager()


class DepthCalculator(object):
	"""
	Interface for a depth calculator.
	"""

	def __init__(self, role, ranks):
		"""
		@param role - Role to consider (None means all)
		@param ranks - Iterable of ranks to consider
		"""

		self.role, self.ranks = role, ranks

	def calc(self, sid):
		"""
		Calculates the depth for the given story.

		@param sid - Story id of story
		@return Depth value
		"""

		raise NotImplementedError


class VectorDepthCalculator(DepthCalculator):
	"""
	Calculates depth of a story using collocate vectors.
	"""

	# Shared Word2Vec model.
	MODEL = Word2Vec.load_word2vec_format(os.path.join(DATA_DIRPATH,
		'GoogleNews-vectors-negative300.bin.gz'), binary=True)

	def calc(self, sid):
		"""
		Calculates the depth for the given story by computing the average and
		standard deviation of pairwise vector distance (cosine) between
		collocates.

		@param sid - Story id of story
		@return Average and stndard deviation of pairwise vector distance of
			collocates, as a paire (returns (-1.0, -1.0) if there are not enough
			collocates)
		"""

		collocates = collocates_manager.get(sid, tpe='character',
			role=self.role, ranks=self.ranks)

		words = (coll['token']['lemma'] for coll in collocates)
		dists = []
		for w1, w2 in combinations(words, 2):
			# Ignore collocates with no corresponding vector (including
			# collocates that are character aliases for now).
			try:
				dists.append(1 - self.MODEL.similarity(w1, w2))
			except KeyError:
				continue

		if len(dists) == 0:
			return (-1.0, -1.0)
			
		return (np.mean(dists), np.std(dists))


class WordNetDepthCalculator(DepthCalculator):
	"""
	Calculates depth of a story using WordNet path distance of collocates.
	"""

	def calc(self, sid):
		"""
		Calculates the depth for the given story by computing the average
		pairwise path distance between collocates.

		@param sid - Story id of story
		@return Average pairwise path distance of collocates (returns -1.0 if 
			there are not enough collocates)
		"""

		collocates = collocates_manager.get(sid, tpe='character',
			role=self.role, ranks=self.ranks)
		num_collocates = len(collocates)

		if num_collocates == 0 or num_collocates == 1:
			return -1.0

		# List of collocate synsets, one per collocate.
		coll_syns = []
		for coll in collocates:
			# TODO: Handle error better.
			try:
				# TODO: Add POS tag.
				syns = wn.synsets(coll['token']['lemma'])
				if len(syns) > 0:
					# Take MFS.
					coll_syns.append(syns[0])
			except UnicodeDecodeError:
				pass

		dist_sum, n = 0.0, 0
		for syn1, syn2 in combinations(coll_syns, 2):
			ps = syn1.path_similarity(syn2)
			dist_sum += (1 - ps) if ps else 1.0
			n += 1

		if n == 0:
			return -1.0

		return dist_sum / n
