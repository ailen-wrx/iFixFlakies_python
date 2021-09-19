repo_dir=$1
project=$2
dataset=$3
test_list=$4
output_dir=$5

cd $repo_dir/$project
echo Installing $project...
sha=$(grep $project, $dataset | cut -d, -f3 | head -1)
echo Switching to $sha...
git remote set-branches origin $sha
git fetch --depth 1 origin $sha
git checkout $sha

python3 -m venv venv
source venv/bin/activate
for i in $(find -name "*requirement*"); do
    pip install -r $i
done
pip install pytest
pip install pytest-csv
pytest --collect-only -q > $test_list
cd -
mkdir -p $output_dir/$project
for i in $(grep $project, $dataset); do
    echo processing $project starttime: $(date) >> log_install
    Test_filename=$(echo $i | cut -d, -f4)
    Test_classname=$(echo $i | cut -d, -f5)
    Test_funcname=$(echo $i | cut -d, -f6)
    Test_parametrization=$(echo $i | cut -d, -f7)
    md5=$(echo $i | md5sum | cut -d' ' -f1)
    echo  $Test_filename,$Test_funcname,$md5 >> $output_dir/$project/victim_mapping.csv
    bash find_polluter.sh $Test_funcname $test_list $Test_filename $repo_dir/$project $output_dir/$project/$md5
done
deactivate
rm -rf $repo_dir/$project/venv
