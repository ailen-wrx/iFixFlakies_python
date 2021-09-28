#bash clone.sh victims_brittles.csv Repo

dataset=$1
repo_dir=$2

base_url=$(pwd)
mkdir -p $repo_dir/$project
for i in $(cut -d, -f1,2 $dataset | uniq | sed '1d'); do
    project=$(echo $i | cut -d, -f1)
    url=$(echo $i | cut -d, -f2)

    echo cloning $project starttime: $(date) >> log_clone
    cd $repo_dir
    git clone $url --depth=1

    cd $repo_dir/$project
    sha=$(grep $project, $dataset | cut -d, -f3 | head -1)
    echo Switching to $sha...
    git remote set-branches origin $sha
    git fetch --depth 1 origin $sha
    git checkout $sha
    
    cd $base_url
done
