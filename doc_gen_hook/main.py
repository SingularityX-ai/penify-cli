import sys
from .analyzer import DocGenHook

def main():
    if len(sys.argv) != 3:
        print("Usage: doc_gen_hook <repo_path> <api_url>")
        sys.exit(1)

    repo_path = sys.argv[1]
    api_url = sys.argv[2]

    analyzer = DocGenHook(repo_path, api_url)
    analyzer.run()

if __name__ == "__main__":
    main()
