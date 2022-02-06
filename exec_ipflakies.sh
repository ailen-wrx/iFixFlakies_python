# bash exec_ipflakies.sh test.in dataset.csv

input=$1
dataset=$2

mkdir -p /root/external/ipflakies_result
mkdir -p /root/external/ipflakies_log
mkdir -p /root/external/install_log
mkdir -p /root/Projects
for info in $(cat $input); do
    project=$(echo $info | cut -d, -f1)
    tuples=$(grep $project $dataset)
    url=$(echo $info | cut -d, -f2)
    sha=$(echo $info | cut -d, -f3)

    cd /root
    echo "[ PROJECT ] $project"

    rm -rf $project
    echo Cloning $project start at: $(date) >> log_clone

    timeout 600s git clone $url --depth=1
    exit_status=${PIPESTATUS[0]}
    if [[ ${exit_status} -eq 124 ]] || [[ ${exit_status} -eq 137 ]]; then
        echo "[ PROJECT ] $project not found."
	echo "$project,do_not_exist" >> /root/external/error.csv
	continue
    fi
    if [[ ! -d $project ]]; then
	echo "[ PROJECT ] $project not cloned."
	echo "$project,fail_to_clone" >> /root/external/error.csv
	continue
    fi
	
    cd $project
    git remote set-branches origin $sha
    git fetch --depth 1 origin $sha
    git checkout $sha

    if [[ -e "Pipfile" ]]; then
	pipfile freeze -o ./requirements_Pipfile.txt
    fi
    
    python3 -m venv venv
    source venv/bin/activate
    pip3 install --upgrade pip > /dev/null
    echo "[ PROJECT ] $project installing dependencies..."
    echo "" > /root/external/install_log/$project.log
    for i in $(find -name "*requirement*"); do
	pip3 install -r $i >> /root/external/install_log/$project.log 2>&1
    done
    pip3 install ipflakies==1.1.0 > /dev/null

    timeout 864s python3 -m pytest
    exit_status=${PIPESTATUS[0]}
    if [[ ${exit_status} -eq 124 ]] || [[ ${exit_status} -eq 137 ]]; then
	echo "[ PROJECT ] $project timed out."
	echo "$project,timed_out" >> /root/external/error.csv
	continue
    fi

    python3 -m pytest --collect-only -q > test_list
    echo "Complete."
    
    python3 -m ipflakies --log --rerun 3 --verify 3

    for i in $(echo $tuples); do
	Test_filename=$(echo $i | cut -d, -f4)
	Test_classname=$(echo $i | cut -d, -f5)
	Test_funcname=$(echo $i | cut -d, -f6)
	Test_parametrization=$(echo $i | cut -d, -f7)

	if [[ $Test_classname == '' ]]; then
	    if [[ $Test_parametrization == '' ]]; then
		victim=$(grep $Test_filename:: test_list | grep ::$Test_funcname | sort | head -1)
	    else
		victim=$(grep $Test_filename:: test_list | grep ::$Test_funcname | grep -F $Test_parametrization | sort | head -1)
	    fi
	else
	    if [[ $Test_parametrization == '' ]]; then
		victim=$(grep $Test_filename:: test_list | grep ::$Test_classname | grep ::$Test_funcname | sort | head -1)
	    else
		victim=$(grep $Test_filename:: test_list | grep ::$Test_classname | grep ::$Test_funcname | grep -F $Test_parametrization | sort | head -1)
	    fi
	fi

	if [[ -z "$victim" ]]; then
	    continue
	fi

	echo "[ TEST ] $victim"
	
	python3 -m ipflakies -t $victim  --log --rerun 3 --verify 3
    done

    mkdir -p /root/external/ipflakies_result/$project
    mkdir -p /root/external/ipflakies_log/$project

    zip -rq $project.zip ipflakies_result
    mv $project.zip /root/external/ipflakies_result/$project/
    zip -rq $project.zip ipflakies_log
    mv $project.zip /root/external/ipflakies_log/$project/

    deactivate
    cd /root
    mv $project /root/Projects
done

chmod 777 /root/external/*
chmod 777 /root/external/ipflakies_result/*
chmod 777 /root/external/ipflakies_log/*
chmod 777 /root/external/install_log/*
