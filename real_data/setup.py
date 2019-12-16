from setuptools import setup
from setuptools import find_packages

setup(
    name='desed_real',
    version='1.1.0',
    license="MIT",
    description="DESED dataset utils",
    author="Nicolas Turpault, Romain Serizel, Ankit Shah, Justin Salamon",
    author_email="turpaultn@gmail.com",
    url="https://github.com/turpaultn/DESED",
    install_requires=[
        "dcase-util >= 0.2.5",
        "youtube-dl >= 2019.4.30",
        "pysoundfile >= 0.10.1",
        "numpy >= 1.15.4",
        "pandas >= 0.24.0"
    ],
    packages=find_packages()
)