output_dir=$1
base_url=$(pwd)

cd $output_dir

for i in $(ls); do
    cd $i
    if [[ ! -e "$i.zip" ]]; then
        echo $i
        cd -
        continue
    fi
    unzip -q $i.zip > /dev/null
    rm $i.zip
    cd -
done

cd $base_url
