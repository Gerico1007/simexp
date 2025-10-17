from setuptools import setup, find_packages

setup(
    name='simexp',
    version = "0.3.10",
    packages=find_packages(
        include=["simexp", "test-*.py"], exclude=["test*log", "*test*csv", "*test*png"]
    ),
    #package_dir={'': 'src'},
    install_requires=[
        'requests',
        'beautifulsoup4',
        'pyperclip',
        'pyyaml',
        'fetcher',
        'playwright>=1.40.0'
    ],
    entry_points={
        'console_scripts': [
            'simexp=simexp:main',
        ],
    },
    author='gerico1007',
    author_email='gerico@jgwill.com',
    description='A web content extractor and archiver for simplenote',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/gerico1007/simexp',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)