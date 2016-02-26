# people

A web application to perform operations on user records. For the spec, see https://gist.github.com/jakedahn/3d90c277576f71d805ed.

## Requirements

* Python 2.7
* sqlite3

## Install

```bash
git clone https://github.com/shahin/people.git
cd people
pip install -e.
```

## Run Tests

```bash
python tests/tests.py
```

## Initialize and Run Server

```bash
python db_create.py
python people/app.py
```
