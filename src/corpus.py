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
#	raise NotImplementedError

# Data directory path.
DATA_DIRPATH = GetDataPath() 


#"/home/ubuntu/work/ra/noveltm/characterization/data"


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
