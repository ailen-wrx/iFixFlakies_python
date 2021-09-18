func_name=$1
test_list=$2
module=$3
project_dir=$4
output_dir=$5

rm -rf $output_dir
mkdir -p $output_dir
cd $project_dir
victim=$(grep $module:: $test_list | grep ::$func_name | head -1)
for i in $(grep $module:: $test_list); do
    if [[ "$i" == "$victim" ]]; then
	i=""
    fi
    md5=$(echo $i,$victim | md5sum | cut -d' ' -f1)
    timeout 1000s pytest $i $victim --csv $output_dir/$md5.csv
    exit_status=${PIPESTATUS[0]}
    if [[ ${exit_status} -eq 124 ]] || [[ ${exit_status} -eq 137 ]]; then
        echo $i,$victim >> $output_dir/timed_out.csv
        continue
    fi
    echo $i,$victim,$md5 >> $output_dir/test_mapping.csv
done
cd -

