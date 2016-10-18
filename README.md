Requirements:
-------
- Python 2.x
- Java 1.8 or higher (required for coreNLP and bookNLP)
- LIWC (not free) is required for calculating the LIWC features.
- See python_packages.txt for an extensive list of required python libraries.
	Note that many of these libraries are required only for specific scripts.


Setup and running the scripts:
-------
First, change the path in the datapath.txt file, so that it points to the exact location of your data directory.
This directory will contain all of your texts, each in their own directory. (See the harry-potter excerpt,
which has been provided as an example.)

If you want to do your own texts, note that they will need to be run through coreNLP and bookNLP first.
Download here, and check the "booknlp-corenlp-prep" directory in the scripts directory, for some guidance
as to what command line parameters to include. Note, these are kind've messy at the moment. Apologies!

Once you have the output from coreNLP and bookNLP, put that output in the same directory structure as
harry-potter has, with the original text itself being in a "texts" directory.

With all the texts that you wish to analyze, in the data directory and properly organized, you can start
running characterization scripts.

Go into the scripts directory and run the following:

parse_characters.py
> python parse_characters.py 1

ident_aliases.py
> python ident_aliases.py character 1

parse_collocates.py
> python parse_collocates.py character 1


At this point you should be able to run many of the calc scripts (for example, calc_concreteness.py).
Most of them will require you to specify an output directory that is different from your data directory
(e.g. "../out/concreteness/").


If you have any questions or concerns at all, please contact hardik.vala@mail.mcgill.ca.


KNOWN ISSUES:
-------
- Preliminary setup with coreNLP and bookNLP needs to be made more straightfoward and easy to understand
- Initial code had functionality for parsing sub-copora as well as single works, but this has been commented
	out due to its reliance on hardcoding.
- Publication date is always 0 due to the original code hardcoding the publication date for each individual
	work. This date will have to be provided for each work through some additional metadata file perhaps.
- Various scripts require certain other scripts to be run first, and will often quietly fail if run out of
	order. Better feedback needs to be provided.

Credits:
-------
- Original code by Hardik Vala
- (Some) cleanup by Robert Budac
- Harry Potter and the Chamber of Secrets excerpt copied from:
https://www.bookbrowse.com/excerpts/index.cfm/book_number/453/Harry-Potter-and-The-Chamber-of-Secrets
