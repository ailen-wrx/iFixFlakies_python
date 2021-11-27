base=$(pwd)
outdir=$base/repro/src/idflakies
mkdir -p $outdir
for i in $(cut -d, -f1 repro/src/dataset_final.csv | sort -u); do
    cd /home/user/iFixFlakies_python/Repo
    rm -rf $i
    echo "copying $i.zip"
    cp /home/user/data/Installed_Repositories/$i.zip .
    echo "unzipping $i.zip"
    unzip $i.zip > /dev/null
    rm $i.zip

    if [[ ! -d "$i" ]]; then
	continue
    fi

    
    cd $i

    mkdir -p cache/ipflakies

    source venv/bin/activate
    pip -V
    python3 -m pytest
    pip install ipflakies==0.0.8

    python3 -m ipflakies 

    mkdirs $outdir/$i
    cp -r -f ipflakies_result $outdir/$i
    cp -r -f cache/ipflakies/random_suite $outdir/$i

    cd $base
    rm -rf /home/user/iFixFlakies_python/Repo/$i
done


