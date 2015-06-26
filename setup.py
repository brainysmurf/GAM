"""
NOTE: I do not have a windows machine, so cannot test py2exe stuff
Anyway, I am not sure it needs it anymore anyway, as click takes care of a lot of windows problems 
that often happens with python

This is a more standard setuptools config, anyway
Can put it into a virtualenv, essential if we want to be able to import stuff
"""

from distutils.core import setup
setup(
    name = "gam",
    description = "",
    author = "",
    author_email = "",
    keywords = [],
    packages=['cli', 'gdata', 'googleapiclient', 'oauth2client', 'httplib2', 'passlib'],
    entry_points='''
        [console_scripts]
        gami=cli.cli:cli
    ''',
    install_requires = ['click', 'colorama'],
    #install_requires = ['gdata', 'google-api-python-client==1.4.0', 'oauth2client==1.4.7', 'httplib2==0.9', 'passlib==1.6.2']


    # classifiers = [
    #     "Programming Language :: Python",
    #     "Programming Language :: Python :: 3",
    #     "Development Status :: 4 - Beta",
    #     "Intended Audience :: Developers",
    #     "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
    #     "Operating System :: OS Independent",
    #     ],
    long_description = """\
TODO: DESCRIBE THIS!


"""
)

# from distutils.core import setup
# import py2exe, sys, os

# sys.argv.append('py2exe')

# setup(
#   console = ['gam.py'],

#   zipfile = None,
#   options = {'py2exe': 
#               {'optimize': 2,
#                'bundle_files': 3,
#                'includes': ['passlib.handlers.sha2_crypt'],
#                'dist_dir' : 'gam'}
#             }
#   )
