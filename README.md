# import-time-checker

Script that measures execution time of importing modules in project

## How to run script

Always give absolute path to project

```python
python execute_imports.py -d /home/user/dir_project
```
## Output

in ascending order of execution 
```python
scipy 0.233 s
joblib 0.255 s
matplotlib 0.271 s
...
Total time for importing: 18.524
modules that cannot import: ['pandas', 'utils.foo']
# shows modules that unable tp import due to incorrect path or module does not exist
```
