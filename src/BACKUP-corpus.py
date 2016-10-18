"""
Manages corpora.

@author: Hardik
"""

import csv
import os
import sys


# Data directory path.
DATA_DIRPATH = "/home/ubuntu/work/ra/noveltm/characterization/data"


class StoryManager(object):
	"""
	Manages the data files (text, CoreNLP .xml, and BookNLP .html) for a given
	story.
	"""

	# Inititalizes the manager with the given root directory, BookNLP .html,
	# CoreNLP .xml, and text paths. If not specified, then the paths are
	# initialized to defaults (except for the root directory path).
	def __init__(self, dirpath, booknlp_fpath=None, corenlp_fpath=None,
		text_fpath=None):
		self.dirpath = dirpath
		self.booknlp_fpath = (os.path.join(os.path.join(self.dirpath, 'booknlp'),
			'book.id.html') if booknlp_fpath is None else booknlp_fpath)
		self.corenlp_fpath = (os.path.join(self.dirpath, 'corenlp.xml')
			if corenlp_fpath is None else corenlp_fpath)
		self.text_fpath = (os.path.join(os.path.join(self.dirpath, 'texts'), 
			'orig.txt') if text_fpath is None else text_fpath)

		booknlp_dirpath = os.path.dirname(self.booknlp_fpath)
		# Path to BookNLP tokens file, assumed to be in the BookNLP directory.
		self.booknlp_tokens_fpath = os.path.join(booknlp_dirpath,
			'book.id.tokens')

	def get_id(self):
		"""
		Returns the story id.
		"""

		raise NotImplementedError

	def get_date(self):
		"""
		Returns the story publication date.

		@return Story publication date (as an integer)
		"""

		raise NotImplementedError

	def get_wc(self):
		"""
		Returns the story word count.

		@return Word count
		"""

		raise NotImplementedError

	def has_booknlp(self):
		"""
		Checks if the BookNLP .html file has been generated.
		"""

		return os.path.exists(self.booknlp_fpath)

	def has_corenlp(self):
		"""
		Checks if the CoreNLP .xml file has been generated.
		"""

		return os.path.exists(self.corenlp_fpath)


class ATaleOfTwoCitiesStoryManager(StoryManager):
	"""
	Manages the data files (text, CoreNLP .xml, and BookNLP .html) for the story
	'A Tale of Two Cities', by Charles Dickens.
	"""

	# Inititalizes the manager with the given root directory, BookNLP .html,
	# CoreNLP .xml, and text paths. If not specified, then the paths are
	# initialized to defaults.
	def __init__(self, dirpath=None, booknlp_fpath=None, corenlp_fpath=None,
		text_fpath=None):
		if dirpath is None:
			dirpath = os.path.join(DATA_DIRPATH, 'a-tale-of-two-cities')

		super(ATaleOfTwoCitiesStoryManager, self).__init__(dirpath=dirpath,
			booknlp_fpath=booknlp_fpath, corenlp_fpath=corenlp_fpath,
			text_fpath=text_fpath)

	def get_id(self):
		"""
		Returns the story id.
		"""

		return 'a-tale-of-two-cities'

	def get_date(self):
		"""
		Returns the story publication date.

		@return Story publication date (as an integer)
		"""

		return 1859

	def get_wc(self):
		"""
		Returns the story word count.

		@return Word count
		"""

		return 135587


class PeregrinePickleManager(StoryManager):
	"""
	Manages the data files (text, CoreNLP .xml, and BookNLP .html) for the story
	'The Adventures of Peregrine Pickle', by Tobias Smollett.
	"""

	# Inititalizes the manager with the given root directory, BookNLP .html,
	# CoreNLP .xml, and text paths. If not specified, then the paths are
	# initialized to defaults.
	def __init__(self, dirpath=None, booknlp_fpath=None, corenlp_fpath=None,
		text_fpath=None):
		if dirpath is None:
			dirpath = os.path.join(DATA_DIRPATH, 'peregrine-pickle')

		super(PeregrinePickleManager, self).__init__(dirpath=dirpath,
			booknlp_fpath=booknlp_fpath, corenlp_fpath=corenlp_fpath,
			text_fpath=text_fpath)

		booknlp_dirpath = os.path.dirname(self.booknlp_fpath)
		# Path to BookNLP tokens file, assumed to be in the BookNLP directory.
		self.booknlp_tokens_fpath = os.path.join(booknlp_dirpath, 'tokens')

	def get_id(self):
		"""
		Returns the story id.
		"""

		return 'peregrine-pickle'

	def get_date(self):
		"""
		Returns the story publication date.

		@return Story publication date (as an integer)
		"""

		return 1751

	def get_wc(self):
		"""
		Returns the story word count.

		@return Word count
		"""

		return 349133


class PrideAndPrejudiceManager(StoryManager):
	"""
	Manages the data files (text, CoreNLP .xml, and BookNLP .html) for the story
	'Pride and Prejudice', by Jane Austen.
	"""

	# Inititalizes the manager with the given root directory, BookNLP .html,
	# CoreNLP .xml, and text paths. If not specified, then the paths are
	# initialized to defaults.
	def __init__(self, dirpath=None, booknlp_fpath=None, corenlp_fpath=None,
		text_fpath=None):
		if dirpath is None:
			dirpath = os.path.join(DATA_DIRPATH, 'pride-and-prejudice')

		super(PrideAndPrejudiceManager, self).__init__(dirpath=dirpath,
			booknlp_fpath=booknlp_fpath, corenlp_fpath=corenlp_fpath,
			text_fpath=text_fpath)

	def get_id(self):
		"""
		Returns the story id.
		"""

		return 'pride-and-prejudice'

	def get_date(self):
		"""
		Returns the story publication date.

		@return Story publication date (as an integer)
		"""

		return 1813

	def get_wc(self):
		"""
		Returns the story word count.

		@return Word count
		"""

		return 121562


class ToTheLighthouseStoryManager(StoryManager):
	"""
	Manages the data files (text, CoreNLP .xml, and BookNLP .html) for the story
	'To The Lighthouse', by Virginia Woolf.
	"""

	# Default path to story data directory.
	DIRPATH = "/home/ndg/project/shared_datasets/narrative/characterization/data/to-the-lighthouse"

	# Inititalizes the manager with the given root directory, BookNLP .html,
	# CoreNLP .xml, and text paths. If not specified, then the paths are
	# initialized to defaults.
	def __init__(self, dirpath=None, booknlp_fpath=None, corenlp_fpath=None,
		text_fpath=None):
		if dirpath is None:
			dirpath = os.path.join(DATA_DIRPATH, 'to-the-lighthouse')

		super(ToTheLighthouseStoryManager, self).__init__(dirpath=dirpath,
			booknlp_fpath=booknlp_fpath, corenlp_fpath=corenlp_fpath,
			text_fpath=text_fpath)

	def get_id(self):
		"""
		Returns the story id.
		"""

		return 'to-the-lighthouse'

	def get_date(self):
		"""
		Returns the story publication date.

		@return Story publication date (as an integer)
		"""

		return 1927

	def get_wc(self):
		"""
		Returns the story word count.

		@return Word count
		"""

		return 69316


class TristramShandyManager(StoryManager):
	"""
	Manages the data files (text, CoreNLP .xml, and BookNLP .html) for the story
	'The Life and Opinions of Tristram Shandy, Gentleman', by Laurence Sterne.
	"""

	# Inititalizes the manager with the given root directory, BookNLP .html,
	# CoreNLP .xml, and text paths. If not specified, then the paths are
	# initialized to defaults.
	def __init__(self, dirpath=None, booknlp_fpath=None, corenlp_fpath=None,
		text_fpath=None):
		if dirpath is None:
			dirpath = os.path.join(DATA_DIRPATH, 'tristram-shandy')

		super(TristramShandyManager, self).__init__(dirpath=dirpath,
			booknlp_fpath=booknlp_fpath, corenlp_fpath=corenlp_fpath,
			text_fpath=text_fpath)

		booknlp_dirpath = os.path.dirname(self.booknlp_fpath)
		# Path to BookNLP tokens file, assumed to be in the BookNLP directory.
		self.booknlp_tokens_fpath = os.path.join(booknlp_dirpath, 'tokens')

	def get_id(self):
		"""
		Returns the story id.
		"""

		return 'tristram-shandy'

	def get_date(self):
		"""
		Returns the story publication date.

		@return Story publication date (as an integer)
		"""

		return 1760

	def get_wc(self):
		"""
		Returns the story word count.

		@return Word count
		"""

		return 187359


class SubCorpusManager(object):
	"""
	Manages the base files (text, CoreNLP .xml, and BookNLP .html) for a
	sub-corpus.
	"""

	# Inititalizes the manager with the given root, BookNLP, CoreNLP, and text
	# directory paths. If not specified, then the paths are initialized to
	# defaults (except for the root directory path).
	def __init__(self, dirpath, booknlp_dirpath=None, corenlp_dirpath=None,
		text_dirpaths=None):
		self.dirpath = dirpath
		self.booknlp_dirpath = (os.path.join(self.dirpath, 'booknlp')
			if booknlp_dirpath is None else booknlp_dirpath)
		self.corenlp_dirpath = (os.path.join(self.dirpath, 'corenlp')
			if corenlp_dirpath is None else corenlp_dirpath)
		self.text_dirpaths = ([os.path.join(os.path.join(self.dirpath, 'texts'), 
			'orig')] if text_dirpaths is None else text_dirpaths)

	def get_ids(self, origin):
		"""
		Returns a list of sub-corpus story Id's.

		@param origin - If origin is 'all', 'gen', or 'novels', then all the
			Id's, the Id's corresponding to stories for which the CoreNLP .xml
			and BookNLP files have been generated, or only the novel Id's (if
			applicable) are returned, respectively
		@return List of story Id's in sub-corpus, in alphabetical order
		"""

		if origin == 'all':
			raise NotImplementedError
		elif origin == 'gen':
			bids, cids = [], []

			for parent, subdirnames, fnames in os.walk(self.booknlp_dirpath):
				for fname in fnames:
					if fname.endswith('.html'):
						bids.append(os.path.basename(parent))

			for fname in os.listdir(self.corenlp_dirpath):
				if fname.endswith('.xml'):
					cids.append(fname.split('.')[0])

			return sorted(set(bids) & set(cids))
		elif origin == 'novels':
			raise NotImplementedError
		else:
			raise ValueError("'origin' argument must be 'all', 'gen', or "
				"'novels'.")

	def get_dates(self):
		"""
		Returns the publication dates for all stories in the sub-corpus.

		@return Map from story Id to publication date (as an integer)
		"""

		raise NotImplementedError

	def get_wcs(self):
		"""
		Returns the word counts for all stories in the sub-corpus.

		@return Map from story Id to word count
		"""

		wcs = {}
		for path in self.get_text_paths():
			fname = os.path.basename(path)

			with open(path) as f:
				wcs[fname[:-4]] = len(f.read().split())

		return wcs

	def get_booknlp_fpath(self, sid):
		"""
		Returns the filepath to the BookNLP .html for the given story.

		@param sid - Story Id of story
		@return Filepath to BookNLP .html
		"""

		return os.path.join(os.path.join(self.booknlp_dirpath, sid),
			'book.id.html')

	def get_booknlp_tokens(self, sid):
		"""
		Returns the filepath to the BookNLP .tokens for the given story.

		@param sid - Story Id of story
		@return Filepath to BookNLP .tokens
		"""

		booknlp_dirpath = os.path.dirname(self.get_booknlp_fpath(sid))
		# Path to BookNLP tokens file, assumed to be in the BookNLP directory.
		return os.path.join(booknlp_dirpath, 'tokens')

	def get_corenlp_fpath(self, sid):
		"""
		Returns the filepath to the CoreNLP .xml for the given story.

		@param sid - Story Id of story
		@return Filepath to CoreNLP .xml
		"""

		return os.path.join(self.corenlp_dirpath, sid + '.xml')

	def get_text_fpath(self, sid):
		"""
		Returns the filepath to the text for the given story.

		@param sid - Story Id of story
		@return Filepath to text (None if story doesn't belong to sub-corpus)
		"""

		fname = sid + '.txt'

		for dirpath in self.text_dirpaths:
			path = os.path.join(dirpath, fname)
			if os.path.exists(path):
				return path

	def get_text_paths(self):
		"""
		Returns a generator over all filepaths to text files belonging to the
		sub-corpus.

		@return Generator of filepaths
		"""

		for dirpath in self.text_dirpaths:
			for fname in os.listdir(dirpath):
				if fname.endswith('.txt'):
					yield os.path.join(dirpath, fname)

	def belongs(self, sid):
		"""
		Checks if the given story Id corresponds to a story in the sub-corpus.

		@param - Story Id of story.
		@return True if the story belongs to the sub-corpus, False otherwise
			(Checks if story text exists in sub-corpus).
		"""

		return (self.get_text_fpath(sid) is not None)


class BothTextsMinusShakesCorpusManager(SubCorpusManager):
	"""
	Manages the base files (text, CoreNLP .xml, and BookNLP .html) for the
	BOTH_TEXTS_MINUS_SHAKES corpus.
	"""

	# Inititalizes the manager with the given root, BookNLP, CoreNLP, and text
	# directory paths. If not specified, then the paths are initialized to
	# defaults.
	def __init__(self, dirpath=None, booknlp_dirpath=None, corenlp_dirpath=None,
		text_dirpaths=None):
		
		if dirpath is None:
			dirpath = os.path.join(DATA_DIRPATH, 'BOTH_TEXTS_MINUS_SHAKES')

		super(BothTextsMinusShakesCorpusManager, self).__init__(dirpath=dirpath,
			booknlp_dirpath=booknlp_dirpath, corenlp_dirpath=corenlp_dirpath,
			text_dirpaths=text_dirpaths)

	def get_dates(self):
		"""
		Returns the publication dates for all stories in the sub-corpus.

		@return Map from story Id to publication date (as an integer)
		"""

		dates = {}
		for path in self.get_text_paths():
			fname = os.path.basename(path)
			try:
				dates[fname[:-4]] = int(fname[:4])
			except ValueError:
				continue

		return dates


class ContemporaryCorpusManager(SubCorpusManager):
	"""
	Manages the base files (text, CoreNLP .xml, and BookNLP .html) for the
	Contemporary corpus.
	"""

	# Sub-corpus is divided into the following sections.
	SECTIONS = ['bestsellers', 'contemporary-ny-times', 'mystery',
		'prizewinners', 'romance', 'scifi', 'young-adult-amazon',
		'young-adult-goodreads']

	# Inititalizes the manager with the given root, BookNLP, CoreNLP, and text
	# directory paths. If not specified, then the paths are initialized to
	# defaults.
	def __init__(self, dirpath=None, booknlp_dirpath=None, corenlp_dirpath=None,
		text_dirpaths=None):
		
		if dirpath is None:
			dirpath = os.path.join(DATA_DIRPATH, 'contemporary')

		if text_dirpaths is None:
			text_dirpaths = [os.path.join(os.path.join(os.path.join(dirpath,
									sec), 'texts'), 'orig')
								for sec in self.SECTIONS]

		super(ContemporaryCorpusManager, self).__init__(dirpath=dirpath,
			booknlp_dirpath=booknlp_dirpath, corenlp_dirpath=corenlp_dirpath,
			text_dirpaths=text_dirpaths)

	def get_dates(self):
		"""
		Returns the publication dates for all stories in the sub-corpus.

		@return Map from story Id to publication date (as an integer)
		"""

		dates = {}
		for path in self.get_text_paths():
			fname = os.path.basename(path)
			dates[fname[:-4]] = int(fname[:4])

		return dates

	def get_genre(self, sid, pretty=False):
		"""
		Returns the genre for the given story.

		@param sid - Story Id of story
		@param pretty - If True, then genre is returned in a more print friendly
			format (Default is False)
		@return Genre (as a string)
		"""

		# Checks the text filepath for particular folders to determine the
		# genre.
		text_path = self.get_text_fpath(sid)

		if 'contemporary-ny-times' in text_path:
			if pretty:
				return 'NY-Times'

			return 'ny-times'

		if 'young-adult' in text_path:
			if pretty:
				return 'Young Adult'

			return 'young-adult'

		for sec in self.SECTIONS:
			if sec in text_path:
				if pretty:
					# Capitalize.
					return sec[0].upper() + sec[1:]

				return sec


class MFACorpusManager(SubCorpusManager):
	"""
	Manages the base files (text, CoreNLP .xml, and BookNLP .html) for the
	MFA corpus.
	"""

	# Inititalizes the manager with the given root, BookNLP, CoreNLP, and text
	# directory paths. If not specified, then the paths are initialized to
	# defaults.
	def __init__(self, dirpath=None, booknlp_dirpath=None, corenlp_dirpath=None,
		text_dirpaths=None):
		
		if dirpath is None:
			dirpath = os.path.join(DATA_DIRPATH, 'mfa')

		super(MFACorpusManager, self).__init__(dirpath=dirpath,
			booknlp_dirpath=booknlp_dirpath, corenlp_dirpath=corenlp_dirpath,
			text_dirpaths=text_dirpaths)

	def get_dates(self):
		"""
		Returns the publication dates for all stories in the sub-corpus.

		@return Map from story Id to publication date (as an integer)
		"""

		dates = {}
		for path in self.get_text_paths():
			fname = os.path.basename(path)
			dates[fname[:-4]] = int(fname[:4])

		return dates


class Nonfiction19CCorpusManager(SubCorpusManager):
	"""
	Manages the base files (text, CoreNLP .xml, and BookNLP .html) for the
	19C non-fiction (English) corpus.
	"""

	# Inititalizes the manager with the given root, BookNLP, CoreNLP, and text
	# directory paths. If not specified, then the paths are initialized to
	# defaults.
	def __init__(self, dirpath=None, booknlp_dirpath=None, corenlp_dirpath=None,
		text_dirpaths=None):
		
		if dirpath is None:
			dirpath = os.path.join(DATA_DIRPATH, 'nonnovel-english-19C-history')

		super(Nonfiction19CCorpusManager, self).__init__(dirpath=dirpath,
			booknlp_dirpath=booknlp_dirpath, corenlp_dirpath=corenlp_dirpath,
			text_dirpaths=text_dirpaths)

	def get_dates(self):
		"""
		Returns the publication dates for all stories in the sub-corpus.

		@return Map from story Id to publication date (as an integer)
		"""

		dates = {}
		for path in self.get_text_paths():
			fname = os.path.basename(path)
			dates[fname[:-4]] = int(fname[:4])

		return dates


class Nonfiction21CCorpusManager(SubCorpusManager):
	"""
	Manages the base files (text, CoreNLP .xml, and BookNLP .html) for the
	21C non-fiction (English) corpus.
	"""

	# Inititalizes the manager with the given root, BookNLP, CoreNLP, and text
	# directory paths. If not specified, then the paths are initialized to
	# defaults.
	def __init__(self, dirpath=None, booknlp_dirpath=None, corenlp_dirpath=None,
		text_dirpaths=None):
		
		if dirpath is None:
			dirpath = os.path.join(DATA_DIRPATH,
				'nonnovel-english-contemporary-mixed')

		super(Nonfiction21CCorpusManager, self).__init__(dirpath=dirpath,
			booknlp_dirpath=booknlp_dirpath, corenlp_dirpath=corenlp_dirpath,
			text_dirpaths=text_dirpaths)

	def get_dates(self):
		"""
		Returns the publication dates for all stories in the sub-corpus.

		@return Map from story Id to publication date (as an integer)
		"""

		dates = {}
		for path in self.get_text_paths():
			fname = os.path.basename(path)
			dates[fname[:-4]] = int(fname[:4])

		return dates


class NYTimesNoMFACorpusManager(SubCorpusManager):
	"""
	Manages the base files (text, CoreNLP .xml, and BookNLP .html) for the
	NY-Times (No MFA) corpus.
	"""

	# Inititalizes the manager with the given root, BookNLP, CoreNLP, and text
	# directory paths. If not specified, then the paths are initialized to
	# defaults.
	def __init__(self, dirpath=None, booknlp_dirpath=None, corenlp_dirpath=None,
		text_dirpaths=None):
		
		if dirpath is None:
			dirpath = os.path.join(DATA_DIRPATH, 'nytimes-no-mfa')

		super(NYTimesNoMFACorpusManager, self).__init__(dirpath=dirpath,
			booknlp_dirpath=booknlp_dirpath, corenlp_dirpath=corenlp_dirpath,
			text_dirpaths=text_dirpaths)

	def get_dates(self):
		"""
		Returns the publication dates for all stories in the sub-corpus.

		@return Map from story Id to publication date (as an integer)
		"""

		dates = {}
		for path in self.get_text_paths():
			fname = os.path.basename(path)
			dates[fname[:-4]] = int(fname[:4])

		return dates


class PeriodCorpusManager(SubCorpusManager):
	"""
	Manages the base files (text, CoreNLP .xml, and BookNLP .html) for the
	Period Novels corpus.
	"""

	# Sub-corpus is divided into the following sections.
	SECTIONS = ['c18', 'rom', 'vic']

	# Inititalizes the manager with the given root, BookNLP, CoreNLP, and text
	# directory paths. If not specified, then the paths are initialized to
	# defaults.
	def __init__(self, dirpath=None, booknlp_dirpath=None, corenlp_dirpath=None,
		text_dirpaths=None):
		
		if dirpath is None:
			dirpath = os.path.join(DATA_DIRPATH, 'period-novels')

		if text_dirpaths is None:
			text_dirpaths = [os.path.join(os.path.join(os.path.join(dirpath,
									sec), 'texts'), 'orig')
								for sec in self.SECTIONS]

		super(PeriodCorpusManager, self).__init__(dirpath=dirpath,
			booknlp_dirpath=booknlp_dirpath, corenlp_dirpath=corenlp_dirpath,
			text_dirpaths=text_dirpaths)

	def get_dates(self):
		"""
		Returns the publication dates for all stories in the sub-corpus.

		@return Map from story Id to publication date (as an integer)
		"""

		dates = {}
		for path in self.get_text_paths():
			fname = os.path.basename(path)

			if fname.startswith('Chadwyck'):
				dates[fname[:-4]] = int(fname[9:13])
			else:
				dates[fname[:-4]] = int(fname[:4])

		return dates

	def get_period(self, sid, pretty=False):
		"""
		Returns the period ('rom', 'vic', or 'c18') for the given story.

		@param sid - Story Id of story
		@return Period (as a string)
		"""

		# Checks the text filepath for particular folders to determine the
		# period.
		text_path = self.get_text_fpath(sid)

		for sec in self.SECTIONS:
			if sec in text_path.split(os.sep):
				return sec


class PiperCorpusManager(SubCorpusManager):
	"""
	Manages the base files (text, CoreNLP .xml, and BookNLP .html) for the
	Piper corpus.

	The files corresponding to a story are traced using the story's id, a
	positive integer string 8 characters long (Includes leading 0's if
	necessary).
	"""

	# Inititalizes the manager with the given root, BookNLP, CoreNLP, and text
	# directory paths. If not specified, then the paths are initialized to
	# defaults.
	def __init__(self, dirpath=None, booknlp_dirpath=None, corenlp_dirpath=None,
		text_dirpaths=None):
		
		if dirpath is None:
			dirpath = os.path.join(DATA_DIRPATH, 'piper')

		# Path to info .csv file.
		self.info_path = os.path.join(dirpath, 'novels-info.csv')

		super(PiperCorpusManager, self).__init__(dirpath=dirpath,
			booknlp_dirpath=booknlp_dirpath, corenlp_dirpath=corenlp_dirpath,
			text_dirpaths=text_dirpaths)

	def get_ids(self, origin):
		"""
		Returns a list of sub-corpus story Id's.

		@param origin - If origin is 'all', 'gen', or 'novels', then all the
			Id's, the Id's corresponding to stories for which the CoreNLP .xml
			and BookNLP files have been generated, or only the novel Id's (if
			applicable) are returned, respectively
		@return List of story Id's in sub-corpus, in alphabetical order
		"""

		if origin == 'all':
			raise NotImplementedError
		elif origin == 'gen':
			bids, cids = [], []

			for parent, subdirnames, fnames in os.walk(self.booknlp_dirpath):
				for fname in fnames:
					if fname.endswith('.html'):
						bids.append(os.path.basename(parent))

			for fname in os.listdir(self.corenlp_dirpath):
				if fname.endswith('.xml'):
					cids.append(fname.split('.')[0])

			return sorted(set(bids) & set(cids), key=lambda i: int(i))
		elif origin == 'novels':
			raise NotImplementedError
		else:
			raise ValueError("'origin' argument must be 'all', 'gen', or "
				"'novels'.")

	def get_dates(self):
		"""
		Returns the publication dates for all stories in the sub-corpus.

		@return Map from story Id to publication date (as an integer)
		"""

		# Converts a raw story Id in the info .csv to the proper Id.
		def to_sid(raw_id):
			return '0' * (8 - len(raw_id)) + raw_id

		with open(self.info_path, 'rb') as f:
			reader = csv.reader(f, delimiter=',', quotechar='"')

			next(reader)

			return {to_sid(row[0]): int(row[-5]) for row in reader}

	def get_wcs(self):
		"""
		Returns the word counts for all stories in the sub-corpus.

		@return Map from story Id to word count
		"""

		# Converts a raw story Id in the info .csv to the proper Id.
		def to_sid(raw_id):
			return '0' * (8 - len(raw_id)) + raw_id

		with open(self.info_path, 'rb') as f:
			reader = csv.reader(f, delimiter=',', quotechar='"')

			next(reader)

			return {to_sid(row[0]): int(row[-1]) for row in reader}


class StanfordCorpusManager(SubCorpusManager):
	"""
	Manages the base files (text, CoreNLP .xml, and BookNLP .html) for the
	Stanford corpus.
	"""

	# Inititalizes the manager with the given root, BookNLP, CoreNLP, and text
	# directory paths. If not specified, then the paths are initialized to
	# defaults.
	def __init__(self, dirpath=None, booknlp_dirpath=None, corenlp_dirpath=None,
		text_dirpaths=None):
		
		if dirpath is None:
			dirpath = os.path.join(DATA_DIRPATH, '19C-stanford')

		super(StanfordCorpusManager, self).__init__(dirpath=dirpath,
			booknlp_dirpath=booknlp_dirpath, corenlp_dirpath=corenlp_dirpath,
			text_dirpaths=text_dirpaths)

	def get_dates(self):
		"""
		Returns the publication dates for all stories in the sub-corpus.

		@return Map from story Id to publication date (as an integer)
		"""

		dates = {}
		for path in self.get_text_paths():
			fname = os.path.basename(path)
			sid = fname[:-4]

			if sid == "InternetArchive_British_n.d_Braddon_Sonsoffire" or \
				sid == "InternetArchive_British_n.d_Egan_Theflowerof" or \
				sid == "InternetArchive_British_n.d_Lytton_TheParisians" or \
				sid == "InternetArchive_British_n.d_Sharowood_T_S_Foraking" or \
				sid == "InternetArchive_British_Between_1863_and_1878_Ainsworth_Thegoldsmithwife" or \
				sid == "InternetArchive_British_l865_Ouida_1839_1908_Strathmorea":
				continue
			elif sid == "Other_British_ca._1841_Ellis_Familysecretsor":
				date = "1841"
			elif sid == "Stanford_British_MDCCCXXXIV_[1834_Martineau_Illustrationsofpolitical":
				date = "1834"
			elif sid == "Stanford_British_c1898_Sand_Maupratby":
				date = "1898"
			elif sid == "InternetArchive_British_c1893_Blackmore_LornaDoone":
				date = "1893"
			elif sid == "InternetArchive_British_1816-1820_Burney_Talesoffancy":
				date = "1816"
			else:
				date = fname.split('_')[2]

			if date:
				dates[sid] = int(date)

		return dates


class WilkensCorpusManager(SubCorpusManager):
	"""
	Manages the base files (text, CoreNLP .xml, and BookNLP .html) for the
	Wilkens corpus.
	"""

	# Inititalizes the manager with the given root, BookNLP, CoreNLP, and text
	# directory paths. If not specified, then the paths are initialized to
	# defaults.
	def __init__(self, dirpath=None, booknlp_dirpath=None, corenlp_dirpath=None,
		text_dirpaths=None):
		
		if dirpath is None:
			dirpath = os.path.join(DATA_DIRPATH, 'wilkens')

		# Path to info .csv file.
		self.info_path = os.path.join(dirpath, 'info.csv')

		super(WilkensCorpusManager, self).__init__(dirpath=dirpath,
			booknlp_dirpath=booknlp_dirpath, corenlp_dirpath=corenlp_dirpath,
			text_dirpaths=text_dirpaths)

	def get_dates(self):
		"""
		Returns the publication dates for all stories in the sub-corpus.

		@return Map from story Id to publication date (as an integer)
		"""

		with open(self.info_path, 'rb') as f:
			reader = csv.reader(f, delimiter=',', quotechar='"')

			next(reader)

			return {row[0]: int(row[9]) for row in reader}

	def get_wcs(self):
		"""
		Returns the word counts for all stories in the sub-corpus.

		@return Map from story Id to word count
		"""

		with open(self.info_path, 'rb') as f:
			reader = csv.reader(f, delimiter=',', quotechar='"')

			next(reader)

			return {row[0]: int(row[-1]) for row in reader}


class CorpusManager(object):
	"""
	Manages the data files (text, CoreNLP .xml, and BookNLP .html) for the
	entire corpus (including all sub-corpora).
	"""

	# Inititalizes the manager with the given root and particular
	# story/collection directory paths. If not specified, then the paths are
	# initialized to defaults.
	def __init__(self, dirpath=None, atotc_dirpath=None, pp_dirpath=None,
		pnp_dirpath=None, ttl_dirpath=None, tt_dirpath=None,
		both_texts_minus_shakes_dirpath=None, contemporary_dirpath=None,
		mfa_dirpath=None, nonfict_19C_dirpath=None, nonfict_21C_dirpath=None,
		nytimes_no_mfa_dirpath=None, period_dirpath=None, piper_dirpath=None,
		stanford_dirpath=None, wilkens_dirpath=None):

		self.dirpath = DATA_DIRPATH if dirpath is None else dirpath
		atotc_dirpath = (os.path.join(self.dirpath, 'a-tale-of-two-cities')
			if atotc_dirpath is None else atotc_dirpath)
		pp_dirpath = (os.path.join(self.dirpath, 'peregrine-pickle')
			if pp_dirpath is None else pp_dirpath)
		pnp_dirpath = (os.path.join(self.dirpath, 'pride-and-prejudice')
			if pnp_dirpath is None else pnp_dirpath)
		ttl_dirpath = (os.path.join(self.dirpath, 'to-the-lighthouse')
			if ttl_dirpath is None else ttl_dirpath)
		both_texts_minus_shakes_dirpath = (os.path.join(self.dirpath,
			'BOTH_TEXTS_MINUS_SHAKES')
			if both_texts_minus_shakes_dirpath is None else
			both_texts_minus_shakes_dirpath)
		contemporary_dirpath = (os.path.join(self.dirpath, 'contemporary')
			if contemporary_dirpath is None else contemporary_dirpath)
		mfa_dirpath = (os.path.join(self.dirpath, 'mfa')
			if mfa_dirpath is None else mfa_dirpath)
		nonfict_19C_dirpath = (os.path.join(self.dirpath,
			'nonnovel-english-19C-history')
			if nonfict_19C_dirpath is None else nonfict_19C_dirpath)
		nonfict_21C_dirpath = (os.path.join(self.dirpath,
			'nonnovel-english-contemporary-mixed')
			if nonfict_21C_dirpath is None else nonfict_21C_dirpath)
		nytimes_no_mfa_dirpath = (os.path.join(self.dirpath, 'nytimes-no-mfa')
			if nytimes_no_mfa_dirpath is None else nytimes_no_mfa_dirpath)
		period_dirpath = (os.path.join(self.dirpath, 'period-novels')
			if period_dirpath is None else period_dirpath)
		piper_dirpath = (os.path.join(self.dirpath, 'piper')
			if piper_dirpath is None else piper_dirpath)
		stanford_dirpath = (os.path.join(self.dirpath, '19C-stanford')
			if stanford_dirpath is None else stanford_dirpath)
		wilkens_dirpath = (os.path.join(self.dirpath, 'wilkens')
			if wilkens_dirpath is None else wilkens_dirpath)
		
		self.atotcm = ATaleOfTwoCitiesStoryManager(dirpath=atotc_dirpath)
		self.ppm = PeregrinePickleManager(dirpath=pp_dirpath)
		self.pnpm = PrideAndPrejudiceManager(dirpath=pnp_dirpath)
		self.ttlm = ToTheLighthouseStoryManager(dirpath=ttl_dirpath)
		self.ttm = TristramShandyManager(dirpath=tt_dirpath)
		self.btmsm = BothTextsMinusShakesCorpusManager(
			dirpath=both_texts_minus_shakes_dirpath)
		self.contcm = ContemporaryCorpusManager(dirpath=contemporary_dirpath)
		self.mfacm = MFACorpusManager(dirpath=mfa_dirpath)
		self.nf19Cm = Nonfiction19CCorpusManager(dirpath=nonfict_19C_dirpath)
		self.nf21Cm = Nonfiction21CCorpusManager(dirpath=nonfict_21C_dirpath)
		self.nycm = NYTimesNoMFACorpusManager(dirpath=nytimes_no_mfa_dirpath)
		self.percm = PeriodCorpusManager(dirpath=period_dirpath)
		self.pipcm = PiperCorpusManager(dirpath=piper_dirpath)
		self.stancm = StanfordCorpusManager(dirpath=stanford_dirpath)
		self.wilkcm = WilkensCorpusManager(dirpath=wilkens_dirpath)

	def get_ids(self, origin):
		"""
		Returns a list of corpus story id's. If origin is 'all', 'gen', or
		'novels', then all the id's, the id's corresponding to stories for which
		the CoreNLP .xml and BookNLP files have been generated, or only the
		novel id's are returned, respectively.
		"""

		if origin == 'all':
			raise NotImplementedError
		elif origin == 'gen':
			ids = self.btmsm.get_ids('gen')
			ids += self.contcm.get_ids('gen')
			ids += self.mfacm.get_ids('gen')
			ids += self.nf19Cm.get_ids('gen')
			ids += self.nf21Cm.get_ids('gen')
			ids += self.nycm.get_ids('gen')
			ids += self.pipcm.get_ids('gen')
			ids += self.percm.get_ids('gen')
			ids += self.stancm.get_ids('gen')
			ids += self.wilkcm.get_ids('gen')
			
			if self.ttm.has_booknlp() and self.ttm.has_corenlp():
				ids = [self.ttm.get_id()] + ids

			if self.ttlm.has_booknlp() and self.ttlm.has_corenlp():
				ids = [self.ttlm.get_id()] + ids

			if self.pnpm.has_booknlp() and self.pnpm.has_corenlp():
				ids = [self.pnpm.get_id()] + ids

			if self.ppm.has_booknlp() and self.ppm.has_corenlp():
				ids = [self.ppm.get_id()] + ids

			if self.atotcm.has_booknlp() and self.atotcm.has_corenlp():
				ids = [self.atotcm.get_id()] + ids

			return ids
		elif origin == 'novels':
			raise NotImplementedError
		else:
			raise ValueError("'origin' argument must be 'all', 'gen', or "
				"'novels'.")

	def get_dates(self):
		"""
		Returns the publication dates for all stories in the corpus.

		@return Map from story Id to publication date (as an integer)
		"""

		dates = self.btmsm.get_dates()
		dates.update(self.contcm.get_dates())
		dates.update(self.mfacm.get_dates())
		dates.update(self.nf19Cm.get_dates())
		dates.update(self.nf21Cm.get_dates())
		dates.update(self.nycm.get_dates())
		dates.update(self.pipcm.get_dates())
		dates.update(self.percm.get_dates())
		dates.update(self.stancm.get_dates())
		dates.update(self.wilkcm.get_dates())

		dates[self.atotcm.get_id()] = self.atotcm.get_date()
		dates[self.ppm.get_id()] = self.ppm.get_date()
		dates[self.pnpm.get_id()] = self.pnpm.get_date()
		dates[self.ttlm.get_id()] = self.ttlm.get_date()
		dates[self.ttm.get_id()] = self.ttm.get_date()

		return dates

	def get_wcs(self):
		"""
		Returns the word counts for all stories in the corpus.

		@return Map from story Id to word count
		"""

		wcs = self.btmsm.get_wcs()
		wcs.update(self.contcm.get_wcs())
		wcs.update(self.mfacm.get_wcs())
		wcs.update(self.nf19Cm.get_wcs())
		wcs.update(self.nf21Cm.get_wcs())
		wcs.update(self.nycm.get_wcs())
		wcs.update(self.pipcm.get_wcs())
		wcs.update(self.percm.get_wcs())
		wcs.update(self.stancm.get_wcs())
		wcs.update(self.wilkcm.get_wcs())

		wcs[self.atotcm.get_id()] = self.atotcm.get_wc()
		wcs[self.ppm.get_id()] = self.ppm.get_wc()
		wcs[self.pnpm.get_id()] = self.pnpm.get_wc()
		wcs[self.ttlm.get_id()] = self.ttlm.get_wc()
		wcs[self.ttm.get_id()] = self.ttm.get_wc()

		return wcs

	def get_sub(self, sid):
		"""
		Returns the sub-corpus name (if any) for the given story.

		@param sid - Story Id of story
		@return Sub-corpus name as a string
		"""

		# Single stories don't have a sub-corpus.
		if (sid == 'a-tale-of-two-cities' or sid == 'peregrine-pickle' or \
			sid == 'pride-and-prejudice' or sid == 'to-the-lighthouse' or \
			sid == 'tristram-shandy'):
			return None
		elif self.btmsm.belongs(sid):
			return 'BOTH_TEXTS_MINUS_SHAKES'
		elif self.contcm.belongs(sid):
			return 'contemporary'
		elif self.mfacm.belongs(sid):
			return 'mfa'
		elif self.nf19Cm.belongs(sid):
			return 'nonfiction-19C'
		elif self.nf21Cm.belongs(sid):
			return 'nonfiction-21C'
		elif self.nycm.belongs(sid):
			return 'ny-times'
		elif self.pipcm.belongs(sid):
			return 'klab'
		elif self.percm.belongs(sid):
			return 'period-novels'
		elif self.stancm.belongs(sid):
			return 'stanford'
		elif self.wilkcm.belongs(sid):
			return 'wilkens'
		else:
			raise ValueError("Unrecognized story id, " + sid + ".")

	def get_genre(self, sid, pretty=False):
		"""
		Returns the genre for the given story.

		@param sid - Story Id of story
		@param pretty - If True, then genre is returned in a more print friendly
			format (Default is False)
		@return Genre (as a string if it exists, otherwise None)
		"""

		# Single stories don't have a genre.
		if (sid == 'a-tale-of-two-cities' or sid == 'peregrine-pickle' or \
			sid == 'pride-and-prejudice' or sid == 'to-the-lighthouse' or \
			sid == 'tristram-shandy'):
			return None
		# The Contemporary sub-corpus is organized by genre
		elif self.contcm.belongs(sid):
			return self.contcm.get_genre(sid, pretty)
		# The MFA sub-corpus is its own genre.
		elif self.mfacm.belongs(sid):
			if pretty:
				return 'MFA'

			return 'mfa'
		# So is the NY-Times (No MFA) sub-corpus.
		elif self.nycm.belongs(sid):
			if pretty:
				return 'NY-Times'

			return 'ny-times'
		# These sub-corpora do not track genre.
		elif self.btmsm.belongs(sid) or self.nf19Cm.belongs(sid) or \
			self.nf21Cm.belongs(sid) or self.pipcm.belongs(sid) or \
			self.percm.belongs(sid) or self.stancm.belongs(sid) or \
			self.wilkcm.belongs(sid):
			return None
		else:
			raise ValueError("Unrecognized story id, " + sid + ".")

	def belongs(self, sid):
		"""
		Checks whether the given story Id corresponds to a story in the corpus.
		"""

		return (sid == 'a-tale-of-two-cities' or sid == 'peregrine-pickle' or \
			sid == 'pride-and-prejudice' or sid == 'to-the-lighthouse' or \
			sid == 'tristram-shandy' or self.btmsm.belongs(sid) or \
			self.contcm.belongs(sid) or self.mfacm.belongs(sid) or \
			self.nf19Cm.belongs(sid) or self.nf21Cm.belongs(sid) or \
			self.nycm.belongs(sid) or self.pipcm.belongs(sid) or \
			self.percm.belongs(sid) or self.stancm.belongs(sid) or \
			self.wilkcm.belongs(sid))

	def get_dirpath(self, sid):
		"""
		Returns the path to the data directory for the given story.
		"""

		if sid == 'a-tale-of-two-cities':
			return self.atotcm.dirpath
		elif sid == 'peregrine-pickle':
			return self.ppm.dirpath
		elif sid == 'pride-and-prejudice':
			return self.pnpm.dirpath
		elif sid == 'to-the-lighthouse':
			return self.ttlm.dirpath
		elif sid == 'tristram-shandy':
			return self.ttm.dirpath
		elif self.btmsm.belongs(sid):
			return self.btmsm.dirpath
		elif self.contcm.belongs(sid):
			return self.contcm.dirpath
		elif self.mfacm.belongs(sid):
			return self.mfacm.dirpath
		elif self.nf19Cm.belongs(sid):
			return self.nf19Cm.dirpath
		elif self.nf21Cm.belongs(sid):
			return self.nf21Cm.dirpath
		elif self.nycm.belongs(sid):
			return self.nycm.dirpath
		elif self.pipcm.belongs(sid):
			return self.pipcm.dirpath
		elif self.percm.belongs(sid):
			return self.percm.dirpath
		elif self.stancm.belongs(sid):
			return self.stancm.dirpath
		elif self.wilkcm.belongs(sid):
			return self.wilkcm.dirpath
		else:
			raise ValueError("Unrecognized story id, " + sid + ".")

	def get_booknlp_fpath(self, sid):
		"""
		Returns the filepath to the BookNLP .html for the story with id sid.
		"""

		if sid == 'a-tale-of-two-cities':
			return self.atotcm.booknlp_fpath
		elif sid == 'peregrine-pickle':
			return self.ppm.booknlp_fpath
		elif sid == 'pride-and-prejudice':
			return self.pnpm.booknlp_fpath
		elif sid == 'to-the-lighthouse':
			return self.ttlm.booknlp_fpath
		elif sid == 'tristram-shandy':
			return self.ttm.booknlp_fpath
		elif self.btmsm.belongs(sid):
			return self.btmsm.get_booknlp_fpath(sid)
		elif self.contcm.belongs(sid):
			return self.contcm.get_booknlp_fpath(sid)
		elif self.mfacm.belongs(sid):
			return self.mfacm.get_booknlp_fpath(sid)
		elif self.nf19Cm.belongs(sid):
			return self.nf19Cm.get_booknlp_fpath(sid)
		elif self.nf21Cm.belongs(sid):
			return self.nf21Cm.get_booknlp_fpath(sid)
		elif self.nycm.belongs(sid):
			return self.nycm.get_booknlp_fpath(sid)
		elif self.pipcm.belongs(sid):
			return self.pipcm.get_booknlp_fpath(sid)
		elif self.percm.belongs(sid):
			return self.percm.get_booknlp_fpath(sid)
		elif self.stancm.belongs(sid):
			return self.stancm.get_booknlp_fpath(sid)
		elif self.wilkcm.belongs(sid):
			return self.wilkcm.get_booknlp_fpath(sid)
		else:
			raise ValueError("Unrecognized story id, " + sid + ".")

	def get_booknlp_tokens(self, sid):
		"""
		Returns the filepath to the BookNLP .tokens for the story with id sid.
		"""

		if sid == 'a-tale-of-two-cities':
			return self.atotcm.booknlp_tokens_fpath
		elif sid == 'peregrine-pickle':
			return self.ppm.booknlp_tokens_fpath
		elif sid == 'pride-and-prejudice':
			return self.pnpm.booknlp_tokens_fpath
		elif sid == 'to-the-lighthouse':
			return self.ttlm.booknlp_tokens_fpath
		elif sid == 'tristram-shandy':
			return self.ttm.booknlp_tokens_fpath
		elif self.btmsm.belongs(sid):
			return self.btmsm.get_booknlp_tokens(sid)
		elif self.contcm.belongs(sid):
			return self.contcm.get_booknlp_tokens(sid)
		elif self.mfacm.belongs(sid):
			return self.mfacm.get_booknlp_tokens(sid)
		elif self.nf19Cm.belongs(sid):
			return self.nf19Cm.get_booknlp_tokens(sid)
		elif self.nf21Cm.belongs(sid):
			return self.nf21Cm.get_booknlp_tokens(sid)
		elif self.nycm.belongs(sid):
			return self.nycm.get_booknlp_tokens(sid)
		elif self.pipcm.belongs(sid):
			return self.pipcm.get_booknlp_tokens(sid)
		elif self.percm.belongs(sid):
			return self.percm.get_booknlp_tokens(sid)
		elif self.stancm.belongs(sid):
			return self.stancm.get_booknlp_tokens(sid)
		elif self.wilkcm.belongs(sid):
			return self.wilkcm.get_booknlp_tokens(sid)
		else:
			raise ValueError("Unrecognized story id, " + sid + ".")

	def get_booknlp_dirpath(self, sid):
		"""
		Returns the path to the BookNLP directory for the story with id sid.
		"""

		return os.path.split(self.get_booknlp_fpath(sid))[0]

	def get_corenlp_fpath(self, sid):
		"""
		Returns the filepath to the CoreNLP .xml for the story with id sid.
		"""

		if sid == 'a-tale-of-two-cities':
			return self.atotcm.corenlp_fpath
		elif sid == 'peregrine-pickle':
			return self.ppm.corenlp_fpath
		elif sid == 'pride-and-prejudice':
			return self.pnpm.corenlp_fpath
		elif sid == 'to-the-lighthouse':
			return self.ttlm.corenlp_fpath
		elif sid == 'tristram-shandy':
			return self.ttm.corenlp_fpath
		elif self.btmsm.belongs(sid):
			return self.btmsm.get_corenlp_fpath(sid)
		elif self.contcm.belongs(sid):
			return self.contcm.get_corenlp_fpath(sid)
		elif self.mfacm.belongs(sid):
			return self.mfacm.get_corenlp_fpath(sid)
		elif self.nf19Cm.belongs(sid):
			return self.nf19Cm.get_corenlp_fpath(sid)
		elif self.nf21Cm.belongs(sid):
			return self.nf21Cm.get_corenlp_fpath(sid)
		elif self.nycm.belongs(sid):
			return self.nycm.get_corenlp_fpath(sid)
		elif self.pipcm.belongs(sid):
			return self.pipcm.get_corenlp_fpath(sid)
		elif self.percm.belongs(sid):
			return self.percm.get_corenlp_fpath(sid)
		elif self.stancm.belongs(sid):
			return self.stancm.get_corenlp_fpath(sid)
		elif self.wilkcm.belongs(sid):
			return self.wilkcm.get_corenlp_fpath(sid)
		else:
			raise ValueError("Unrecognized story id, " + sid + ".")

	def get_text_path(self, sid):
		"""
		Returns the filepath to the text for the given story.

		@param sid - Story Id of story
		@return Filepath to corresponding text file
		"""

		if sid == 'a-tale-of-two-cities':
			return self.atotcm.text_fpath
		elif sid == 'peregrine-pickle':
			return self.ppm.text_fpath
		elif sid == 'pride-and-prejudice':
			return self.pnpm.text_fpath
		elif sid == 'to-the-lighthouse':
			return self.ttlm.text_fpath
		elif sid == 'tristram-shandy':
			return self.ttm.text_fpath
		elif self.btmsm.belongs(sid):
			return self.btmsm.get_text_fpath(sid)
		elif self.contcm.belongs(sid):
			return self.contcm.get_text_fpath(sid)
		elif self.mfacm.belongs(sid):
			return self.mfacm.get_text_fpath(sid)
		elif self.nf19Cm.belongs(sid):
			return self.nf19Cm.get_text_fpath(sid)
		elif self.nf21Cm.belongs(sid):
			return self.nf21Cm.get_text_fpath(sid)
		elif self.nycm.belongs(sid):
			return self.nycm.get_text_fpath(sid)
		elif self.pipcm.belongs(sid):
			return self.pipcm.get_text_fpath(sid)
		elif self.percm.belongs(sid):
			return self.percm.get_text_fpath(sid)
		elif self.stancm.belongs(sid):
			return self.stancm.get_text_fpath(sid)
		elif self.wilkcm.belongs(sid):
			return self.wilkcm.get_text_fpath(sid)
		else:
			raise ValueError("Unrecognized story id, " + sid + ".")
