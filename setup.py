import os
from setuptools import setup
from setuptools import find_packages


def package_file(fname):
    return os.path.relpath(os.path.join(os.path.dirname(__file__), fname))


setup(
    name='desed',
    version='1.2.3',
    description="DESED dataset utils",
    author="Nicolas Turpault, Romain Serizel, Ankit Shah, Justin Salamon",
    author_email="turpaultn@gmail.com",
    url="https://github.com/turpaultn/DESED",
    license='MIT',
    package_dir={"": package_file("desed")},
    packages=find_packages(package_file("desed")),
    install_requires=[
        "scaper >= 1.3.5",
        "numpy >= 1.15.4",
        "pandas >= 0.24.0",
        "dcase-util >= 0.2.11",
        "youtube-dl >= 2019.4.30",  # Better with conda install and conda-forge channel
        "soundfile >= 0.10.1",
        "jams >= 0.3.4",
        "tqdm >= 4.29.1",
        "requests >= 2.21.0"
    ]
)
