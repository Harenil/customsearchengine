from setuptools import setup, find_packages

setup(
    name='searchengine',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'flask',
        'requests',
        'beautifulsoup4',
        # Add other dependencies as needed
    ],
)

# How to run:
# powershell first - be in customsearchenginefolder
# pip install -e .

# powershell second
# $env:FLASK_APP = "searchengine"
# $env:FLASK_DEBUG = "1"
# flask run