from distutils.core import setup

setup(
    name="people",
    version="1.0",
    description="A REST service that stores user and group records.",
    author="Shahin",

    install_requires=[
        'werkzeug<=0.10.4', # 0.11.4 has logging issues, see werkzeug #...
        'flask', 
        'flask-sqlalchemy',
        'flask-restful',
    ],
)
