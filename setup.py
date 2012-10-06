import os
from setuptools import setup, find_packages

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name = "rdflib-django",
    version = "0.2",
    url = "http://github.com/publysher/rdflib-django",
    license = 'MIT',
    description = "Store implementation for RDFlib using Django models as its backend",
    long_description = read('README.rst'),
    keywords = 'django rdf rdflib store', 

    author = 'Yigal Duppen',
    author_email = 'yigal@publysher.nl',

    packages = find_packages('src'),
    package_dir = {'': 'src'},
    zip_safe = True,

    install_requires = ['rdflib>=3.2.1'],

    classifiers = [
        'Development Status :: 3 - Alpha',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)