from distutils.core import setup
import sys, os

DATA_FILES = ['README', 'LICENSE']

ASTEROID_PNGS = ['large.png', 'medium.png', 'small.png', 'ship.png']
INVASION_PNGS = ['ship.png', 'alien.png']

TUTORIALS = ['examples/tutorial/'+t for t in os.listdir('examples/tutorial/')]
DATA_FILES += TUTORIALS

setup(
	name='pyrge', 
	version='0.6',
	author="Michael Potter",
	author_email="michael@potterpcs.net",
	url="http://github.com/momikey/pyrge",
	packages = ['pyrge',
                    'pyrge.examples.asteroid',
                    'pyrge.examples.invasion'],
	package_dir = {'pyrge': ''},
	package_data = {'pyrge': DATA_FILES, 
		'pyrge.examples.asteroid': ['*.png'],
		'pyrge.examples.invasion': ['*.png']},
	requires=['pygame (>= 1.9)'])

