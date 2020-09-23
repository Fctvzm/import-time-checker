# import-time-checker

Script that measures execution time of importing modules in project

## How to run script

Always give absolute path to project

```python
python execute_imports.py -d /home/user/dir_project
```
Also you can specify path to enviroment activation file

```python
# Example
python execute_imports.py -d /home/user/dir_project -e /home/user/.env/bin/activate
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
# shows modules that unable to import due to incorrect path or module does not exist
```
