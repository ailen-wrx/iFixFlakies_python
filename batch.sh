dataset=$1
global_repo_dir=$2
global_output_dir=$3
test_list=$4

echo script version: $(git rev-parse HEAD)

parent_dir=$(pwd)
cd $global_repo_dir
rm $global_output_dir/stat.csv
for i in $(cut -d, -f1 $dataset | uniq | sed '1d'); do
    if [[ ! -d "$i" ]]; then
	echo $i,fail_to_clone >> $global_output_dir/stat.csv
	continue
    fi
    cd $global_repo_dir/$i
    if [[ ! -n "$(find -maxdepth 1 -name "*requirement*")" ]]; then
        echo $i,requirements_not_found >> $global_output_dir/stat.csv
	cd $global_repo_dir
        continue
    fi
    cd $parent_dir
    bash install.sh $global_repo_dir $i $dataset $test_list $global_output_dir
    echo $i,install>> $global_output_dir/stat.csv
    cd $global_repo_dir
done
cd $parent_dir

