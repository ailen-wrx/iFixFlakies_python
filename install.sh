repo_dir=$1
project=$2
dataset=$3
test_list=$4
output_dir=$5

cd $repo_dir/$project
python3 -m venv venv
source venv/bin/activate
for i in $(find -name "*requirement*"); do
    pip install -r $i
done
pip install pytest-csv
pytest --csv $test_list
cd -
mkdir -p $output_dir/$project
for i in $(grep $project, $dataset); do
    module=$(echo $i | cut -d, -f5)
    victim=$(echo $i | cut -d, -f4)::$(echo $i | cut -d, -f6)$(echo $i | cut -d, -f7)
    md5=$(echo $i | md5sum | cut -d' ' -f1)
    echo  $module,$(echo $i | cut -d, -f6),$md5 >> $output_dir/$project/victim_mapping.csv
    bash find_polluter.sh $victim $test_list $module $repo_dir/$project $(pwd)/$output_dir/$project/$md5
done
deactivate
rm -rf venv
