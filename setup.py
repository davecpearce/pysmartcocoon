import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

setup(
    name='pysmartcocoon',
    version='0.5.0', # Should be updated with new versions
    author='Dave Pearce',
    author_email='pearcd2@yahoo.com',
    packages=['pysmartcocoon'],
    url='https://github.com/urbandave/pysmartcocoon',
    license='Open Source',
    long_description=README,
    long_description_content_type="text/markdown",
    description='A simple API to controll SmartCocoon fans from Python.',
    install_requires=[
        'asyncio-mqtt'
    ],
    zip_safe=False
)