#!/bin/bash

for FILE in ../test-images/[abc]-*.jpg; 
do 
  filename=$(basename -- "$FILE")
  extension="${filename##*.}"
  filename="${filename%.*}"
  results_file="results2/${filename}_results.txt"
  groundtruth_file="../test-images/${filename}_groundtruth.txt"

  printf "\n\n\n*********\n"
  echo "python grade2.py $FILE $results_file";
  python grade2.py $FILE $results_file;
  printf "\n******\n"

  echo "diff $results_file $groundtruth_file"
  diff $results_file $groundtruth_file
done

