repo_dir=$1
project=$2
dataset=$3
test_list=$4
output_dir=$5
task_type=$6

cd $repo_dir/$project

python3 -m venv venv
source venv/bin/activate
for i in $(find -maxdepth 1 -name "*requirement*"); do
    pip install -r $i
done
pip install pytest
pip install pytest-csv

pytest --collect-only -q > $test_list
cd -
rm -rf $output_dir/$project
mkdir -p $output_dir/$project

for i in $(grep $project, $dataset); do
    Test_filename=$(echo $i | cut -d, -f4)
    Test_classname=$(echo $i | cut -d, -f5)
    Test_funcname=$(echo $i | cut -d, -f6)
    Test_parametrization=$(echo $i | cut -d, -f7)
    md5=$(echo $i | md5sum | cut -d' ' -f1)
    echo $Test_filename,$Test_funcname,$(date) >> $output_dir/$project/log_pytest.csv
    echo  $Test_filename,$Test_funcname,$md5 >> $output_dir/$project/victim_mapping.csv

    if [[ $task_type == 1 ]]; then
        bash verdict_isolated.sh $Test_funcname $test_list $Test_filename $repo_dir/$project $output_dir/$project/$md5
    fi

    if [[ $task_type == 2 ]]; then
        bash find_polluter.sh $Test_funcname $test_list $Test_filename $repo_dir/$project $output_dir/$project/$md5
    fi

    if [[ $task_type == 3 ]]; then
        continue
    fi
    
done
deactivate
rm -rf $repo_dir/$project/venv
