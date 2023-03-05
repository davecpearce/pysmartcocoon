import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

setup(
    name='pysmartcocoon',
    version='0.5.4', # Should be updated with new versions
    author='Dave Pearce',
    author_email='davepearce@live.com',
    packages=['pysmartcocoon'],
    url='https://github.com/davecpearce/pysmartcocoon',
    license='Open Source',
    long_description=README,
    long_description_content_type="text/markdown",
    description='An API to control SmartCocoon fans from Python.',
    install_requires=[
        'asyncio-mqtt'
    ],
    zip_safe=False
)