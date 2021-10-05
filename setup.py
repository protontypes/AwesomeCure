from setuptools import setup, find_packages

setup(
    name='sustainbeat',
    version='1.0.0',
    url='https://github.com/protontypes/sustainbeat.git',
    description='Collecting data about open source ecosystem described within awesome lists',
    packages=find_packages(),
    install_requires=['beautifulsoup4', 'markdown', 'pygithub', 'python-dotenv'],
)
