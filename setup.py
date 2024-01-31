from setuptools import setup, find_packages

setup(
    name="pylasr_sdk",
    version="0.1.5",
    packages=find_packages(),
    description="""helpers and types for developers
    building programs for the lasr network in python""",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="asmith",
    author_email="as@versatus.io",
    url="https://github.com/versatus/pylasr-sdk",
    install_requires=[],
    python_requires=">=3.6",
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
