dataset=$1
global_repo_dir=$2
global_output_dir=$3
test_list=$4
task_type=$5
zip_valid=$6
zip_dest=$7

echo script version: $(git rev-parse HEAD)

base_dir=$(pwd)
mkdir -p $global_output_dir
cd $global_repo_dir
#rm $global_output_dir/stat.csv
for i in $(cut -d, -f1 $dataset | uniq | sed '1d'); do
    if [[ ! -d "$i" ]]; then
        echo $i,fail_to_clone >> $global_output_dir/stat.csv
        continue
    fi
    cd $base_dir
    bash install.sh $global_repo_dir $i $dataset $test_list $global_output_dir $task_type
    echo $i,install>> $global_output_dir/stat.csv

    # when running on Azure Machine:
    if [[ $zip_valid == 1 ]]; then
        zip -rq $i.zip $global_output_dir/$i
        sudo mkdir -p $zip_dest
        sudo rm $zip_dest/$i.zip
        sudo mv $i.zip $zip_dest/
    fi

    cd $global_repo_dir
done
cd $base_dir

