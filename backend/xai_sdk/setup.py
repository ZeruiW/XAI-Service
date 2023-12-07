from setuptools import setup, find_packages

setup(
    name="xai_sdk",
    version="0.5",
    packages=find_packages(),
    install_requires=[
        'requests',
        'pyyaml',
        'tqdm',
    ],
    # Metadata
    author="Hari Vinayak Sai Kandikattu",
    author_email="harivinayaksai.kandikattu@mail.concordia.ca",
    description="SDK Gateway for XAI",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url="https://github.com/hari-vinayak/XAI-Service", 
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ],
)
