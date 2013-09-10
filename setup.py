from setuptools import setup
import os

with open(os.environ['OPENSHIFT_REPO_DIR'] + 'requirements.txt') as f:
    required = f.read().splitlines()

setup(name='tao.bb',
      version='1.0',
      description='tao.bb short url',
      author='T.G.',
      author_email='farmer1992@gmail.com',
      url='http://tao.bb',
      install_requires=required,
     )
