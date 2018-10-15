# Always prefer setuptools over distutils
from setuptools import setup, find_packages

setup(
    name='twine-graph',
    version='0.0.1',
    description="""A utility for parsing HTML Twine stories and saving
        them into json or graph formats""",
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
    # For example, the following would provide a command called `sample` which
    # executes the function `main` from this package when invoked:
    entry_points={  # Optional
        'console_scripts': [
            'twine_graph=twine_graph.__main__:main',
        ],
    }
)
