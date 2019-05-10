# B250 Project Monitor

## Installation

```
git clone
conda create -n b250 python=3
source activate b250
pip install -r requirements.txt
mongod --config /usr/local/etc/mongod.conf
export FLASK_APP=main.py
export FLASK_ENV=development
flask run --host 0.0.0.0 --port 80
```

