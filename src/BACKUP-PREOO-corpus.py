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
		atotc_dirpath = (os.path.join(self.dirpath, 'a-tale-of-two-cities')
			if atotc_dirpath is None else atotc_dirpath)
		
		self.atotcm = ATaleOfTwoCitiesStoryManager(dirpath=atotc_dirpath)

	def get_ids(self, origin):
		"""
		Returns a list of corpus story id's. If origin is 'all', 'gen', or
		'novels', then all the id's, the id's corresponding to stories for which
		the CoreNLP .xml and BookNLP files have been generated, or only the
		novel id's are returned, respectively.
		"""
		ids = []
		if origin == 'all':
			raise NotImplementedError
		elif origin == 'gen':
			if self.atotcm.has_booknlp() and self.atotcm.has_corenlp():
				ids = [self.atotcm.get_id()]
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
		dates = {}
		dates[self.atotcm.get_id()] = self.atotcm.get_date()

		return dates

	def get_wcs(self):
		"""
		Returns the word counts for all stories in the corpus.

		@return Map from story Id to word count
		"""

		wcs[self.atotcm.get_id()] = self.atotcm.get_wc()

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
		else:
			raise ValueError("Unrecognized story id, " + sid + ".")

	def belongs(self, sid):
		"""
		Checks whether the given story Id corresponds to a story in the corpus.
		"""

		return (sid == 'a-tale-of-two-cities')

	def get_dirpath(self, sid):
		"""
		Returns the path to the data directory for the given story.
		"""

		if sid == 'a-tale-of-two-cities':
			return self.atotcm.dirpath
		else:
			raise ValueError("Unrecognized story id, " + sid + ".")

	def get_booknlp_fpath(self, sid):
		"""
		Returns the filepath to the BookNLP .html for the story with id sid.
		"""

		if sid == 'a-tale-of-two-cities':
			return self.atotcm.booknlp_fpath
		else:
			raise ValueError("Unrecognized story id, " + sid + ".")

	def get_booknlp_tokens(self, sid):
		"""
		Returns the filepath to the BookNLP .tokens for the story with id sid.
		"""

		if sid == 'a-tale-of-two-cities':
			return self.atotcm.booknlp_tokens_fpath
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
		else:
			raise ValueError("Unrecognized story id, " + sid + ".")
