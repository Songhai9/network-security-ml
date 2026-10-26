'''
The setup.py file is an essential part of packaging and
distributing Python projects. It is used by setuptools to
define the configuration of the project
'''

from setuptools import find_packages,setup
from typing import List


def get_requirements()->List[str]:
    '''
    This function will return list of requirements
    '''
    requirement_lst: List[str] = []
    try:
        with open('requirements.txt', 'r') as file:
                  #read lines from the line
                  lines = file.readlines()
                  for line in lines:
                        requirement = line.strip()
                        if requirement and requirement != '-e .':
                              requirement_lst.append(requirement)
    except FileNotFoundError:
          print('No requirements file found')

    return requirement_lst


setup(
      name='networksecurity',
      version='0.1.0',
      author='Oumarou MAIGA',
      author_email='oumar.s.m@outlook.fr',
      packages=find_packages(),
      install_requires=get_requirements()
)