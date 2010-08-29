from distutils.core import setup

ASTEROID_PNGS = ['large.png', 'medium.png', 'small.png', 'ship.png']
INVASION_PNGS = ['ship.png', 'alien.png']

setup(
	name='pyrge', 
	version='0.1',
	author="Michael Potter",
	author_email="michael@potterpcs.net",
	url="http://github.com/momikey/",
	packages = ['pyrge', 'pyrge.examples.asteroid', 'pyrge.examples.invasion'],
	package_dir = {'pyrge': ''},
	data_files = [('examples/asteroid', ['examples/asteroid/'+a for a in ASTEROID_PNGS]),
		('examples/invasion', ['examples/invasion/'+i for i in INVASION_PNGS])],
	requires=['pygame (>= 1.9)'])

