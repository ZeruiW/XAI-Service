from setuptools import setup, find_packages

setup(
    name="xai_sdk",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'requests',
        'pyyaml',
        'tqdm',
    ],
    package_data={
        'xai_sdk': ['sdk_config.yaml'],  # include the configuration file in the package
    },
    # Metadata
    author="Hari Vinayak Sai Kandikattu",
    author_email="harivinayaksai.kandikattu@mail.concordia.ca",
    description="SDK Gateway for XAI",
    long_description=open('README.md').read(),
    url="https://github.com/hari-vinayak/XAI-Service",  # Replace with the URL to the SDK's repository
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ],
)
