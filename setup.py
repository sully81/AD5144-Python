from setuptools import setup, find_packages

setup(
    name='ad5144',
    version='0.1.0'
    description='Python driver for AD5144 digital potentiometer',
    author='Patrick Sullivan',
    url='https://github.com/sully81/AD5144-Python',
    packages=find_packages(),
    install_requires=['smbus2'],
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
