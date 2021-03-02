from setuptools import setup

setup(
    packages=['aiogram_tools'],
    setup_requires=['pbr'], pbr=True,
    install_requires=[
        'aiogram>=2.11.2',
    ],
)
