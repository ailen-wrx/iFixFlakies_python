# bash find_cleaner.sh parsing_result/polluter_tsm/polluter-potential.csv $(pwd)/Repo test_list $(pwd)/output/cleaner 3

polluter_list=$1
global_repo_dir=$2
test_list=$3
global_output_dir=$4
max_cleaner=$5

echo script version: $(git rev-parse HEAD)

mkdir -p global_output_dir/cleaners

base_dir=$(pwd)
if [[ $clear_output == 1 ]]; then
    rm -rf $global_output_dir
fi
mkdir -p $global_output_dir
if [[ ! -f "$global_output_dir/cleaner.csv" ]]; then
    echo "Project_Name,Project_URL,Project_Hash,Polluter,Cleaner,Victim" > $global_output_dir/cleaner.csv
fi
for vict in $(cut -d, -f1,7 $polluter_list | sed '1d' | sort | uniq); do
    echo $vict

for i in $(cat $polluter_list | fgrep "$(echo $vict | cut -d, -f1)" | fgrep "$(echo $vict | cut -d, -f2)" | shuf -n 5 --random-source=<(cat $base_dir/victims_brittles.csv)); do
    project=$(echo $i | cut -d, -f1)
    url=$(echo $i | cut -d, -f2)
    sha=$(echo $i | cut -d, -f3)

    test_filename=$(echo $i | cut -d, -f4)
    polluter=$(echo $i | cut -d, -f5)
    victim=$(echo $i | cut -d, -f7)

    if [[ "$project" == "Project_Name" ]]; then
	continue
    fi

    cd $global_repo_dir
    if [ ! -d "$project" ]; then
	cp /home/user/data/Repo_zipped/$project.zip .
	unzip $project.zip > /dev/null
	rm $project.zip
    fi

    cd $global_repo_dir/$project

    source venv/bin/activate
    
    polluter_victim=$(echo $i | md5sum | cut -d' ' -f1) 
    
    mkdir -p $global_output_dir/$polluter_victim

    echo $polluter_victim,$project,$polluter,$victim >> $global_output_dir/cleaners/polluter-victim-mapping.csv

    cleaner_cnt=0
    if [[ "$tcm" == 1 ]]; then
	tlist=$(fgrep "$test_filename" $test_list)
	echo "[tcm]"
    else
	tlist=$(fgrep "::" $test_list)
    fi
    for t in $tlist; do
	if [[ "$t" == "polluter" || "$t" == "victim" ]]; then
	    continue
	fi
	echo "---------------------------------------"
	echo [project] $project
	echo [polluter] $polluter
	echo [victim] $victim
	echo Testing: $t
	md5=$(echo $t | md5sum | cut -d' ' -f1)
	timeout 1000s python -m pytest $polluter $t  $victim --csv $global_output_dir/cleaners/$polluter_victim/$md5.csv > $global_output_dir/cleaners/$polluter_victim/$md5.log
	exit_status=${PIPESTATUS[0]}
	if [[ ${exit_status} -eq 124 ]] || [[ ${exit_status} -eq 137 ]]; then
	    echo $t >> $global_output_dir/cleaners/$polluter_victim/timed_out.csv
	    continue
	fi
	cleaner_flag=$(grep "3 passed" $global_output_dir/$polluter_victim/$md5.log)
	if [[ -n "$cleaner_flag" ]]; then
	    echo "*Cleaner*" $t
	    echo $project,$url,$sha,$polluter,$t,$victim >> $global_output_dir/cleaner.csv
	    let cleaner_cnt++
	fi
	echo "---------------------------------------"
	echo $md5,$t >> $global_output_dir/cleaners/$polluter_victim/test_mapping.csv
	if (( $max_cleaner != 0 )) && (( $cleaner_cnt >= $max_cleaner )); then
	    break
	fi
    done

    deactivate


done

done
