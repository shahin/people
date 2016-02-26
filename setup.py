from distutils.core import setup

setup(
    name="people",
    version="1.0",
    description="A REST service that stores user and group records.",
    author="Shahin",

    install_requires=[
        'werkzeug<=0.10.4',
        'flask', 
        'flask-sqlalchemy',
        'flask-restful',
    ],
)
