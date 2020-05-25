import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

NAME = 'busylight'

setuptools.setup(
    name=NAME,
    version='0.0.2',
    author='Anthony Lannutti',
    author_email='lannuttia@gmail.com',
    description='An Azure IoT busy light',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/lannuttia/busylight-py',
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
    install_requires=[
        'gpiozero~=1.5',
        'azure-iot-device~=2.1',
    ]
)
