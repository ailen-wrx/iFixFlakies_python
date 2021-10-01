victim=$1
test_list=$2
module=$3
project_dir=$4
output_dir=$5

mkdir -p $output_dir
cd $project_dir
for i in {1..10}; do
    timeout 400s pytest $victim --csv $output_dir/$i.csv
    exit_status=${PIPESTATUS[0]}
    if [[ ${exit_status} -eq 124 ]] || [[ ${exit_status} -eq 137 ]]; then
        echo $i >> $output_dir/timed_out.csv
        continue
    fi
done
cd -
