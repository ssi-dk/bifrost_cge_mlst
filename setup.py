from setuptools import setup, find_namespace_packages

setup(
    name='bifrost_cge_mlst',
    version='2.2.10',
    description='MLST component for Bifrost',
    url='https://github.com/ssi-dk/bifrost_cge_mlst',
    author='Kim Ng',
    author_email='kimn@ssi.dk',
    license='MIT',
    packages=find_namespace_packages(),
    install_requires=[
        'bifrostlib >= 2.1.9',
        'biopython>=1.77'
    ],
    python_requires='>=3.6',
    package_data={'bifrost_cge_mlst': ['config.yaml', 'pipeline.smk']},
    include_package_data=True
)