from setuptools import setup

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(name='tao.bb',
      version='1.0',
      description='tao.bb short url',
      author='T.G.',
      author_email='farmer1992@gmail.com',
      url='http://tao.bb',
      install_requires=required,
     )
