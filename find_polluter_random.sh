# bash find_polluter_random.sh butter/mas/tests/clients/client_http_test.py::TestHttpClientApiMethods::testGetAvailableAnimations test_list TestHttpClientApiMethods $(pwd)/Repo/Butter.MAS.PythonAPI $(pwd)/output/polluter_random/Butter.MAS.PythonAPI

victim=$1
test_list=$2
class=$3
project_dir=$4
output_dir=$5

echo script version: $(git rev-parse HEAD)

mkdir -p $output_dir
cd $project_dir

pip install pytest-random-order
if [[ ! -z "$class" ]]; then
    echo "Random testing in Test Class Mode..."
    mkdir -p $output_dir/tcm
    for j in {1..50}; do
	
	echo "[$j] pytest -k $class --random-order-bucket=global"
	timeout 1000s pytest -k $class --random-order-bucket=global --csv pytest_random.csv > terminal_output
	exit_status=${PIPESTATUS[0]}
	if [[ ${exit_status} -eq 124 ]] || [[ ${exit_status} -eq 137 ]]; then
	    echo "[$j] timeout"
	    continue
	fi
	seed=$(grep random-order-seed= terminal_output | sed 's/Using --random-order-seed=//g' )
	mv pytest_random.csv $output_dir/tcm/$seed.csv
	echo "[$j] random-order-seed=$seed"
    done
fi 

echo "Random testing in Test Suite Mode..."
mkdir -p $output_dir/tsm
for j in {1..50}; do
    echo "[$j] pytest --random-order-bucket=global"
    timeout 1000s pytest --random-order-bucket=global --csv pytest_random.csv > terminal_output
    exit_status=${PIPESTATUS[0]}
    if [[ ${exit_status} -eq 124 ]] || [[ ${exit_status} -eq 137 ]]; then
	echo "[$j] timeout"
	continue
    fi
    seed=$(grep random-order-seed= terminal_output | sed 's/Using --random-order-seed=//g' )
    mv pytest_random.csv $output_dir/tsm/$seed.csv
    echo "[$j] random-order-seed=$seed"
done

cd -

