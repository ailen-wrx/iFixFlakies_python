#bash clone.sh victims_brittles.csv Repo

dataset=$1
repo_dir=$2

base_url=$(pwd)
mkdir -p $repo_dir/$project
rm $base_url/latest_repo_dirs.csv
for i in $(cut -d, -f1,2 $dataset | uniq | sed '1d'); do
    project=$(echo $i | cut -d, -f1)
    url=$(echo $i | cut -d, -f2)

    echo cloning $project starttime: $(date) >> log_clone

    cd $repo_dir
    echo "" > new-t
    git clone $url --depth=1
    latest_name=$(find . -mindepth 1 -maxdepth 1 -newer new-t | rev | cut -d'/' -f1 | rev)
    
    echo $latest_name
    echo $project,$latest_name >> $base_url/latest_repo_dirs.csv

    cd $repo_dir/$project
    sha=$(grep $project, $dataset | cut -d, -f3 | head -1)
    echo Switching to $sha...
    git remote set-branches origin $sha
    git fetch --depth 1 origin $sha
    git checkout $sha
    
    cd $base_url
done
