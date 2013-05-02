import os
from setuptools import setup

version = '0.1'

# Package requirements
install_requires = [
    'nose',
    'coverage',
]


def desc(*filenames):
    """Create long description."""
    here = os.path.abspath(os.path.dirname(__file__))

    def try_read(name):
        path = os.path.join(here, name+'.rst')

        try:
            f = open(path, 'r')
        except IOError:
            return ''
        else:
            return f.read()

    d = map(try_read, filenames)
    return '\n\n'.join(d)

setup(
    name='OxBerryPis',
    version=version,
    description="Process stock exchage data using a cluster of Raspberry Pis.",
    long_description=desc('README'),
    classifiers=[
        'Development Status :: 1 - Planning',
        'Operating System :: Unix',
        'Programming Language :: Python :: 2.7',
        'Topic :: Office/Business :: Financial',
        'Topic :: System :: Clustering',
        'Topic :: System :: Distributed Computing',
        'Topic :: System :: Networking',
    ],
    keywords='raspberry pi cluster stock',
    author='Group 8',
    author_email='oxberrypis@googlegroups.com',
    url='https://github.com/expipiplus1/oxberrypis',
    license='',
    packages=['oxberrypis'],
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    entry_points = {
        'console_scripts': [
            'oxberrypis-parser = oxberrypis.parsing.parsers:main',
        ],
    },
)
