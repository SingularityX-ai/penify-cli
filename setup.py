from setuptools import setup, find_packages

setup(
    name='doc_gen_hook',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'GitPython',
        'requests'
    ],
    entry_points={
        'console_scripts': [
            'doc_gen_hook=doc_gen_hook.main:main',  # This forces the name to use underscores
        ],
    },
    author='Suman Saurabh',
    description='A post-commit hook that analyzes modified files via an API and commits changes automatically.',
    url='https://github.com/SingualrityX-ai/doc_gen_hook',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
