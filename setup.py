from setuptools import setup, find_packages

setup(
    name = "rdflib-django",
    version = "1.0",
    license = 'MIT',
    description = "Store implementation for RDFlib using Django models as its backend",
    author = 'Yigal Duppen',
    packages = find_packages('src'),
    package_dir = {'': 'src'},
    install_requires = ['setuptools', 'rdflib'],
)
