## Setup
- python 3.8.10


## ast_test
A project with 2 demo tests:
- `test_sum.py`
- `test_twoassertions.py`

## copy_test.py
A script to copy one test(cleaner) into another(victim).
- Usage: 
```
python3 coy_test.py cleaner_path victim_path combination_path

e.g.:
python3 copy_test.py ast_test/test_sum.py ast_test/test_twoassertions.py combination.py
```
- The combination of the 2 tests will be saved in `combination_path`.

## unparse.py
To generate source from the AST.