#!/bin/bash
mkdir -p results
for FILE in test-images/[abc]-*.jpg; 
do 
  filename=$(basename -- "$FILE")
  extension="${filename##*.}"
  filename="${filename%.*}"
  results_file="results/${filename}_results.txt"
  groundtruth_file="test-images/${filename}_groundtruth.txt"

  printf "\n\n\n*********\n"
  echo "python3 grade.py $FILE $results_file";
  python3 grade.py $FILE $results_file;
  printf "\n******\n"

  echo "diff $results_file $groundtruth_file"
  diff $results_file $groundtruth_file
done

