#!/bin/bash

usage() {
	echo -e "Usage:$0 [-h] -c <CoreNLP path> -t <Corpus path> -o <Output directory path> -l <Log directory path> -n <# Processes> [-f]"
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
		-f|--force)
		# Force re-running CoreNLP over texts already with CoreNLP output files.
		FORCE=true
		;;
		-c|--corenlp)
		# Path to CoreNLP folder.
		CORENLP_DIRPATH=$2
		shift
		;;
		-t|--texts)
		# Path to corpus folder with texts.
		TEXTS_DIRPATH=$2
		shift
		;;
		-o|--output)
		# Path to folder for CoreNLP output files.
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

if [[ -z $CORENLP_DIRPATH || -z $TEXTS_DIRPATH || -z $OUTPUT_DIRPATH || -z $LOGS_DIRPATH || -z $NPROC ]]
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
	if [[ ! -f "$OUTPUT_DIRPATH/${filename%.*}.xml" || $FORCE ]]
	then
		r=`expr $i % $NPROC`
		# File lists are created in the current directory.
		echo $text_path >> .tmp/corenlp-filelist-$exid-$r
		i=`expr $i + 1`
	fi
done

mkdir -p $OUTPUT_DIRPATH
mkdir -p $LOGS_DIRPATH

i=0
for filelist_path in $(pwd)/.tmp/corenlp-filelist-$exid-*
do
	/bin/bash run-corenlp.sh -c $CORENLP_DIRPATH -t $filelist_path -o $OUTPUT_DIRPATH -l $LOGS_DIRPATH/$i.log &
	i=`expr $i + 1`
done

