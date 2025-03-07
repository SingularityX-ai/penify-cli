from setuptools import setup, find_packages

setup(
    name="penifycli",  # Changed from "penifycli" to a more unique name
    version="0.2.2",
    packages=['penify_hook'],
    install_requires=[
        "requests",
        "tqdm",
        "GitPython",
        "colorama",
        "litellm",
        "jira"
    ],
    entry_points={
        "console_scripts": [
            "penifycli=penify_hook.main:main",  # Command name remains the same
        ],
    },
    author="Suman Saurabh",
    author_email="ss.sumansaurabh92@gmail.com",
    description="A penify cli tool to generate Documentation, Commit-summary.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/SingularityX-ai/penifycli",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)