from setuptools import setup, find_packages

setup(
    name="penify-hook",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "requests",
    ],
    entry_points={
        "console_scripts": [
            "penify-hook=penify_hook.main:main",
        ],
    },
    author="Popin Bose Roy",
    author_email="your.email@example.com",
    description="A post-commit hook that sends modified files and their contents to an API.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/penify-hook",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
