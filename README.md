# python
```shell
# install python dependencies
virtualenv -p python3 venv
source venv/bin/activate
pip3 install -r requirements.txt

# save python dependencies
pip freeze > requirements.txt
```

### Type checking
```
mypy /path/to/script.py
```
