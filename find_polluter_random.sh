#bash find_polluter_random.sh tests/test_merger.py::test_core_commands test_list $(pwd)/Repo/Breathe $(pwd)/output/polluter_tsm/Breathe

victim=$1
test_list=$2
project_dir=$3
output_dir=$4

echo script version: $(git rev-parse HEAD)

mkdir -p $output_dir
cd $project_dir
for i in {1..100}
do

    timeout 1000s python -m pytest $i $victim --csv $output_dir/$md5.csv
    exit_status=${PIPESTATUS[0]}
    if [[ ${exit_status} -eq 124 ]] || [[ ${exit_status} -eq 137 ]]; then
        echo $i,$victim >> $output_dir/timed_out.csv
        continue
    fi
done
cd -

