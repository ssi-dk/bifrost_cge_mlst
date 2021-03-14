from setuptools import setup, find_packages

setup(
    name='bifrost_cge_mlst',
    version='v2_2_1',
    description='Datahandling functions for bifrost (later to be API interface)',
    url='https://github.com/ssi-dk/bifrost_cge_mlst',
    author="Kim Ng, Martin Basterrechea",
    author_email="kimn@ssi.dk",
    packages=find_packages(),
    install_requires=[
        'bifrostlib >= 2.1.9',
    ],
    package_data={"bifrost_cge_mlst": ['config.yaml', 'pipeline.smk']},
    include_package_data=True
)
