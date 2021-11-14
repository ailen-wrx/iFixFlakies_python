
input_csv=$1
linenum=$(cat $input_csv | wc -l)
save_path=$2
repo=$3
echo $linenum

echo project,sha,polluter_fullpath,cleaner_fullpath,victim_fullpath,md5,pv_result,pcv_result,can_copy_work,1st_patch_time,minimal_patch_time >> $save_path

base_dir=$(pwd)

for ((i=2;i<=$linenum;i++))
  do
    for eachline in $i
    do
	project=$(sed -n ${i}p $input_csv | cut -d "," -f1)
	sha=$(sed -n ${i}p $input_csv | cut -d "," -f3)
       	polluter_full_path=$(sed -n ${i}p $input_csv | cut -d "," -f4)
	cleaner_full_path=$(sed -n ${i}p $input_csv | cut -d "," -f5)
        victim_full_path=$(sed -n ${i}p $input_csv | cut -d "," -f6)
        combination_path=${victim_full_path%.*}_patch.py
	#save_path=/home/yyy/test_result_patcher.csv
        #echo $combination_path

	cd $repo

	echo $(pwd)

	echo $project
	
	if [[ ! -d "$project" ]]; then
	    echo "copying $project"
	    cp /home/user/data/Repo_zipped/$project.zip .
	    echo "unzipping $project"
	    unzip $project.zip > /dev/null
	    rm $project.zip
	    echo "呜呜呜呜"
	fi

#	read a

	cd $project

	source venv/bin/activate
	python -m pytest $polluter_full_path $victim_full_path

	echo $project $sha $polluter_full_path $cleaner_full_path $victim_full_path $combination_path $save_path

	python3 $base_dir/new_patcher.py $project $sha $polluter_full_path $cleaner_full_path $victim_full_path $combination_path $save_path 

	deactivate
        cd $base_dir
    done
  done
  
