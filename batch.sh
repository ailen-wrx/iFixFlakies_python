# bash batch.sh $(pwd)/dataset_latest.csv $(pwd)/Repo $(pwd)/output/isolated test_list 1 0
# bash batch.sh $(pwd)/dataset_latest.csv $(pwd)/Repo $(pwd)/output/polluter test_list 2 0

dataset=$1
global_repo_dir=$2
global_output_dir=$3
test_list=$4
task_type=$5
clear_output=$6

echo script version: $(git rev-parse HEAD)

base_dir=$(pwd)
mkdir -p $global_output_dir
cd $global_repo_dir
rm $global_output_dir/stat.csv
for i in $(cut -d, -f1 $dataset | uniq); do
    if [[ ! -d "$i" ]]; then
        cd /home/user/iFixFlakies_python/Repo
        rm -rf $i
        echo "copying $i.zip"
        cp /home/user/data/Installed_Repositories/$i.zip .
        echo "unzipping $i.zip"
        unzip $i.zip > /dev/null
        rm $i.zip
    fi

    if [[ ! -d "$i" ]]; then
        continue
    fi   

    cd $base_dir

    bash install.sh $global_repo_dir $i $dataset $test_list $global_output_dir $task_type $clear_output
    echo $i,install>> $global_output_dir/stat.csv

    cd $global_repo_dir
done
cd $base_dir

