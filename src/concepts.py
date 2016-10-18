import csv
import json
import os

from collections import Counter

from corpus import CorpusManager
from unigrams import UnigramsManager


CONCEPTS = set(['man', 'woman', 'life', 'mind'])


class ConceptsFromUnigramsExtractor(object):
	"""
	Extracts a concepts from a unigram counts .tsv file.
	"""

	def __init__(self):
		pass

	def extract(self, unigrams_path):
		"""
		Extracts the concepts from the unigram counts .tsv file located by the
		give path.
		"""

		concept_counter = Counter()
		with open(unigrams_path, 'rb') as f:
			reader = csv.reader(f, delimiter='\t', quotechar='"')
			for row in reader:
				if row[0] in CONCEPTS:
					concept_counter[row[0]] += int(row[2])

		return [{
					'aliases': [
						{
							'alias': concept,
							'count': count
						}
					],
					'character': concept,
					'count': count
				}
				for concept, count
				in sorted(concept_counter.items(), key=lambda i: -i[1])]

	def save(self, concepts, out_path):
		"""
		Outputs the given list of concepts (As returned by extract) to a .json
		file specified by the given filepath.
		"""

		with open(out_path, 'w') as f:
			json.dump(concepts, f, sort_keys=True, indent=4)


class ConceptsManager(object):
	"""
	Manages the list of concepts for each story in the corpus.
	"""

	def __init__(self):
		self.extractor = ConceptsFromUnigramsExtractor()
		self.cm = CorpusManager()
		self.um = UnigramsManager()

	def get_fpath(self, sid):
		"""
		Returns the filepath to the concepts .json file for the given story.
		"""

		if not self.cm.belongs(sid):
			raise ValueError(sid +
				" does not correspond to a story in the corpus.")

		dirpath = self.cm.get_dirpath(sid)

		# I don't even know what this is doing, so commenting out. -Rob
		#if sid == 'a-tale-of-two-cities' or sid == 'to-the-lighthouse':
		return os.path.join(dirpath, 'concepts.json')
		# Assume story is in piper corpus.
		#else:
		#	return os.path.join(os.path.join(dirpath, 'concepts'), sid + '.json')

	def saved(self, sid):
		"""
		Checks whether the concepts .json for the given story has been
		generated.
		"""
		print self.get_fpath(sid)
		return os.path.exists(self.get_fpath(sid))

	def gen(self, sid):
		"""
		Generates the concepts .json file for the given story (Overwrites it
		if it already exists).
		"""

		concepts = self.extractor.extract(self.um.get_fpath(sid))
		self.extractor.save(concepts, self.get_fpath(sid))

	def get_concepts(self, sid):
		"""
		Retrieves the concepts dictioanry for the given story from the stored
		.json file for the given story (Must exist and if not, generate it with
		ConceptsManager.gen).
		"""

		with open(self.get_fpath(sid)) as f:
			return json.load(f)
