# bash find_cleaner.sh parsing_result/polluter_tsm/polluter-potential.csv $(pwd)/Repo test_list $(pwd)/output/cleaner

polluter_list=$1
global_repo_dir=$2
test_list=$3
global_output_dir=$4


echo script version: $(git rev-parse HEAD)

base_dir=$(pwd)
rm -rf $global_output_dir
mkdir -p $global_output_dir
for i in $(cat $polluter_list | sed '1d'); do
    project=$(echo $i | cut -d, -f1)
    polluter=$(echo $i | cut -d, -f5)
    victim=$(echo $i | cut -d, -f7)

    echo in $project
    echo [polluter] $polluter
    echo [victim]: $victim

    cd $global_repo_dir/$project

    source venv/bin/activate
    
    polluter_victim=$(echo $i | md5sum | cut -d' ' -f1)

    mkdir -p $global_output_dir/$polluter_victim

    echo $polluter_victim,$project,$polluter,$victim >> $global_output_dir/polluter-victim-mapping.csv
    
    for t in $(grep :: $test_list); do
	if [[ "$t" == "polluter" || "$t" == "victim" ]]; then
	    continue
	fi
	md5=$(echo $t | md5sum | cut -d' ' -f1)
	timeout 1000s python -m pytest $polluter $t  $victim --csv $global_output_dir/$polluter_victim/$md5.csv
	exit_status=${PIPESTATUS[0]}
	if [[ ${exit_status} -eq 124 ]] || [[ ${exit_status} -eq 137 ]]; then
	    echo $t >> $global_output_dir/$polluter_victim/timed_out.csv
	    continue
	fi
	echo $md5,$t >> $global_output_dir/$polluter_victim/test_mapping.csv
    done


done
