input_dataset=$1

pip install pandas
pip install py

mkdir -p repro/src

cp input_dataset repro/src/dataset_final.csv

bash batch.sh $(pwd)/repro/src/dataset_final.csv $(pwd)/Repo $(pwd)/repro/src/isolated test_list 1 0

python3 isolated.py repro/src/dataset_final.csv repro/src/

bash exec_idflakies.sh

bash batch.sh $(pwd)/repro/src/dataset_final.csv $(pwd)/Repo $(pwd)/repro/src/polluter test_list 2 0

python3 polluter_or_state_setter.py repro/src

python3 idflakies.py

python3 random_parsing.py

bash find_cleaner.sh repro/src/polluters.csv $(pwd)/Repo test_list $(pwd)/repro/src 3

python3 Test_status.py


