victim=$1
test_list=$2
module=$3
project_dir=$4
output_dir=$5

echo script version: $(git rev-parse HEAD)

mkdir -p $output_dir
cd $project_dir
for i in $(grep $module:: $test_list); do
    if [[ "$i" == "$victim" ]]; then
	continue
    fi
    md5=$(echo $i,$victim | md5sum | cut -d' ' -f1)
    timeout 1000s python -m pytest $i $victim --csv $output_dir/$md5.csv
    exit_status=${PIPESTATUS[0]}
    if [[ ${exit_status} -eq 124 ]] || [[ ${exit_status} -eq 137 ]]; then
	echo $i,$victim >> $output_dir/timed_out.csv
	continue
    fi
done
cd -

