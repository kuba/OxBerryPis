import os

from setuptools import setup
from setuptools import find_packages


version = '0.1'

# Package requirements
install_requires = [
    'nose',
    'coverage',
    'protobuf',
    'pyzmq',
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
    url='https://github.com/kuba/oxberrypis',
    license='',
    packages=find_packages(exclude=['tests*',]),
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    entry_points = {
        'console_scripts': [
            'oxberrypis-channel-parser = oxberrypis.scripts.parsers:channel_parser',
            'oxberrypis-controller = oxberrypis.scripts.controller:main',
            'oxberrypis-rpi = oxberrypis.scripts.rpi:main',
            'oxberrypis-vis-test = oxberrypis.scripts.vis_test:main',
        ],
    },
)
