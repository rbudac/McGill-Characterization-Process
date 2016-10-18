"""
Parses collocates around a list of enitity aliases by parsing specific
dependency relations. (The project dependency types differ slightly from the
Stanford dependency types and so assume any mention of "dependency types" below
refers to the former, unless specified otherwise.)

@author: Hardik
"""

import csv
import os
import json
import sys

from collections import defaultdict
from corenlp_xml.document import Document
from corenlp_xml.dependencies import DependencyGraph


# List of defined dependency types.
TYPES = ['acomp', 'agent-verb', 'agent-nusbj', 'agent-nusbjpass', 'amod',
	'appos', 'dobj-verb', 'dobj-nsubj', 'dobj-nsubjpass', 'dobj-iobj',
	'iobj-verb', 'iobj-nsubj', 'iobj-nsubjpass', 'iobj-dobj', 'nmod:of',
	'nsubj-verb', 'nsubj-noun', 'nsubj-adj', 'nsubj-dobj', 'nsubj-iobj',
	'nsubjpass-verb', 'nsubjpass-dobj', 'nsubjpass-iobj', 'poss', 'pobj']


class DependencyParser(object):
	"""
	Parses collocates around a list of enitity aliases using specific dependency
	relation parse rules. The (Stanford) dependency types of interest are the
	following: acomp, nmod:agent, amod, appos, dobj, iobj, nsubj, nsubjpass,
	pobj, nmod:poss, compound:prt, and vmod.
	"""

	def __init__(self):
		pass

	def parse(self, doc, alias, types=None):
		"""
		Parses the collocates around the given alias according to a list of
		desired dependency types.

		@param doc - Document to extract from (corenlp_xml.document.Document)
		@param alias - Alias of interest (as returned by AliasManager.ident)
		@param types - List of desired dependency types (if None, the default,
			all types are considered)
		@return List of collocates with each collocate taking the form,
			{
				'type': <Dependency type>,
				'token': {
					'index': <Token index within containing sentence>,
					'lemma': <Token lemma>
				}
			}
		"""

		collocates = []

		# TODO: Comment.
		def extract_siblings(governor, types):
			g = graph.get_node_by_idx(governor.idx)
			return [sib for t in types for sib in g.dependents_by_type(t)]

		# TODO: Comment.
		def is_sibling(governor, types):
			return any(sib.idx in alias['local_indices'] for sib
				in extract_siblings(governor, types))

		sentence = doc.get_sentence_by_id(alias['sentence_index'])
		graph = sentence.collapsed_ccprocessed_dependencies

		def get_token_info(tok_idx):
			tok = sentence.get_token_by_id(tok_idx)
			return {
				'index': tok_idx,
				'lemma': tok.lemma,
				'word': tok.word
			}

		def get_pos(tok_idx):
			return sentence.get_token_by_id(tok_idx).pos

		if types is None or 'acomp' in types:
			for link in graph.links_by_type('acomp'):
				if is_sibling(link.governor, ['nsubj', 'nsubjpass']):
					collocates.append({
						'type': 'acomp',
						'token': get_token_info(link.dependent.idx)
					})

		if types is None or 'agent' in types:
			for link in graph.links_by_type('nmod:agent'):
				if link.dependent.idx in alias['local_indices']:
					collocates.append({
						'type': 'agent-verb',
						'token': get_token_info(link.governor.idx)
					})

					for sib in extract_siblings(link.governor, ['nsubj']):
						collocates.append({
							'type': 'agent-nusbj',
							'token': get_token_info(sib.idx)
						})

					for sib in extract_siblings(link.governor, ['nsubjpass']):
						collocates.append({
							'type': 'agent-nusbjpass',
							'token': get_token_info(sib.idx)
						})

		if types is None or 'amod' in types:
			for link in graph.links_by_type('amod'):
				if link.governor.idx in alias['local_indices']:
					collocates.append({
						'type': 'amod',
						'token': get_token_info(link.dependent.idx)
					})

		if types is None or 'appos' in types:
			for link in graph.links_by_type('appos'):
				if link.governor.idx in alias['local_indices']:
					collocates.append({
						'type': 'appos',
						'token': get_token_info(link.dependent.idx)
					})

					# Rules recursively applied here.
					appos_alias = {
						'sentence_index': alias['sentence_index'],
						'local_indices': [link.dependent.idx]
					}

					collocates += self.parse(doc, appos_alias)

		if types is None or 'dobj' in types:
			for link in graph.links_by_type('dobj'):
				if link.dependent.idx in alias['local_indices']:
					collocates.append({
						'type': 'dobj-verb',
						'token': get_token_info(link.governor.idx)
					})

					for sib in extract_siblings(link.governor, ['nsubj']):
						collocates.append({
							'type': 'dobj-nsubj',
							'token': get_token_info(sib.idx)
						})

					for sib in extract_siblings(link.governor, ['nsubjpass']):
						collocates.append({
							'type': 'dobj-nsubjpass',
							'token': get_token_info(sib.idx)
						})

					for sib in extract_siblings(link.governor, ['iobj']):
						collocates.append({
							'type': 'dobj-iobj',
							'token': get_token_info(sib.idx)
						})

		if types is None or 'iobj' in types:
			for link in graph.links_by_type('iobj'):
				if link.dependent.idx in alias['local_indices']:
					collocates.append({
						'type': 'iobj-verb',
						'token': get_token_info(link.governor.idx)
					})

					for sib in extract_siblings(link.governor, ['nsubj']):
						collocates.append({
							'type': 'iobj-nsubj',
							'token': get_token_info(sib.idx)
						})

					for sib in extract_siblings(link.governor, ['nsubjpass']):
						collocates.append({
							'type': 'iobj-nsubjpass',
							'token': get_token_info(sib.idx)
						})

					for sib in extract_siblings(link.governor, ['dobj']):
						collocates.append({
							'type': 'iobj-dobj',
							'token': get_token_info(sib.idx)
						})

		if types is None or 'nmod:of' in types:
			for link in graph.links_by_type('nmod:of'):
				if link.governor.idx in alias['local_indices']:
					collocates.append({
						'type': 'nmod:of',
						'token': get_token_info(link.dependent.idx)
					})

		if types is None or 'nsubj' in types:
			for link in graph.links_by_type('nsubj'):
				if link.dependent.idx in alias['local_indices']:
					pos = get_pos(link.governor.idx)[0]
					dep_type = 'nsubj-verb' if pos == 'V' else ('nsubj-noun' 
						if pos == 'N' else 'nsub-adj')
					collocates.append({
						'type': dep_type,
						'token': get_token_info(link.governor.idx)
					})

					# If the governor is a noun, then extract that noun's amods
					# and nmod:of's.
					if get_pos(link.governor.idx)[0] == 'N':
						gov_alias = {
							'sentence_index': alias['sentence_index'],
							'local_indices': [link.governor.idx]
						}

						collocates += self.parse(doc, gov_alias, types=['amod'])
						collocates += self.parse(doc, gov_alias,
							types=['nmod:of'])

					for sib in extract_siblings(link.governor, ['dobj']):
						collocates.append({
							'type': 'nsubj-dobj',
							'token': get_token_info(sib.idx)
						})

					for sib in extract_siblings(link.governor, ['iobj']):
						collocates.append({
							'type': 'nsubj-iobj',
							'token': get_token_info(sib.idx)
						})

		if types is None or 'nsubjpass' in types:
			for link in graph.links_by_type('nsubjpass'):
				if link.dependent.idx in alias['local_indices']:
					collocates.append({
						'type': 'nsubjpass-verb',
						'token': get_token_info(link.governor.idx)
					})

					for sib in extract_siblings(link.governor, ['dobj']):
						collocates.append({
							'type': 'nsubjpass-dobj',
							'token': get_token_info(sib.idx)
						})

					for sib in extract_siblings(link.governor, ['iobj']):
						collocates.append({
							'type': 'nsubjpass-iobj',
							'token': get_token_info(sib.idx)
						})

		if types is None or 'poss' in types:
			for link in graph.links_by_type('nmod:poss'):
				if link.dependent.idx in alias['local_indices']:
					collocates.append({
						'type': 'poss',
						'token': get_token_info(link.governor.idx)
					})

		if types is None or 'pobj' in types:
			for link in graph.links_by_type('pobj'):
				if any(prep_link.governor.idx == coll['token']['index']
					for prep_link in graph.links_by_type('prep')
					for coll in collocates):
					collocates.append({
						'type': 'pobj',
						'token': get_token_info(link.dependent.idx)
					})

		# Attach phrasal verb particles.
		for link in graph.links_by_type('compund:prt'):
			for coll in collocates:
				if link.governor.idx == coll['token']['index']:
					coll['prt'] = get_token_info(link.dependent.idx)

		# Attach reduced non-finite verbal modifier.
		for link in graph.links_by_type('vmod'):
			for coll in collocates:
				if link.governor.idx == coll['token']['index']:
					coll['vmod'] = get_token_info(link.dependent.idx)

		return collocates

	def parse_doc(self, fpath, aliases, character_aliases):
		"""
		Parses the collocates around a list of aliases in a CoreNLP .xml file.
		Character aliases appearing as collocates are given the designation
		'CHAR-r', where r is the rank of the character corresponding to the
		alias.		

		@param fpath - Filepath to CoreNLP .xml file
		@param aliases - List of aliases (as returned by AliasManager.ident)
		@param character_aliases - List of character aliases (as returned by
			AliasManager.ident)
		@return List of collocates with each collocate taking the form,
			{
				'type': <Dependency type>,
				'token': {
					'index': <Token index within containing sentence>,
					'lemma': <Token lemma>
				}
			}
		"""		

		# Tests equality between two aliases.
		def alias_equals(alias1, alias2):
			return alias1['begin_offset'] == alias2['begin_offset'] and \
				alias1['end_offset'] == alias2['end_offset']

		# Arrange aliases into a table keyed by sentence index.
		if character_aliases is not None:
			chalias_dict = defaultdict(list)
			for alias in character_aliases:
				chalias_dict[alias['sentence_index']].append(alias)

		with open(fpath) as f:
			# Document model.
			doc = Document(f.read())

			for alias in aliases:
				for coll in self.parse(doc, alias):
					coll['alias'] = alias
					
					if character_aliases is not None:
						for chalias in chalias_dict[alias['sentence_index']]:
							if not alias_equals(alias, chalias) and \
								coll['token']['index'] in \
								chalias['local_indices']:
								coll['token']['lemma'] = 'CHAR-' + \
									str(chalias['entity']['rank'])

					yield coll

	def save(self, fpath, aliases, character_aliases, outpath):
		"""
		Saves the collocates for the given CoreNLP .xml file and list of aliases
		as a .tsv file. Character aliases appearing as collocates are given the
		designation 'CHAR-r', where r is the rank of the character corresponding
		to the alias. The column headers in the output are the following (in
		order):

		BEGIN_OFFSET - Beginning character offset of the alias span
		END_OFFSET - Ending character offset of the alias span (BEGIN_OFFSET and
			END_OFFSET uniquely identify the alias)
		INDEX - Token index of the collocate
		LEMMA - Lemma of the collocate
		WORD - Collocate word
		TYPE - Type of the dependency relation
		PRT_INDEX - Particle token index (if it exists, otherwise blank)
		PRT_LEMMA - Particle lemma (if it exists, otherwise blank)
		VMOD_INDEX - Verbal modifier token index (if it exists, otherwise blank)
		VMOD_LEMMA - Verbal modifier lemma (if it exists, otherwise blank)

		@param: fpath - Filepath to CoreNLP .xml file
		@param: aliases - List of aliases (as returned by AliasIdentifier.ident)
		@param character_aliases - List of character aliases (as returned by
			AliasManager.ident)
		@param: outpath - Output .tsv filepath
		"""

		collocates = self.parse_doc(fpath, aliases, character_aliases)

		with open(outpath, 'wb') as out:
			writer = csv.writer(out, delimiter='\t', quotechar='"')

			# Header.
			writer.writerow(['BEGIN_OFFSET', 'END_OFFSET', 'INDEX', 'LEMMA',
				'WORD', 'TYPE', 'PRT_INDEX', 'PRT_LEMMA', 'VMOD_INDEX',
				'VMOD_LEMMA'])

			for coll in collocates:
				row = [coll['alias']['begin_offset'],
					coll['alias']['end_offset'], coll['token']['index'],
					coll['token']['lemma'], coll['token']['word'], coll['type']]
				
				if 'prt' in coll and 'vmod' in coll:
					row += [coll['prt']['index'], coll['prt']['lemma'],
						coll['vmod']['index'], coll['vmod']['lemma']]
				elif 'prt' in coll:
					row += [coll['prt']['index'], coll['prt']['lemma']]
				elif 'vmod' in coll:
					row += ['', '', coll['vmod']['index'],
						coll['vmod']['lemma']]

				for i in range(len(row)):
					if isinstance(row[i], basestring):
						row[i] = row[i].encode('utf-8')

				writer.writerow(row)
