#!/bin/bash

# Note: Unfortunately, must be invoked from the BookNLP project directory.

if [[ ! -f files/coref.weights ]]
then
	echo "ERROR: Must be invoked from the BookNLP project directory."
	exit 1
fi

usage() {
	echo -e "Usage:$0 [-h] -b <BookNLP path> -t <Corpus path> -o <Output directory path> -l <Log directory path> -n <# Processes> [-f]"
}

# TODO: Print usage message on erroneous input.

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
		-f|--force)
		# Force re-running CoreNLP over texts already with CoreNLP output files.
		FORCE=true
		;;
		-b|--booknlp)
		# Path to BookNLP folder.
		BOOKNLP_DIRPATH=$2
		shift
		;;
		-t|--texts)
		# Path to corpus folder with texts.
		TEXTS_DIRPATH=$2
		shift
		;;
		-o|--output)
		# Path to folder for all BookNLP output directories.
		OUTPUT_DIRPATH=$2
		shift
		;;
		-l|--logs)
		# Path to logs directory.
		LOGS_DIRPATH=$2
		shift
		;;
		-n|--nproc)
		# Number of processes to spawn.
		NPROC=$2
		shift
		;;
		*)
		# Unknown parameter.
		usage
		exit 1
		;;
	esac
	shift
done

if [[ -z $BOOKNLP_DIRPATH || -z $TEXTS_DIRPATH || -z $OUTPUT_DIRPATH || -z $LOGS_DIRPATH || -z $NPROC ]]
then
	usage
	exit 1
fi

# Random Id to attached to file list filenames.
exid=$(cat /proc/sys/kernel/random/uuid)

# Temporary directory to store file lists.
mkdir -p .tmp

i=0
for text_path in $(find $TEXTS_DIRPATH -name '*.txt')
do
	filename=$(basename $text_path)
	if [[ ! -d "$OUTPUT_DIRPATH/${filename%.*}" || $FORCE ]]
	then
		r=`expr $i % $NPROC`
		# File lists are created in the current directory.
		echo $text_path >> .tmp/booknlp-filelist-$exid-$r
		i=`expr $i + 1`
	fi
done

mkdir -p $OUTPUT_DIRPATH
mkdir -p $LOGS_DIRPATH

i=0
for filelist_path in $(pwd)/.tmp/booknlp-filelist-$exid-*
do
	echo "[run-corpus-booknlp.sh] Processing $filelist_path..."
	/bin/bash ../scripts/run-booknlp.sh -b $BOOKNLP_DIRPATH -t $filelist_path -o $OUTPUT_DIRPATH -l $LOGS_DIRPATH/$i.log &
	i=`expr $i + 1`
done
