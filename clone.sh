#bash clone.sh victims_brittles.csv Repo

dataset=$1
project=$2

for i in $(cut -d, -f2 $dataset | uniq | sed '1d'); do
    echo cloning $project starttime: $(date) > log_clone
    cd $project
    git clone $i --depth=1
    cd -
done
