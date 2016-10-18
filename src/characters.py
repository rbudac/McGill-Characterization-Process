"""
Parses and manages characters for all stories.

@author: Hardik
"""

import json
import os
import re

from corpus import CorpusManager


class BookNLPCharacterParser(object):
	"""
	Parser for BookNLP .html files.
	"""

	def __init__(self):
		pass

	def parse(self, filepath, top=None):
		"""
		Parses the characters from the BookNLP .html formatted file located at
		the given filepath. If top is not None, then only the top characters,
		according to the # of occurrences in text, are returned.

		The output is a list of characters, where each character is represented
		as,

		{
			"entity": [First alias span],
			"count": [# occurrences of all character's aliases],
			"aliases": [List of aliases]
		}

		Each alias is also represented as a dictionary in the following format,

		{
			"alias": [Span],
			"count": [# occurrences]
		}
		"""

		with open(filepath, 'r') as f:
			content = f.read()
			# Starting index of the character content.
			start_index = content.find('</h1>') + 5
			# Ending index of the character content.
			end_index = content.rfind('<h1>')
			# Character content string.
			character_content = content[start_index:end_index]

			# List of characters, with each character is represented as a dictionary
			# with character name (The first one listed), character count, and a
			# list of aliases, with each alias represented as a dictionary with
			# alias span and count.
			characters = []

			i = 0
			# Character aliases are listed on separate lines.
			for l in character_content.split('<br />'):
				# Only retain the top characters.
				if l.strip() != "" and (top is None or i < top):
					character = {}

					# The character count is the number starting the line.
					character_count = re.search(r'^\d+', l)
					if character_count:
						count = int(character_count.group())
						if count == 0:
							continue
						else:
							character['count'] = count
					else:
						# Reached the text portion.
						if l.startswith("<h1>"):
							break
						else:
							Exception("Failed to parse character count in " +
								filepath + " on line: " + l)

					# Drop the starting character count.
					parsed_l = l[character_count.end():].strip()

					# The first name is taken as the sequence of characters after 
					# the character count leading up to the first '(' (without any
					# leading or trailing whitespace), i.e. the first alias span.
					first_name = re.search(r'^([^\(]+)\s+\(', parsed_l)
					if first_name:
						character['entity'] = first_name.group(1)
					else:
						raise Exception("Failed to parse first character name "
							"in " + filepath + " on line: " + l)

					alias_matches = list(re.finditer(r'([^(\(\))]+)\s+\((\d+)\)',
						parsed_l))
					if len(alias_matches) > 0:
						character['aliases'] = [{
													'alias': m.group(1).strip(),
													'count': int(m.group(2))
												}
												for m
												in alias_matches]
					else:
						raise Exception("Failed to parse aliases in " +
							filepath + " on line: " + l)

					characters.append(character)
					i += 1
				else:
					break

			return characters

	def save(self, characters, filepath):
		"""
		Outputs the given list of characters (As returned by parse) to a .json
		file specified by the given filepath.
		"""

		with open(filepath, 'w') as out:
			json.dump(characters, out, sort_keys=True, indent=4)


class CharactersManager(object):
	"""
	Manages the list of characters for each story in the corpus.
	"""

	def __init__(self):
		self.parser = BookNLPCharacterParser()
		self.cm = CorpusManager()

	def get_fpath(self, sid):
		"""
		Returns the filepath to the characters .json file for the given story.
		"""

		return os.path.join(self.cm.get_booknlp_dirpath(sid), 'characters.json')

	def saved(self, sid):
		"""
		Checks whether the characters .json for the given story has been
		generated.
		"""
		print self.get_fpath(sid)
		return os.path.exists(self.get_fpath(sid))

	def gen(self, sid):
		"""
		Generates the characters .json file for the given story (Overwrites it
		if it already exists).
		"""

		characters = self.parser.parse(self.cm.get_booknlp_fpath(sid))
		self.parser.save(characters, self.get_fpath(sid))

	def get_characters(self, sid):
		"""
		Retrieves the character dictionary from the .json file for the given
		story.
		"""

		with open(self.get_fpath(sid)) as f:
			return json.load(f)
