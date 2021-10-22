

base_url=$(pwd)

rm $base_url/projects_to_reinstall
rm $base_url/projects_installed

cd Repo

cnt=0
cnt1=0
for project in `ls`;
do
    
    cd $base_url/Repo/$project


    dep=$(grep "ModuleNotFoundError:" test_list | sed 's/E   ModuleNotFoundError: No module named //g' | sed 's/'\''//g' | uniq)

    if [[ "$dep" != "" ]]; then
	echo $project >> $base_url/projects_to_reinstall
	let cnt+=1

	# source venv/bin/activate
	# pip3 install $dep
	# python -m pytest --collect-only -q > test_list
	# deactivate

	continue
    fi

    echo $project >> $base_url/projects_installed
    let cnt1+=1
    
done

echo $cnt projects to reinstall
echo $cnt1 projects installed

rm -rf ~/.cache/pip/http
