# bash find_polluter_random.sh $(pwd)/Repo/Butter.MAS.PythonAPI $(pwd)/output/polluter_random/Butter.MAS.PythonAPI

project_dir=$1
output_dir=$2

echo script version: $(git rev-parse HEAD)

rm -rf $output_dir
mkdir -p $output_dir
cd $project_dir

source venv/bin/activate
pip install pytest-random-order
echo "Random testing..."
mkdir -p $output_dir
for j in {1..100}; do
    echo "[$j] pytest --random-order"
    timeout 1000s python3 -m pytest --random-order --csv pytest_random.csv > terminal_output
    exit_status=${PIPESTATUS[0]}
    if [[ ${exit_status} -eq 124 ]] || [[ ${exit_status} -eq 137 ]]; then
	echo "[$j] timeout"
	continue
    fi
    seed=$(grep random-order-seed= terminal_output | sed 's/Using --random-order-seed=//g' )
    mv pytest_random.csv $output_dir/$seed.csv
    mv terminal_output $output_dir/$seed.log
    echo "[$j] random-order-seed=$seed"
done
deactivate

cd -

