from hooks.precommit import PrecommitHook

def main():
    API_URL = "http://localhost:8000/api"  # Replace with your actual API URL
    hook = PrecommitHook(API_URL)
    hook.run()

if __name__ == "__main__":
    main()
