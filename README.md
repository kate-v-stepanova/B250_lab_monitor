# B250_lab_monitor
Web interface to monitor the current lab projects

## Installation

```
git clone
conda create -n b250 python=3
source activate b250
pip install -r requirements.txt
export FLASK_APP=main.py
export FLASK_ENV=development
flask run --host 0.0.0.0 --port 80
```

## Database

```
cd ~/PycharmProjects/B250_lab_monitor
redis-server
```

-------------

## Users management

`python ./utils/user_management.py --help`:

```
Usage: user_management.py [OPTIONS] COMMAND [ARGS]...

Options:
  --host TEXT
  --port TEXT
  --help       Show this message and exit.

Commands:
  create-user
  delete-user
```

Create user: `python utils/user_management.py --host 172.22.54.5 create-user`

```
Username: kate@a.a
Password:
Repeat password:
```

Delete user: `python utils/user_management.py delete-user kate`
