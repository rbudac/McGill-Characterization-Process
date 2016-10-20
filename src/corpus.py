"""
Manages corpora.

@author: Hardik
"""

import csv
import os
import sys


def GetDataPath():
	file = open('../datapath.txt', 'r')
	return file.readline().strip('\n')

# Data directory path.
DATA_DIRPATH = GetDataPath() 


class StoryManager(object):
	"""
	Manages the data files (text, CoreNLP .xml, and BookNLP .html) for a given
	story.
	"""

	# Inititalizes the manager with the given root directory, BookNLP .html,
	# CoreNLP .xml, and text paths. If not specified, then the paths are
	# initialized to defaults (except for the root directory path).
	def __init__(self, dirpath, id, date, wc=None, booknlp_fpath=None, corenlp_fpath=None,
		text_fpath=None):
		self.dirpath = dirpath
		self.id = id
		self.date = date
		text_filename = ''.join([id, '.txt'])
		self.wc = wc
		self.booknlp_fpath = (os.path.join(os.path.join(self.dirpath, 'booknlp'),
			'book.id.html') if booknlp_fpath is None else booknlp_fpath)
		self.corenlp_fpath = (os.path.join(self.dirpath, 'corenlp.xml')
			if corenlp_fpath is None else corenlp_fpath)
		self.text_fpath = (os.path.join(os.path.join(self.dirpath, 'texts'), 
			text_filename) if text_fpath is None else text_fpath)

		booknlp_dirpath = os.path.dirname(self.booknlp_fpath)
		# Path to BookNLP tokens file, assumed to be in the BookNLP directory.
		self.booknlp_tokens_fpath = os.path.join(booknlp_dirpath,
			'book.id.tokens')

	def get_id(self):
		"""
		Returns the story id.
		"""

		return self.id
		#raise NotImplementedError

	def get_date(self):
		"""
		Returns the story publication date.

		@return Story publication date (as an integer)
		"""

		return self.date
		#raise NotImplementedError

	def get_wc(self):
		"""
		Returns the story word count.

		@return Word count
		"""

		if self.wc is None:
			self.text_fpath 
			
			num_lines = 0
			num_words = 0
			num_chars = 0

			with open(self.text_fpath, 'r') as f:
				for line in f:
					words = line.split()
					num_lines += 1
					num_words += len(words)
					num_chars += len(line)

			self.wc = num_words
		return self.wc
		#raise NotImplementedError

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
	def __init__(self, dirpath=None, atotc_dirpath=None):

		self.dirpath = DATA_DIRPATH if dirpath is None else dirpath

		textdirs = os.listdir(self.dirpath) # returns list
		self.texts = []

		for file in textdirs:
			text_dir = os.path.join(self.dirpath, file)
			self.texts.append(StoryManager(dirpath=text_dir, id=file, date=0))

	def get_ids(self, origin):
		"""
		Returns a list of corpus story id's. If origin is 'all', 'gen', or
		'novels', then all the id's, the id's corresponding to stories for which
		the CoreNLP .xml and BookNLP files have been generated, or only the
		novel id's are returned, respectively.
		"""

		ids = []
		for text in self.texts:
			if origin == 'all':
				raise NotImplementedError
			elif origin == 'gen':
				if text.has_booknlp() and text.has_corenlp():
					ids = [text.get_id()] + ids
			elif origin == 'novels':
				raise NotImplementedError
			else:
				raise ValueError("'origin' argument must be 'all', 'gen', or "
					"'novels'.")
		return ids


	def get_dates(self):
		"""
		Returns the publication dates for all stories in the corpus.

		@return Map from story Id to publication date (as an integer)
		"""
		dates = {}
		for text in self.texts:
			dates[text.get_id()] = text.get_date()

		return dates

	def get_wcs(self):
		"""
		Returns the word counts for all stories in the corpus.

		@return Map from story Id to word count
		"""
		wcs = {}
		for text in self.texts:
			wcs[text.get_id()] = text.get_wc()

		return wcs

	def get_sub(self, sid):
		"""
		Returns the sub-corpus name (if any) for the given story.

		@param sid - Story Id of story
		@return Sub-corpus name as a string
		"""

		# HACK - removed sub-corpus functionality. -Rob
		return None
		# Single stories don't have a sub-corpus.
		"""
		if (sid == 'a-tale-of-two-cities' or sid == 'peregrine-pickle' or \
			sid == 'pride-and-prejudice' or sid == 'to-the-lighthouse' or \
			sid == 'tristram-shandy'):
			return None
		else:
			raise ValueError("Unrecognized story id, " + sid + ".")
		"""

	def get_genre(self, sid, pretty=False):
		"""
		Returns the genre for the given story.

		@param sid - Story Id of story
		@param pretty - If True, then genre is returned in a more print friendly
			format (Default is False)
		@return Genre (as a string if it exists, otherwise None)
		"""

		# HACK - removed sub-corpus functionality. -Rob
		return None
		# Single stories don't have a genre.
		"""
		if (sid == 'a-tale-of-two-cities' or sid == 'peregrine-pickle' or \
			sid == 'pride-and-prejudice' or sid == 'to-the-lighthouse' or \
			sid == 'tristram-shandy'):
			return None
		else:
			raise ValueError("Unrecognized story id, " + sid + ".")
		"""

	def belongs(self, sid):
		"""
		Checks whether the given story Id corresponds to a story in the corpus.
		"""

		for text in self.texts:
			if (sid == text.get_id()):
				return True
		return False

	def get_dirpath(self, sid):
		"""
		Returns the path to the data directory for the given story.
		"""

		for text in self.texts:
			if (sid == text.get_id()):
				return text.dirpath
		raise ValueError("Unrecognized story id, " + sid + ".")

	def get_booknlp_fpath(self, sid):
		"""
		Returns the filepath to the BookNLP .html for the story with id sid.
		"""

		for text in self.texts:
			if (sid == text.get_id()):
				return text.booknlp_fpath
		raise ValueError("Unrecognized story id, " + sid + ".")

	def get_booknlp_tokens(self, sid):
		"""
		Returns the filepath to the BookNLP .tokens for the story with id sid.
		"""

		for text in self.texts:
			if (sid == text.get_id()):
				return text.booknlp_tokens_fpath
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

		for text in self.texts:
			if (sid == text.get_id()):
				return text.corenlp_fpath
		raise ValueError("Unrecognized story id, " + sid + ".")

	def get_text_path(self, sid):
		"""
		Returns the filepath to the text for the given story.

		@param sid - Story Id of story
		@return Filepath to corresponding text file
		"""

		for text in self.texts:
			if (sid == text.get_id()):
				return text.text_fpath
		raise ValueError("Unrecognized story id, " + sid + ".")
