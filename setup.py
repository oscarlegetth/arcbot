from setuptools import setup, find_packages

setup (
    name='ArcBot',
    version='0.0.1',
    packages=find_packages(where='ArcBot'),
    install_requires=[
        'python-dotenv', 
        'twitchio', 
        'osrsbox', 
        'asyncio'
    ],
)
