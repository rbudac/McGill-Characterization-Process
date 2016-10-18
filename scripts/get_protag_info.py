"""
Retrieves the protagonist (i.e. character with most mentions) name and gender
for each story, saving the results in a .tsv file.

@author: Hardik
"""

import argparse
import csv
import logging
import os
import sys
sys.path.insert(1, os.path.join(sys.path[0], os.path.join('..', 'src')))

from collections import Counter

from aliases import AliasesManager
from corpus import CorpusManager


# Configure logging
logging.basicConfig(format="%(levelname)s: [%(asctime)s] %(message)s",
	level=logging.INFO)


# Gendered pronouns.
MALE_PRONOUNS = set(['he', 'him', 'himself', 'his'])
FEMALE_PRONOUNS = set(['her', 'hers', 'herself', 'she'])


# Returns the name of the protagonist character.
def get_protag(aliases):
	cntr = Counter()

	for alias in aliases:
		cntr[alias['entity']['name']] += 1

	mc = cntr.most_common(1)
	if len(mc) == 0:
		return None

	return mc[0][0]


# Determines the gender of the given character according to the given list of
# aliases.
def det_gender(character_name, aliases):
	male_pron_cnt, female_pron_cnt = 0, 0

	for alias in aliases:
		if alias['entity']['name'] == character_name:
			span = alias['span'].lower()

			if span in MALE_PRONOUNS:
				male_pron_cnt += 1
			elif span in FEMALE_PRONOUNS:
				female_pron_cnt += 1

	if male_pron_cnt > female_pron_cnt:
		return 'MALE'
	elif female_pron_cnt > male_pron_cnt:
		return 'FEMALE'
	else:
		return 'UNKNOWN'

	
def main():
	parser_description = ("Retrieves the protagonist name and gender for each "
		"story, saving the results in a .tsv file.")
	parser = argparse.ArgumentParser(description=parser_description)

	parser.add_argument('out_path', help="Output path to .tsv file")

	args = parser.parse_args()

	aliases_manager = AliasesManager()
	corpus_manager = CorpusManager()
	
	logging.info("Getting story Id's and pub. dates...")
	# Get publication dates for all stories.
	dates = corpus_manager.get_dates()
	# Story Id's.
	sids = corpus_manager.get_ids(origin='gen')

	with open(args.out_path, 'wb') as f:
		writer = csv.writer(f, delimiter='\t', quotechar='"')

		# Write header.
		writer.writerow(['STORY ID', 'PUB. DATE', 'GENRE', 'PROTAG. NAME', 'PROTAG. GENDER'])
		
		for sid in sids:
			if not aliases_manager.saved(sid, tpe='character'):
				logging.info("Skipping %s..." % sid)
				continue
			
			logging.info("Reading %s..." % sid)

			genre = (None if sid.startswith('000') else
					corpus_manager.get_genre(sid, pretty=True))
			row = [sid, dates[sid] if sid in dates else 'DNE',
				genre if genre else 'DNE']

			aliases = aliases_manager.get_aliases(sid, tpe='character')
			
			protag_name = get_protag(aliases)

			if protag_name is None:
				row += [None, None]
			else:
				protag_gender = det_gender(protag_name, aliases)
				row += [protag_name.encode('utf-8'), protag_gender]

			writer.writerow(row)
		

if __name__ == '__main__':
	main()
