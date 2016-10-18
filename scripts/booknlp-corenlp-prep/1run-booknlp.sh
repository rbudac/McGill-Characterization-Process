#cd ../book-nlp/
#./runjava novels/BookNLP -p "../out/" -tok "../out/tokens" -doc "../texts/example.txt" -printHTML
#cd ../scripts/


#$BOOKNLP_DIRPATH/runjava novels/BookNLP -doc $line -printHTML -p $out_dir -tok $out_dir/tokens -f >> $LOG_PATH 2>&1


./aaa.sh -b "../book-nlp/" -t "../list/filelist.txt" -o "../out/" -l "../out/log.log"
