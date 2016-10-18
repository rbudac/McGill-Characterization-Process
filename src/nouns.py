"""
Manages the nouns in each story.

@author: Hardik
"""

import csv
import json
import os
import xml.etree.ElementTree as ET

from collections import Counter

from corpus import CorpusManager
from unigrams import UnigramsManager


class NounsExtractor(object):
	"""
	Extracts nouns from a CoreNLP .xml file.
	"""

	def __init__(self):
		pass

	def extract(self, corenlp_fpath, aliases):
		"""
		Extracts the nouns from a CoreNLP .xml file, skipping over any noun that
		is covered by an alias.

		@param corenlp_fpath - Path to CoreNLP .xml file
		@param aliases - List of aliases to check against (as returned by
			AliasesManager.ident)
		@return List of nouns in reverse order of frequency (formatted according
			to CharactersManager.get_characters)
		"""

		alias_indices = set(i for a in aliases for i in a['indices'])
		
		corenlp_xml = ET.parse(corenlp_fpath).getroot()
		noun_cntr = Counter([t[1].text for i, t
			in enumerate(corenlp_xml.iter('token'))
			if i not in alias_indices and t[4].text[0] == 'N'])

		return [{
					'aliases': [
						{
							'alias': noun,
							'count': cnt
						}
					],
					'entity': noun,
					'count': cnt
				}
				for noun, cnt
				in sorted(noun_cntr.items(), key=lambda i: -i[1])
				# Only consider lowercase nouns.
				if noun == noun.lower()]

		return unigram_cnts

	def save(self, nouns, out_path):
		"""
		Outputs the given list of nouns (as returned by NounsExtractor.extract)
		to a .json file.

		@param nouns - List of nouns (as returned by NounsExtractor.extract)
		@param out_path - Path to output .json file.
		"""

		with open(out_path, 'w') as f:
			json.dump(nouns, f, sort_keys=True, indent=4)


# TODO: Update descriptions with @param and @return info.
class NounsManager(object):
	"""
	Manages the list of nouns for each story in the corpus.
	"""

	def __init__(self):
		self.extractor = NounsExtractor()

		self.corpus_manager = CorpusManager()

	def get_fpath(self, sid):
		"""
		Returns the filepath to the nouns .json file for the given story.
		"""

		if not self.corpus_manager.belongs(sid):
			raise ValueError(sid +
				" does not correspond to a story in the corpus.")

		dirpath = self.corpus_manager.get_dirpath(sid)

		# Don't do this -Rob
		#if sid == 'a-tale-of-two-cities' or sid == 'peregrine-pickle' or \
		#	sid == 'pride-and-prejudice' or sid == 'to-the-lighthouse' or \
		#	sid == 'tristram-shandy':
		return os.path.join(dirpath, 'nouns.json')
		# Assume story is in a sub-corpus.
		# Sub corpus stuff commented out.
		#else:
		#	return os.path.join(os.path.join(dirpath, 'nouns'), sid + '.json')

	def saved(self, sid):
		"""
		Checks whether the nouns .json for the given story has been
		generated.
		"""

		return os.path.exists(self.get_fpath(sid))

	def gen(self, sid):
		"""
		Generates the nouns .json file for the given story (Overwrites it
		if it already exists).
		"""

		# Returns the character aliases for the given story (Formatted
		# according to AliasesManager.get_aliases).
		def get_aliases(sid):
			if not self.corpus_manager.belongs(sid):
				raise ValueError(sid +
					" does not correspond to a story in the corpus.")

			dirpath = self.corpus_manager.get_dirpath(sid)
			aliases_dirpath = os.path.join(dirpath, 'aliases')

			# STOOOOP -Rob
			#if sid == 'a-tale-of-two-cities' or sid == 'peregrine-pickle' or \
			#	sid == 'pride-and-prejudice' or sid == 'to-the-lighthouse' or \
			#	sid == 'tristram-shandy':
			fpath = os.path.join(aliases_dirpath, 'character.json')
			# Commenting out sub corpus functionality.
			# Assume story is in a sub-corpus.
			#else:
			#	fpath = os.path.join(os.path.join(aliases_dirpath, 'character'),
			#		sid + '.json')

			with open(fpath) as f:
				return json.load(f)

		corenlp_fpath = self.corpus_manager.get_corenlp_fpath(sid)
		aliases = get_aliases(sid)
		nouns = self.extractor.extract(corenlp_fpath, aliases)

		out_path = self.get_fpath(sid)

		par_dirpath = os.path.split(out_path)[0]
		if not os.path.exists(par_dirpath):
			os.makedirs(par_dirpath)

		self.extractor.save(nouns, out_path)

	def get_nouns(self, sid):
		"""
		Retrieves the nouns dictionary for the given story from the stored
		.json file for the given story (Must exist and if not, generate it with
		NounsManager.gen).
		"""

		with open(self.get_fpath(sid)) as f:
			return json.load(f)
