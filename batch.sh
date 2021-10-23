# bash batch.sh $(pwd)/dataset_latest.csv $(pwd)/Repo $(pwd)/output/isolated test_list 1
# bash batch.sh $(pwd)/dataset_latest.csv $(pwd)/Repo $(pwd)/output/polluter test_list 2
# bash batch.sh $(pwd)/dataset_latest.csv $(pwd)/Repo $(pwd)/output/polluter_tsm test_list 3
# bash batch.sh $(pwd)/dataset_latest.csv $(pwd)/Repo $(pwd)/output/polluter_random test_list 4

dataset=$1
global_repo_dir=$2
global_output_dir=$3
test_list=$4
task_type=$5

echo script version: $(git rev-parse HEAD)

base_dir=$(pwd)
mkdir -p $global_output_dir
cd $global_repo_dir
rm $global_output_dir/stat.csv
for i in $(cut -d, -f1 $dataset | uniq); do
    if [[ ! -d "$i" ]]; then
        echo $i,fail_to_clone >> $global_output_dir/stat.csv
        continue
    fi
    cd $base_dir

    if [[ $task_type == 3 ]]; then
        bash find_polluter_random.sh $global_repo_dir/$i $global_output_dir/$i
        continue
    fi

    bash install.sh $global_repo_dir $i $dataset $test_list $global_output_dir $task_type
    echo $i,install>> $global_output_dir/stat.csv

    cd $global_repo_dir
done
cd $base_dir

