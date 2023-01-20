from setuptools import setup, find_packages

setup(
    name='xai_backend_central_dev',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        "tinydb",
        "python-dotenv",
        "Flask >= 2.2",
        "flask-cors",
        "pymongo",
        "codecarbon",
        "torch",
        "torchvision",
        "torchaudio"
    ],
)
