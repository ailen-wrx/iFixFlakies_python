# bash install.sh $(pwd)/Repo Butter.MAS.PythonAPI $(pwd)/dataset_trial.csv test_list $(pwd)/output/polluter_tsm 3 0

repo_dir=$1
project=$2
dataset=$3
test_list=$4
output_dir=$5
task_type=$6
clear_output=$7

cd $repo_dir/$project

source venv/bin/activate

cd -
if [[ $clear_output == 1 ]]; then
    rm -rf $output_dir/$project
fi
mkdir -p $output_dir/$project

echo Running $project...
for i in $(grep $project, $dataset); do
    Test_filename=$(echo $i | cut -d, -f4)
    Test_classname=$(echo $i | cut -d, -f5)
    Test_funcname=$(echo $i | cut -d, -f6)
    Test_parametrization=$(echo $i | cut -d, -f7)

    if [[ $Test_classname == '' ]]; then 
        if [[ $Test_parametrization == '' ]]; then
            victim=$(grep $Test_filename:: $repo_dir/$project/$test_list | grep ::$Test_funcname | sort | head -1)
        else
            victim=$(grep $Test_filename:: $repo_dir/$project/$test_list | grep ::$Test_funcname | grep -F $Test_parametrization | sort | head -1)
        fi
    else
        if [[ $Test_parametrization == '' ]]; then
            victim=$(grep $Test_filename:: $repo_dir/$project/$test_list | grep ::$Test_classname | grep ::$Test_funcname | sort | head -1)
        else
            victim=$(grep $Test_filename:: $repo_dir/$project/$test_list | grep ::$Test_classname | grep ::$Test_funcname | grep -F $Test_parametrization | sort | head -1)
        fi
    fi

    if [[ -z "$victim" ]]; then
        continue
    fi


    echo Found $victim.

    if [[ -n $(fgrep "$victim" $output_dir/$project/victim_mapping.csv) ]]; then
	echo Skipped.
	continue
    fi
    
    md5=$(echo $i | md5sum | cut -d' ' -f1)
    echo $victim,$(date) >> $output_dir/$project/log_pytest.csv
    echo $victim,$md5 >> $output_dir/$project/victim_mapping.csv

    if [[ $task_type == 1 ]]; then
        echo "isolated test"
	    bash verdict_isolated.sh $victim $test_list $Test_filename $repo_dir/$project $output_dir/$project/$md5
    fi

    if [[ $task_type == 2 ]]; then
        echo "polluter_tsm"
	    bash find_polluter.sh $victim $test_list $repo_dir/$project $output_dir/$project/$md5
    fi
	
  	
done

deactivate

rm -rf ~/.cache/pip/http
rm -rf ~/.danlp/

