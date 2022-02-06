$ wget https://zenodo.org/record/5949906/files/ipflakies_docker_container.tar

$ docker import ipflakies_docker_container.tar ipflakies

$ docker run -it -v $(pwd)/docker_output:/root/external --name ipflakies_test ipflakies /bin/bash

    cd /root

    grep IOCynergy pytest_suites.csv > test.in
    # sed -n '436,440p' pytest_suites.csv > test.in

    bash exec_ipflakies.sh test.in dataset.csv

    exit

$ cp -r docker_output/ipflakies_result ./ipflakies_result_test
$ bash unzip_output.sh ipflakies_result_test
$ python3 parse_result.py ipflakies_result_test Summary_test



