from setuptools import setup
from setuptools import find_packages

setup(
    name='desed',
    version='1.1.0',
    description="DESED dataset utils",
    author="Nicolas Turpault, Romain Serizel, Ankit Shah, Justin Salamon",
    author_email="turpaultn@gmail.com",
    url="https://github.com/turpaultn/DESED",
    license='MIT',
    install_requires=[
        "scaper >= 1.0.3",
        "numpy >= 1.15.4",
        "pandas >= 0.24.0",
        "dcase-util >= 0.2.5",
        "youtube-dl >= 2019.4.30",
        "soundfile >= 0.10.1",
    ],
    packages=find_packages()
)