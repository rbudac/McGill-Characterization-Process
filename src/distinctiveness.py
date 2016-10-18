"""
Calculates Distinctiveness of stories.

@author: Hardik
"""

import os
import math
import random
import sys

from collections import Counter, defaultdict
from scipy import stats

from collocates import CollocatesManager
from corpus import CorpusManager


# Global collocates manager.
collocates_manager = CollocatesManager()


class Probability(object):
	"""
	Provides a number of probability distrubtion-related functions.
	"""

	def __init__(self):
		pass

	@staticmethod
	def gen_dist(collocates, smooth=False):
		"""
		Calculates the probability distrubtion for the given collocates.

		@param collocates - List of collocates (as returned by
			CollocatesManager.get)
		@param smooth - Whether or not to (Add-1) smooth the distrubtion (
			Default is False)
		@return Probability distrubtion of collocates, as a dictionary
			(Collocates that are character aliases are squashed into a single
			word type)
		"""

		cnts = Counter(coll['token']['lemma'] for coll in collocates)

		num_collocates = float(len(collocates))

		dist = defaultdict(float)
		if smooth:
			v_size = len(cnts)
			for lemma, cnt in cnts.iteritems():
				if lemma.startswith('CHAR-'):
					dist['CHAR'] += cnt
				else:
					dist[lemma] = (cnt + 1) / (num_collocates + v_size)

			dist['CHAR'] = (dist['CHAR'] + 1) / (num_collocates + v_size)
		else:
			for lemma, cnt in cnts.iteritems():
				if lemma.startswith('CHAR-'):
					dist['CHAR'] += cnt / num_collocates
				else:
					dist[lemma] = cnt / num_collocates

		return dict(dist)

	@staticmethod
	def kurtosis(dist):
		"""
		Calculates the kurtosis of the given distrubtion.

		@param dist - Probability distrubtion (as returned by
			Probability.gen_dist)
		@param Kurtosis
		"""

		return stats.kurtosis(dist.values())

	@staticmethod
	def skew(dist):
		"""
		Calculates the skew of the given distrubtion.

		@param dist - Probability distrubtion (as returned by
			Probability.gen_dist)
		@param Skew
		"""

		return stats.skew(dist.values())

	@staticmethod
	def kl_divergence(d1, d2):
		"""
		Calculates the KL-divergence (base 2) between two distributions.

		@param d1 - First probability distrubtion (as returned by
			Probability.gen_dist)
		@param d2 - Second probability distrubtion (same format as d1)
		@return KL-divergence
		"""

		kl = 0.0
		for w in set(d1.keys() + d2.keys()):
			if (w in d1 and d1[w] > 0) and (w in d2 and d2[w] > 0):
				kl += d1[w] * math.log(d1[w] / d2[w], 2)
			elif w in d1 and d1[w] > 0 and 'UNK' in d2 and d2['UNK'] > 0:
				kl += d1[w] * math.log(d1[w] / d2['UNK'], 2)
			elif w in d2 and d2[w] > 0 and 'UNK' in d1:
				kl += d1['UNK'] * math.log(d1['UNK'] / d2[w], 2)
			elif 'UNK' in d2 and d2['UNK'] > 0 and 'UNK' in d1:
				kl += d1['UNK'] * math.log(d1['UNK'] / d2['UNK'], 2)

		return kl

	@staticmethod
	def total_variation(d1, d2):
		"""
		Calculates the total variation distance between two distributions.

		@param d1 - First probability distrubtion (as returned by
			Probability.gen_dist)
		@param d2 - Second probability distrubtion (same format as d1)
		@return total variation distance
		"""

		tv = 0.0
		for w in set(d1.keys() + d2.keys()):
			if w in d1 and w not in d2:
				tv += d1[w]
			elif w not in d1 and w in d2:
				tv += d2[w]
			else:
				tv += abs(d1[w] - d2[w])

		return 0.5 * tv


class DistinctivenessCalculator(object):
	"""
	Interface for a distinctiveness calculator.
	"""

	def __init__(self, role, ranks):
		"""
		@param role - Role to consider (None means all)
		@param ranks - Iterable of ranks to consider
		"""

		self.role, self.ranks = role, ranks

	def calc(self, sid):
		"""
		Calculates the distinctiveness for the given story.

		@param sid - Story id of story
		@return Distinctiveness value
		"""

		raise NotImplementedError


class KurtosisDistinctivenessCalculator(DistinctivenessCalculator):
	"""
	Calculates distinctiveness of a story as the kurtosis of the probability
	distrubtion.
	"""

	def calc(self, sid):
		"""
		Calculates the distinctiveness for the given story as the kurtosis of
		its probability distrubtion.

		@param sid - Story id of story
		@return Kurtosis
		"""

		collocates = collocates_manager.get(sid, tpe='character',
			role=self.role, ranks=self.ranks)

		dist = Probability.gen_dist(collocates, smooth=False)
		return Probability.kurtosis(dist)


class SkewDistinctivenessCalculator(DistinctivenessCalculator):
	"""
	Calculates distinctiveness of a story as the skew of the probability
	distrubtion.
	"""

	def calc(self, sid=None, collocates=None):
		"""
		Calculates the distinctiveness for the given story or list of collocates
		as the skew of its probability distrubtion.

		@param sid - Story id of story (Default is None)
		@param collocates - Collocates (Default is None)
		@return Skew
		"""

		if collocates is None:
			collocates = collocates_manager.get(sid, tpe='character',
				role=self.role, ranks=self.ranks)

		dist = Probability.gen_dist(collocates, smooth=False)
		return Probability.skew(dist)


class KLDistinctivenessCalculator(DistinctivenessCalculator):
	"""
	Calculates distinctiveness of a story as the KL-divergence against the noun
	distribution.
	"""

	def calc(self, sid):
		"""
		Calculates the distinctiveness for the given story as the KL-divergence
		against the noun distrubtion.

		@param sid - Story id of story
		@return KL-divergence
		"""

		char_collocates = collocates_manager.get(sid, tpe='character',
			role=self.role, ranks=self.ranks)
		noun_collocates = collocates_manager.get(sid, tpe='noun')

		# TODO: Figure out which order ir better here.
		d1 = Probability.gen_dist(noun_collocates, smooth=False)
		d2 = Probability.gen_dist(char_collocates, smooth=False)

		return Probability.kl_divergence(d1, d2)


class TVDistinctivenessCalculator(DistinctivenessCalculator):
	"""
	Calculates distinctiveness of a story as the total variation against the
	noun distribution.
	"""

	def calc(self, sid):
		"""
		Calculates the distinctiveness for the given story as the total
		variation against the noun distrubtion.

		@param sid - Story id of story
		@return Total variation
		"""

		char_collocates = collocates_manager.get(sid, tpe='character',
			role=self.role, ranks=self.ranks)
		noun_collocates = collocates_manager.get(sid, tpe='noun')

		d1 = Probability.gen_dist(char_collocates, smooth=False)
		d2 = Probability.gen_dist(noun_collocates, smooth=False)

		return Probability.total_variation(d1, d2)
