import setuptools
import os

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.md')).read()


version = '1.0.0'

setuptools.setup(
    name='pycp2110',
    version=version,
    description='Silabs CP2110 USB HID to UART bridge library',
    long_description=README,
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
    ],
    keywords='',
    author='Robert Ginda',
    author_email='rginda@gmail.com',
    url='https://github.com/rginda/pycp2110',
    license='MIT',
    zip_safe=True,
    packages=setuptools.find_packages(),
    install_requires=['hid>=1.0.1'],
)
