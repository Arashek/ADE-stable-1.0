from setuptools import setup, find_packages

setup(
    name='ade_backend',
    version='1.0',
    packages=find_packages(),
    install_requires=[
        'fastapi>=0.68.0',
        'uvicorn>=0.15.0',
        'python-dotenv>=0.19.0'
    ],
)
