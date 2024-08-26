from setuptools import setup, find_packages

setup(
    name="penify-cli",
    version="0.1.2",  # Increment the version number
    packages=['penify_hook'],  # Explicitly include the penify_hook package
    install_requires=[
        "requests",
        "tqdm",
        "GitPython"
    ],
    entry_points={
        "console_scripts": [
            "penify-cli=penify_hook.main:main",
        ],
    },
    author="Suman Saurabh",
    author_email="ss.sumansaurabh92@gmail.com",
    description="A penify cli tool to generate Documentation, Commit-summary and  Hooks to automate git workflows.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/SingularityX-ai/penify-cli",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)