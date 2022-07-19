from setuptools import setup, find_packages

setup (
    name='ArcBot',
    version='0.0.8',
    packages=find_packages(where='ArcBot'),
    install_requires=[
        'python-dotenv', 
        'twitchio', 
        'osrsbox', 
        'asyncio',
        'requests'
    ],
)
