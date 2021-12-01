
input_csv=$1
linenum=$(cat $input_csv | wc -l)
save_path=$2
repo=$3
clear=$4
echo $linenum

if [[ "$clear"  == 1  ]]; then
    echo clear_output
    echo project,sha,statesetter_fullpath,brittle_fullpath,md5,pv_result,pcv_result,can_copy_work,1st_patch_time,minimal_patch_time,patch_path,diff,verification_patch_result,inserted_node > $save_path
fi
    
base_dir=$(pwd)

for project_name in $(cat $input_csv | sed '1d' | cut -d, -f1 | uniq); do
    cd $repo
    echo $project_name
    if [[ ! -d "$project_name" ]]; then
	echo "copying $project_name"
	cp /home/user/data/Installed_Repositories/$project_name.zip .
	echo "unzipping $project_name"
	unzip $project_name.zip > /dev/null
	rm $project_name.zip

    fi

    for i in $(cat $input_csv | fgrep "$project_name," ); do
# for ((i=2;i<=$linenum;i++))
#   do
#     for eachline in $i
#     do
	project=$(echo $i | cut -d "," -f1)
	sha=$(echo $i | cut -d "," -f3)
       	statesetter_full_path=$(echo $i | cut -d "," -f6)
        brittle_full_path=$(echo $i | cut -d "," -f4)
        combination_path=${brittle_full_path%.*}_patch.py
	#save_path=/home/yyy/test_result_patcher.csv
        #echo $combination_path
	#if [[ -n $(fgrep "$statesetter_full_path,$brittle_full_path" $save_path) ]]; then
	#    echo $(fgrep "$statesetter_full_path,$brittle_full_path" $save_path)
	#    echo "Pass."
	#    continue
	#fi
	cd $repo

	echo $(pwd)

	echo $project
	
#	if [[ ! -d "$project" ]]; then
#	    echo "copying $project"
#	    cp /home/user/data/Repo_zipped/$project.zip .
#	    echo "unzipping $project"
#	    unzip $project.zip > /dev/null
#	    rm $project.zip

#	fi

#	read a

	cd $project

	source venv/bin/activate

#	echo $project $sha $polluter_full_path $cleaner_full_path $victim_full_path $combination_path $save_path

	python3 $base_dir/brittle_patcher2.py $project $sha $statesetter_full_path $brittle_full_path $combination_path $save_path 

	deactivate
        cd $base_dir
    done
    rm -rf $repo/$project_name
  done
  