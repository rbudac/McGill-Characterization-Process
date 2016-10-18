#!/bin/bash

usage() {
	echo -e "Usage:$0 [-h] -b <BookNLP path> -t <Filelist path> -o <Output directory path> -l <Log filepath>"
}

# Parse arguments.
while [[ $@ > 0 ]]
do
	key=$1
	
	case $1 in
		-h|--help)
		# Display usage.
		usage
		exit 0
		;;
		-b|--booknlp)
		# Path to BookNLP project directory.
		BOOKNLP_DIRPATH=$2
		shift
		;;
		-t|--text)
		# Path to file with paths to input text files.
		FILELIST_PATH=$2
		shift
		;;
		-o|--output)
		# Path to output directory.
		OUTPUT_DIRPATH=$2
		shift
		;;
		-l|--log)
		# Path to log file.
		LOG_PATH=$2
		shift
		;;
		*)
		usage
		exit 1
		;;
	esac
	shift
done

if [[ -z $BOOKNLP_DIRPATH || -z $FILELIST_PATH || -z $OUTPUT_DIRPATH || -z $LOG_PATH ]]
then
	usage
	exit 1
fi

# Each line corresponds to an input text filepath.
while read -r line
do
	filename=$(basename $line)
	out_dir=$OUTPUT_DIRPATH/${filename%.*}
	$BOOKNLP_DIRPATH/runjava novels/BookNLP -doc $line -printHTML -p $out_dir -tok $out_dir/tokens -f >> $LOG_PATH 2>&1
done < $FILELIST_PATH

# Remove the filelist when done.
# rm -f $FILELIST_PATH

# If parent directory is empty, then remove it.
# parent_dirpath=$(dirname $FILELIST_PATH)
# [ -d $parent_dirpath ] && [ "$(ls -A $parent_dirpath 2>/dev/null)" ] && rm -rf $parent_dirpath
