input_csv=$1
linenum=$(cat $input_csv | wc -l)
echo $linenum

for ((i=2;i<=$linenum;i++))
  do
    for eachline in $i
    do
	project=$(sed -n ${i}p $input_csv | cut -d "," -f1)
	sha=$(sed -n ${i}p $input_csv | cut -d "," -f3)
       	polluter_full_path=$(sed -n ${i}p $input_csv | cut -d "," -f4)
	cleaner_full_path=$(sed -n ${i}p $input_csv | cut -d "," -f5)
        victim_full_path=$(sed -n ${i}p $input_csv | cut -d "," -f6)
        combination_path=${victim_full_path%.*}_com.py
        #echo $combination_path
	cd /home/yyy/pythonOD/explore_test/projects_with_cleaner/$project
	python3 -m venv venv
	source venv/bin/activate
	python -m pytest $polluter_full_path $victim_full_path  --csv before.csv 
	python3 ../../../ast_test/copy_test.py $project $sha $polluter_full_path $cleaner_full_path $victim_full_path $combination_path --csv before.csv

	deactivate
        cd /home/yyy/pythonOD/ast_test 
    done
  done
  
