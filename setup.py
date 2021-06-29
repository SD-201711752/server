from setuptools import setup

setup(
    name="server",
    version='0.0.1',
    author='Diego',
    description='',
    license='GNU',
    install_requires=['flask','requests'],
    entry_points={
        'console_scripts': [
            'server_docker=server:main'
        ]
    }

)
