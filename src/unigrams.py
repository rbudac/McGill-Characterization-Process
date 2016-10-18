import json
import csv
import os
import xml.etree.ElementTree as ET

from collections import Counter, defaultdict

from corpus import CorpusManager


class UnigramCounter(object):
	"""
	Counts the unigrams (lemma + simplified POS tag) from CoreNLP .xml files.
	"""

	# TODO: Incorporate dependency into unigram definition.

	def get_indices(self, aliases):
	    """
	    Returns the set of indices covered by the given identified aliases.
	    """

	    return set(i for a in aliases for i in a['indices'])

	def get_character_cnts(self, aliases):
	    """
	    Returns a character counter from the given list of identified aliases.
	    """

	    character_map = defaultdict(dict)
	    for a in aliases:
	        character_map[a['character']][a['span']] = a['count']

	    character_counter = Counter()
	    for c, a_map in character_map.iteritems():
	        character_counter[c] = sum(a_map.values())

	    return character_counter

	def get_character_ranks(self, aliases):
	    """
	    Returns a mapping from character to rank from the given list of
	    identified aliases.
	    """

	    return {a['character']: a['character_rank'] for a in aliases}

	def count(self, corenlp_fpath, aliases):
		"""
		Returns a unigram counter from the CoreNLP XML retrieved from the given
		filepath, replacing character aliases with ALIAS-n (for the nth ranked
		character).
		"""

		alias_indices = self.get_indices(aliases)
		corenlp_xml = ET.parse(corenlp_fpath).getroot()

		unigram_cnts = Counter([(t[1].text, t[4].text[0])
		                            for i, t
		                            in enumerate(corenlp_xml.iter('token'))
		                            if i not in alias_indices])

		character_cnts = self.get_character_cnts(aliases)
		character_ranks = self.get_character_ranks(aliases)

		for c, cnt in character_cnts.iteritems():
		    unigram_cnts[('ALIAS-%d' % character_ranks[c], 'N')] = cnt

		return unigram_cnts

	def save(self, unigram_cnts, filepath):
		"""
		Saves the given unigram counts as a .tsv file at filepath.
		"""

		with open(filepath, 'wb') as out:
		    writer = csv.writer(out, delimiter='\t', quotechar='"')
		    for unigram, cnt in sorted(unigram_cnts.items(),
		        key=lambda i: -i[1]):
		        writer.writerow([unigram[0].encode('utf-8'),
		            unigram[1].encode('utf-8'), cnt])


class UnigramsManager(object):
	"""
	Manages the unigrams for each story in the corpus, as well as the whole
	corpus.
	"""

	def __init__(self):
		self.corpus_manager = CorpusManager()
		self.unigram_counter = UnigramCounter()

	def get_fpath(self, sid):
		"""
		Returns the filepath to the unigram counts for the given story.
		"""

		dirpath = self.corpus_manager.get_dirpath(sid)

		# Again, don't know what the piper corpus is or anything,
		# so commenting out. -Rob
		#if sid == 'a-tale-of-two-cities' or sid == 'to-the-lighthouse':
		return os.path.join(dirpath, 'unigrams.tsv')
		# Assume story is in piper corpus.
		#else:
		#	return os.path.join(os.path.join(dirpath, 'unigrams'), sid + '.tsv')
	
	def saved(self, sid):
		"""
		Checks whether the unigram counts .tsv file for the given story has been
		generated.
		"""

		return os.path.exists(self.get_fpath(sid))

	def gen(self, sid):
		"""
		Generates the unigram counts .tsv file for the given story. 
		"""

		# Returns the character aliases for the given story from the stored
		# .json file (Must exist).
		def get_character_aliases(sid):
			dirpath = self.corpus_manager.get_dirpath(sid)
			aliases_dirpath = os.path.join(dirpath, 'aliases')

			#AGAIN, what is this for?? -Rob
			#if sid == 'a-tale-of-two-cities' or sid == 'to-the-lighthouse':
			fpath = os.path.join(aliases_dirpath, 'character.json')
			# Assume story is in piper corpus.
			#else:
			#	fpath = os.path.join(os.path.join(aliases_dirpath, 'character'),
			#		sid + '.json')

			with open(fpath) as f:
				return json.load(f)

		fpath = self.get_fpath(sid)
		
		# Create the parent directory if it doesn't already exist.
		dirpath = os.path.split(fpath)[0]
		if not os.path.exists(dirpath):
			os.makedirs(dirpath)

		corenlp_fpath = self.corpus_manager.get_corenlp_fpath(sid)
		aliases = get_character_aliases(sid)
		unigram_cnts = self.unigram_counter.count(corenlp_fpath, aliases)
		self.unigram_counter.save(unigram_cnts, fpath)

	def get(self, sid):
		"""
		Returns the unigram counts (as a Counter) for the given story (as stored
		in the story's unigram counts .tsv file).
		"""

		unigram_cntr = Counter()
		with open(self.get_fpath(sid), 'rb') as f:
			reader = csv.reader(f, delimiter='\t', quotechar='"')

			for row in reader:
				unigram_cntr[(row[0], row[1])] = int(row[2])

			return unigram_cntr

	def get_doc_counts(self):
		"""
		Returns a Counter of the document frequency of each unigram across the
		entire corpus.
		"""

		doc_cntr = Counter()

		for sid in self.corpus_manager.get_ids(origin='gen'):
			if not self.saved(sid):
				continue

			for unigram in self.get(sid):
				doc_cntr[unigram] += 1

		return doc_cntr
