"""
Identifies and manages aliases for all stories.

@author: Hardik
"""

import csv
import json
import os
import sys
import xml.etree.ElementTree as ET

from collections import Counter, defaultdict

from characters import CharactersManager
from concepts import ConceptsManager
from corpus import CorpusManager
from nouns import NounsManager


# Set of pronouns.
PRONOUNS = set(['he', 'her', 'hers', 'herself', 'him', 'himself', 'his', 'I',
	'me', 'my', 'myself', 'our', 'ours', 'ourselves', 'she', 'their', 'theirs',
	'them', 'themselves', 'they', 'us', 'we', 'who', 'whoever', 'whom',
	'whomever', 'you', 'your', 'yourself', 'yourselves'])


class AliasIdentifier(object):
	"""
	Identifies the aliases of characters, concepts, or nouns (retrieved from a
	.json file) in a CoreNLP .xml file and BookNLP .tokens file.
	"""

	def tokreefy(self, entities):
		"""
		"Tokreefies" the given list of characters, concepts, or nouns producing
		a trie-like structure.

		@param entities - List of entitities formatted according to the standard
			.json format (as returned by CharactersManager.get_characters,
			ConceptsManager.get_concepts, NounsManager.get_nouns)
		@return Trie-like structure based on alias tokens with leaf nodes (keyed
			by '_alias') represented as,

			{
				"span": [Alias span],
				"entity": [Character/Concept/Noun identifier],
				"rank": [Rank of the character/concept/noun],
				"count": [# occurrences of the alias]
			}
		"""

		tokree = {}
		for rank, entity in enumerate(entities, start=1):
			for alias in entity['aliases']: 
				subtokree = tokree
				
				for alias_tok in alias['alias'].split():
					if alias_tok not in subtokree:
						subtokree[alias_tok] = {}
					subtokree = subtokree[alias_tok]
				
				subtokree['_alias'] = {
					'span': alias['alias'],
					'entity': entity['entity'],
					'count': alias['count'],
					'rank': rank
				}

		return tokree

	def get_pronouns(self, booknlp_tokens_path, entities):
		"""
		Reads a BookNLP .tokens file, returning the pronouns corresponding to
		the given list of entities.

		@param booknlp_tokens_path - Filepath to BookNLP .tokens
		@param entities - List of entities for which to grab pronoun
			co-referents
		@return Table mapping token index to pronoun, where a pronoun is
			represented by the tuple,

			(<pronoun>, <beginning offset>, <ending offset>, <referent entity>,
				<entity rank>, <pronoun count>)
		"""

		# Read aliases into a dictionary from character Id to list of aliases,
		# with each alias represented as a tuple with token Id (of the first
		# token), name, beginning character offset, and ending character offset.
		aliases_read = defaultdict(list)

		with open(booknlp_tokens_path) as f:
			# Skip header.
			next(f)

			in_char = False
			# Alias name is taken as the lemmas.
			char_id, token_id, alias_name, = -1, -1, ''
			begin_offset, end_offset = -1, -1
			for line in f:
				entries = line.split()

				curr_id = int(entries[-1])
				# Given token doesn't refer to a character.
				if curr_id == -1:
					if in_char:
						aliases_read[char_id].append((token_id, alias_name,
							begin_offset, end_offset))
						in_char = False
					
					continue

				if in_char and curr_id == char_id:
					alias_name += ' ' + entries[7]
					end_offset = int(entries[4])
				elif in_char and curr_id != char_id:
					aliases_read[char_id].append((token_id, alias_name,
						begin_offset, end_offset))

					char_id, token_id = curr_id, int(entries[2])
					alias_name = entries[7]
					begin_offset, end_offset = int(entries[3]), int(entries[4])
				else:
					char_id, token_id = curr_id, int(entries[2])
					alias_name = entries[7]
					begin_offset, end_offset = int(entries[3]), int(entries[4])
					in_char = True

			pronoun_table = {}
			for _, aliases in aliases_read.iteritems():
				names = set([n for _, n, _, _ in aliases])
				pronoun_cntr = Counter([p for _, p, _, _ in aliases
					if p in PRONOUNS])

				character, rank = None, 0
				for i, entity in enumerate(entities, start=1):
					if entity['entity'] in names:
						character, rank = entity, i
						break

				if character:
					for token_id, name, begin_offset, end_offset in aliases:
						if name.lower() in PRONOUNS:
							pronoun_table[token_id] = (name, begin_offset,
								end_offset, character, rank, pronoun_cntr[name])

			return pronoun_table

	def ident(self, tokree, corenlp_filepath, pronoun_table=None):
		"""
		Identifies the instances of aliases from the tokree in the CoreNLP .xml
		located by corenlp_filepath, returning a list of identifed aliases with
		each alias represented as,

		{
			'indices': [List of token indices in the document covered by the
				alias],
			'local_indices': [List of token indices within the sentence covered
				by the alias]
			'begin_offset': [Starting character offset of alias span],
			'end_offset': [Ending character offset of alias span],
			'span': [Alias span],
			'entity': {
				'name': [Character/Concept/Noun identifier],
				'rank': [Rank of the Character/Concept/Noun]
			},
			'count': [# occurrences of the alias]
		}

		cross-referencing with the pronoun table.
		"""

		aliases = []

		e = ET.parse(corenlp_filepath).getroot()

		tok_matches, subtokree, global_tok_ind = [], tokree, -1
		for sent_ind, sent in enumerate(e.iter('sentence')):
			for i, tok in enumerate(sent.find('tokens')):
				tok_ind = i + 1
				global_tok_ind += 1

				if pronoun_table and global_tok_ind in pronoun_table:
					name = pronoun_table[global_tok_ind][0]
					begin_offset = pronoun_table[global_tok_ind][1]
					end_offset = pronoun_table[global_tok_ind][2]
					entity_name = pronoun_table[global_tok_ind][3]['entity']
					rank = pronoun_table[global_tok_ind][4]
					count = pronoun_table[global_tok_ind][5]
					
					aliases.append({
						'sentence_index': sent_ind + 1,
						'indices': [global_tok_ind],
						'local_indices': [tok_ind],
						'begin_offset': begin_offset,
						'end_offset': end_offset,
						'span': name,
						'entity': {
							'name': entity_name,
							'rank': rank
						},
						'count': count
					})

					continue

				tok_text = tok[0].text
				if tok_text in subtokree:
					tok_matches.append((global_tok_ind, tok_ind, tok))
					subtokree = subtokree[tok_text]
				elif len(tok_matches) > 0:
					try:
						alias_leaf = subtokree['_alias']
					except KeyError:
						tok_matches = []
						subtokree = tokree
						continue

					aliases.append({
						'sentence_index': sent_ind + 1,
						'indices': [i for i, _, _ in tok_matches],
						'local_indices': [j for _, j, _ in tok_matches],
						'begin_offset': int(tok_matches[0][2][2].text),
						'end_offset': int(tok_matches[-1][2][3].text),
						'span': alias_leaf['span'],
						'entity': {
							'name': alias_leaf['entity'],
							'rank': alias_leaf['rank']
						},
						'count': alias_leaf['count']
					})

					tok_matches, subtokree = [], tokree

		return aliases

	def save(self, aliases, filepath):
		"""
		Saves the list of identified alaises (as outputted by ident_aliases) to
		a .json file located at filepath.
		"""

		with open(filepath, 'w') as out:
			json.dump(aliases, out, sort_keys=True, indent=4)


class AliasesManager(object):
	"""
	Manages the list of identified aliases for each story in the corpus.
	"""

	def __init__(self):
		self.identifier = AliasIdentifier()
		self.characters_manager = CharactersManager()
		self.concepts_manager = ConceptsManager()
		self.nouns_manager = NounsManager()
		self.corpus_manager = CorpusManager()

	def get_fpath(self, sid, tpe):
		"""
		Returns the filepath to the identified (character, concept, noun if tpe
		is 'character', 'concept', or 'noun', respectively) aliases .json file
		for the given story.
		"""

		if not self.corpus_manager.belongs(sid):
			raise ValueError(sid +
				" does not correspond to a story in the corpus.")

		dirpath = self.corpus_manager.get_dirpath(sid)
		aliases_dirpath = os.path.join(dirpath, 'aliases')

		# What on earth were you doing -Rob
		#if sid == 'a-tale-of-two-cities' or sid == 'peregrine-pickle' or \
		#	sid == 'pride-and-prejudice' or sid == 'to-the-lighthouse' or \
		#	sid == 'tristram-shandy':
		if tpe == 'character' or tpe == 'concept' or tpe == 'noun':
			return os.path.join(aliases_dirpath, ''.join([tpe, '.json']))
		else:
			raise ValueError("'tpe' must be 'character', 'concept', or "
				"'noun'.")
		# Assume story is in a sub-corpus.
		# Commenting this out for now because it is ridiculous
		# else:
		#	if tpe == 'character':
		#		return os.path.join(os.path.join(aliases_dirpath, 'character'),
		#			sid + '.json')
		#	elif tpe == 'concept':
		#		return os.path.join(os.path.join(aliases_dirpath, 'concept'),
		#							sid + '.json')
		#	elif tpe == 'noun':
		#		return os.path.join(os.path.join(aliases_dirpath, 'noun'),
		#							sid + '.json')
		#	else:
		#		raise ValueError("'tpe' must be 'character', 'concept', or "
		#			"'noun'.")
	
	def saved(self, sid, tpe):
		"""
		Checks whether the (character, concept, or noun if tpe is 'character',
		'concept', or 'noun', respectively) aliases .json for the given story
		has been generated.
		"""

		return os.path.exists(self.get_fpath(sid, tpe))

	def ident(self, sid, tpe):
		"""
		Generates the identified aliases .json file for the given story and type
		(Overwrites it if it already exists).
		"""

		fpath = self.get_fpath(sid, tpe)
		
		# Create the parent directory if it doesn't already exist.
		dirpath = os.path.split(fpath)[0]
		if not os.path.exists(dirpath):
			os.makedirs(dirpath)

		if tpe == 'character':
			entities = self.characters_manager.get_characters(sid)
		elif tpe == 'concept':
			entities = self.concepts_manager.get_concepts(sid)
		elif tpe == 'noun':
			entities = self.nouns_manager.get_nouns(sid)
		else:
			raise ValueError("'tpe' must be 'character', 'concept', or 'noun'.")

		tokree = self.identifier.tokreefy(entities)

		booknlp_tokens_path = self.corpus_manager.get_booknlp_tokens(sid)
		pronoun_table = self.identifier.get_pronouns(booknlp_tokens_path,
			entities)

		aliases = self.identifier.ident(tokree,
			self.corpus_manager.get_corenlp_fpath(sid), pronoun_table)

		self.identifier.save(aliases, self.get_fpath(sid, tpe))

	def get_aliases(self, sid, tpe):
		"""
		Retrieves the (character, concept, noun if tpe is 'character',
		'concept', or 'noun', respectively) aliases from the .json file for the
		given story.
		"""

		with open(self.get_fpath(sid, tpe)) as f:
			return json.load(f)
