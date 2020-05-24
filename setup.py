from setuptools import setup

setup(
	name='chika',
	version='0.1',
	include_package_data=True,
	url='https://github.com/TheNovi/Chika',
	license='MIT',
	author='TheNovi',
	author_email='jakub.novi.novacek@gmail.com',
	description='',
	packages=['chika'],
	# package_data={'': ['conf.json']}, # NOSONAR
	install_requires=['PyInstaller'],
	entry_points={
		'console_scripts': ['chika=chika.__main__:main'],
	},
	classifiers=[
		'Development Status :: 4 - Beta',
		'Intended Audience :: Developers',
		'Topic :: Software Development :: Build Tools',
		'License :: OSI Approved :: MIT License',
		'Programming Language :: Python :: 3.8',
	],
)

# pip install .
