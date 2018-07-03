from setuptools import setup

def readme():
    with open('README.md') as f:
        return f.read()

setup(name='stfile',
      version='0.1',
      description='File System with semantics',
      long_description=readme(),
      classifiers=[
        'Programming Language :: Python'
      ],
      keywords='semantics file system RDF OWL',
      url='https://github.com/pabloriutort/stfile',
      author='Pablo Riutort',
      author_email='pablo.riutort@gmail.com',
      license='MIT',
      packages=['stfile'],
      zip_safe=False,
      include_package_data=True,
      entry_points = {
        'console_scripts': ['stf=stfile.command_line:main'],
        }
      )
