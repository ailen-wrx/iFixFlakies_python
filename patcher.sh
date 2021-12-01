cd AST_copytest

bash can_copy_work.sh $(pwd)/../repro/src/cleaners.csv $(pwd)/../repro/patch_victims.csv $(pwd)/../Repo 1

bash handle_brittle.sh $(pwd)/../repro/src/state_setters.csv $(pwd)/../repro/patch_brittles.csv $(pwd)/../Repo 1

cd -
