dataset=$1
global_repo_dir=$2
global_output_dir=$3

fail_to_clone=0
no_req=0
missing=0
success=0

echo script version: $(git rev-parse HEAD)

parent_dir=$(pwd)
cd $global_repo_dir
for i in $(cut -d, -f1 $dataset | uniq | sed '1d'); do
    if [[ ! -d "$i" ]]; then
	fail_to_clone=`expr $fail_to_clone + 1`
	echo $i,fail_to_clone >> $global_output_dir/stat.csv
	continue
    fi
    cd $global_repo_dir/$i
    if [[ ! -n "$(find -maxdepth 1 -name "*requirement*")" ]]; then
	no_req=`expr $no_req + 1`
        echo $i,requirements_not_found >> $global_output_dir/stat.csv
	cd $global_repo_dir
        continue
    fi
    cd $parent_dir
    bash install.sh $global_repo_dir $i victims_brittles.csv tests.csv output;
    echo $i,can_install>> $global_output_dir/stat.csv
    cd $global_repo_dir
done
cd $parent_dir
echo $fail_to_clone,$no_req

