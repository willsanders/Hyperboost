# from os import path
from setuptools import setup

import hyperboost

# Get the long description from the README file
# here = path.abspath(path.dirname(__file__))
# with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
#     long_description = f.read()

with open('requirements.txt') as fh:
    requirements = fh.read()
requirements = requirements.split('\n')
requirements = [requirement.strip() for requirement in requirements]

print(requirements)
setup(
    name='hyperboost',
    version=hyperboost.__version__,
    packages=['hyperboost'],
    url='https://github.com/Yatoom/hyperboost',
    license='',
    author='Jeroen van Hoof',
    author_email='jmapvhoof@gmail.com',
    description='A hyperparameter optimization tool based on SMAC and gradient boosting.',
    # long_description=long_description,
    install_requires=requirements
)
