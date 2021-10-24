# bash find_cleaner.sh parsing_result/polluter_tsm/polluter-potential.csv $(pwd)/Repo test_list $(pwd)/output/cleaner 1

polluter_list=$1
global_repo_dir=$2
test_list=$3
global_output_dir=$4
clear_output=$5

echo script version: $(git rev-parse HEAD)

base_dir=$(pwd)
if [[ $clear_output == 1 ]]; then
    rm -rf $global_output_dir
fi
mkdir -p $global_output_dir
for i in $(cat $polluter_list); do
    project=$(echo $i | cut -d, -f1)
    polluter=$(echo $i | cut -d, -f5)
    victim=$(echo $i | cut -d, -f7)

    if [[ "$project" == "Project_Name" ]]; then
	continue
    fi
    
    echo In $project:

    cd $global_repo_dir/$project

    source venv/bin/activate
    
    polluter_victim=$(echo $i | md5sum | cut -d' ' -f1)

    mkdir -p $global_output_dir/$polluter_victim

    echo $polluter_victim,$project,$polluter,$victim >> $global_output_dir/polluter-victim-mapping.csv
    
    for t in $(grep :: $test_list); do
	if [[ "$t" == "polluter" || "$t" == "victim" ]]; then
	    continue
	fi
	echo [polluter] $polluter
	echo [Victim] $victim
	echo Testing: $t
	md5=$(echo $t | md5sum | cut -d' ' -f1)
	timeout 1000s python -m pytest $polluter $t  $victim --csv $global_output_dir/$polluter_victim/$md5.csv > $global_output_dir/$polluter_victim/$md5.log
	exit_status=${PIPESTATUS[0]}
	if [[ ${exit_status} -eq 124 ]] || [[ ${exit_status} -eq 137 ]]; then
	    echo $t >> $global_output_dir/$polluter_victim/timed_out.csv
	    continue
	fi
	cleaner_flag=$(grep "3 passed" $global_output_dir/$polluter_victim/$md5.log)
	if [[ ! -n "$cleaner_flag" ]]; then
	    echo [Cleaner Found] $t
	fi
	echo $md5,$t >> $global_output_dir/$polluter_victim/test_mapping.csv
    done

    deactivate


done
