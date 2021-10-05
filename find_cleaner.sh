polluter_list=$1
global_repo_dir=$2
global_output_dir=$3
zip_valid=$4
zip_dest=$5

echo script version: $(git rev-parse HEAD)

base_dir=$(pwd)
rm -rf $global_output_dir
mkdir -p $global_output_dir
for i in $(cat $polluter_list | sed '1d'); do
    project=$(cut -d, -f1 $i)
    polluter=$(cut -d, -f5 $i)
    polluter=$(cut -d, -f7 $i)

    cd $global_repo_dir/$project
    rm -rf venv
    python3 -m venv venv
    source venv/bin/activate
    for i in $(find -maxdepth 1 -name "*requirement*"); do
        pip3 install -r $i
    done
    pip3 install pytest
    pip3 install pytest-csv

    md5=$(echo $i | md5sum | cut -d' ' -f1)
    


done