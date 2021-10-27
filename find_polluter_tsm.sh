#bash find_polluter_tsm.sh tests/test_merger.py::test_core_commands test_list $(pwd)/Repo/Breathe $(pwd)/output/polluter_tsm/Breathe

victim=$1
test_list=$2
project_dir=$3
output_dir=$4

echo script version: $(git rev-parse HEAD)

mkdir -p $output_dir
cd $project_dir
for i in $(fgrep "::" $test_list); do
    if [[ "$i" == "$victim" ]]; then
        continue
    fi

    echo [project] $project_dir
    echo [victim] $victim
    echo Testing: $i
    md5=$(echo $i,$victim | md5sum | cut -d' ' -f1)
    timeout 1000s python3 -m pytest $i $victim --csv $output_dir/$md5.csv >> $output_dir/$md5.log
    exit_status=${PIPESTATUS[0]}
    if [[ ${exit_status} -eq 124 ]] || [[ ${exit_status} -eq 137 ]]; then
        echo $i,$victim >> $output_dir/timed_out.csv
        continue
    fi
    echo $i,$md5 >> $output_dir/test_mapping.csv
done
cd -

