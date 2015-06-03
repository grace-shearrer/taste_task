from distutils.core import setup

description = '''Module for communicating with New Era pump series using a
RS-232 interface'''

setup(
    name='New Era pump interface',
    version='0.7',
    author='Brad Buran',
    author_email='bburan@alum.mit.edu',
    packages=['new_era'],
    url='http://bradburan.com/programs-and-scripts',
    license='LICENSE.txt',
    description='Module for communicating with New Era pump',
    long_description=open('README.txt').read(),
    requires=['pyserial'],
)
