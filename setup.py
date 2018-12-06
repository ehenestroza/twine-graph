from setuptools import setup, find_packages
import os.path as op


# Put README into long_description
this_directory = op.abspath(op.dirname(__file__))
with open(op.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='twine-graph',
    version='0.0.1',
    description="""A utility for parsing HTML Twine stories and saving
        them into json or graph formats""",
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/ehenestroza/twine-graph',
    author='Enrique Henestroza Anguiano',
    author_email='ehenestroza@gmail.com',
    classifiers=[
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8'
    ],
    packages=find_packages(exclude=['examples', 'tests']),
    install_requires=[
        'beautifulsoup4',
        'graphviz'
    ],
    entry_points={
        'console_scripts': [
            'twine_graph=twine_graph.__main__:main',
        ],
    }
)
