pip install pandas
pip install py

mkdir -p repro/src

read a

cp dataset_trial.csv repro/src/dataset_final.csv

bash batch.sh $(pwd)/repro/src/dataset_final.csv $(pwd)/Repo $(pwd)/repro/src/isolated test_list 1 0

python3 isolated.py repro/src/dataset_final.csv repro/src/

bash exec_idflakies.sh

python3 idflakies.py

python3 -m random_parsing.py

bash batch.sh $(pwd)/repro/src/dataset_final.csv $(pwd)/Repo $(pwd)/repro/src/polluter test_list 2 0

python3 polluter_or_state_setter.py repro/src

bash find_cleaner.sh repro/src/polluters.csv $(pwd)/Repo test_list $(pwd)/repro/src 0

python3 Test_status.py


