"""
Manages the collocates for characters, concepts, and nounds for each story in
the corpus.

@author: Hardik
"""

import csv
import os
import sys

from collections import Counter
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.preprocessing import normalize

from aliases import AliasesManager
from characters import CharactersManager
from dependency import DependencyParser
from corpus import CorpusManager
from role import map_role


class CollocatesManager(object):
	"""
	Manages the collocates for characters, concepts, and nounds for each story
	in the corpus.
	"""

	def __init__(self):
		self.depparser = DependencyParser()

		self.aliases_manager = AliasesManager()
		self.corpus_manager = CorpusManager()

	def get_fpath(self, sid, tpe):
		"""
		Returns the filepath to the (character, concept, noun if tpe is
		'character', 'concept', or 'noun;, respectively) collocates .tsv file
		for the given story.
		"""

		if not self.corpus_manager.belongs(sid):
			raise ValueError(sid +
				" does not correspond to a story in the corpus.")

		dirpath = self.corpus_manager.get_dirpath(sid)
		collocates_dirpath = os.path.join(os.path.join(dirpath, 'collocates'),
			'unmarginalized')

		# WHYYYYYY -Rob
		#if sid == 'a-tale-of-two-cities' or sid == 'peregrine-pickle' or \
		#	sid == 'pride-and-prejudice' or sid == 'to-the-lighthouse' or \
		#	sid == 'tristram-shandy':
		if tpe == 'character' or tpe == 'concept' or tpe == 'noun':
                        return os.path.join(collocates_dirpath, ''.join([tpe, '.tsv']))
		else:
			raise ValueError("'tpe' must be 'character', 'concept', or "
				"'noun'.")
		# Assume story is in a sub-corpus.
		# Nope nope nope, sub-corpus stuff is commented out for now
		#else:
		#	if tpe == 'character':
		#		return os.path.join(os.path.join(collocates_dirpath,
		#			'character'), sid + '.tsv')
		#	elif tpe == 'concept':
		#		return os.path.join(os.path.join(collocates_dirpath, 'concept'),
		#			sid + '.tsv')
		#	elif tpe == 'noun':
		#		return os.path.join(os.path.join(collocates_dirpath, 'noun'),
		#			sid + '.tsv')
		#	else:
		#		raise ValueError("'tpe' must be 'character', 'concept', or "
		#			"'noun'.")
	
	def saved(self, sid, tpe):
		"""
		Checks whether the (character, concept, or noun if tpe is 'character'
		'concept', or 'noun', respectively) collocates .tsv for the given story
		has been generated.
		"""

		return os.path.exists(self.get_fpath(sid, tpe))

	def parse(self, sid, tpe):
		"""
		Generates the collocates .tsv file for the given story and type
		(Overwrites it if it already exists).
		"""

		fpath = self.get_fpath(sid, tpe)
		
		# Create the parent directory if it doesn't already exist.
		dirpath = os.path.split(fpath)[0]
		if not os.path.exists(dirpath):
			os.makedirs(dirpath)

		corenlp_fpath = self.corpus_manager.get_corenlp_fpath(sid)

		character_aliases = self.aliases_manager.get_aliases(sid, 'character')
		aliases = character_aliases if tpe == 'character' else \
			self.aliases_manager.get_aliases(sid, tpe)

		self.depparser.save(corenlp_fpath, aliases, character_aliases, fpath)

	def get(self, sid, tpe, role=None, ranks=None):
		"""
		Returns a list of the collocates from the saved .tsv file (must've first
		been generated using CollocatesManager.parse) for the given story and
		type. (The collocates are automatically joined with the corresponding
		aliases.)

		@param sid - Story Id of story
		@param tpe - 'character', 'concept', or 'noun'
		@param role - Role to filter on (If None (default), all collocates are
			returned)
		@param ranks - List of character ranks to filter on (If None (default),
			collocates for all characters are returned)
		@return List of collocates, with each collocate in the form,

			{
				'type': <Dependency type>,
				'token': {
					'index': <Token index within containing sentence>,
					'lemma': <Token lemma>,
					'word': <Token word>
				}
				'alias': <alias>
			}
		"""

		aliases = self.aliases_manager.get_aliases(sid, tpe)

		# Transform list of aliases to a map keyed by character offsets for easy
		# access.
		alias_dict = {(alias['begin_offset'], alias['end_offset']): alias
			for alias in aliases}

		with open(self.get_fpath(sid, tpe), 'rb') as f:
			reader = csv.reader(f, delimiter='\t', quotechar='"')

			# Skip header.
			next(reader)

			collocates = []
			for row in reader:
				begin_offset, end_offset = int(row[0]), int(row[1])

				coll = {
					'type': row[5],
					'token': {
						'index': int(row[2]),
						'lemma': row[3],
						'word': row[4]
					},
					'alias': alias_dict[(begin_offset, end_offset)]
				}

				if len(row) > 6:
					if row[6] != '':
						coll['prt'] = {
							'index': int(row[6]),
							'lemma': int(row[7])
						}

				if len(row) > 8:
					if row[8] != '':
						coll['vmod'] = {
							'index': int(row[8]),
							'lemma': int(row[9])
						}

				collocates.append(coll)

			# Filter collocates based on the role.
			if role:
				collocates = [coll for coll in collocates
								if map_role(coll['type']) == role]

			# Filter collocates based on the ranks.
			if ranks:
				ranks = set(ranks)
				collocates = [coll for coll in collocates
								if coll['alias']['entity']['rank'] in ranks]

			return collocates

	def get_dtmatrix(self, sids, tpe, role=None, ranks=None, min_df=10,
		normal=False):
		"""
		Calculates the document-term matrix, where documents are stories, and
		terms are collocate words.

		@param sids - List of story Id's
		@param tpe - 'character', 'concept', or 'noun'
		@param role - Role to filter on (If None (default), all collocates are
			considered)
		@param ranks - List of character ranks to filter on (If None (default),
			collocates for all characters are considered)
		@param min_df - Ignore terms that have a document frequency strictly
			lower than the given (integer) threshold
		@param normal - If True, normalize returned matrix (by story)
		@param Document-term matrix (in CSR format) and vectorizer as a pair
		"""

		collocate_words = (' '.join([coll['token']['lemma'] for coll
			in self.get(sid, tpe, role, ranks)]) for sid in sids)
		count_vect = CountVectorizer(min_df=min_df)

		dtmat = count_vect.fit_transform(collocate_words).astype(float)

		if normal:
			return normalize(dtmat), count_vect

		return dtmat, count_vect

