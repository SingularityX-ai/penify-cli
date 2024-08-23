import sys
from .analyzer import DocGenHook

def main():
    """Run the main application for the documentation generation hook.

    This function serves as the entry point for the application. It checks
    the command-line arguments to ensure that exactly two arguments are
    provided: the repository path and the API URL. If the arguments are not
    correct, it prints a usage message and exits the program. If the
    arguments are valid, it initializes a `DocGenHook` instance with the
    provided arguments and calls its `run` method to start the documentation
    generation process.
    """

    if len(sys.argv) != 3:
        print("Usage: doc_gen_hook <repo_path> <api_url>")
        sys.exit(1)

    repo_path = sys.argv[1]
    api_url = sys.argv[2]

    analyzer = DocGenHook(repo_path, api_url)
    analyzer.run()

if __name__ == "__main__":
    main()
