# Penify-cli

Penify-cli is a Git post-commit hook that automatically generates docstrings for modified functions and classes in your codebase. It integrates with a remote API to analyze the changes and generate documentation, helping developers maintain high-quality, consistent documentation across their projects.

## 1. Installing Penify-cli

To install the `penify-cli` package, follow these steps:

1. **Install the Penify-cli Package:**

   First, make sure to install the `penify-cli` package via pip (replace `penify-cli` with the correct package name):

   ```bash
   pip install penify-cli
   ```

## 2. Adding Environment Variable PENIFY_API_TOKEN

To use Penify-cli, you need an API token. This token can be obtained from the Penify dashboard.

1. **Obtain Your API Token:**

   Go to [dashboard.penify.dev](https://dashboard.penify.dev) and log in. Navigate to the API section and generate your API token.

2. **Set Your API Token as an Environment Variable:**

   Add the token to your environment variables for easier usage:

   ```bash
   export PENIFY_API_TOKEN=<YOUR_API_TOKEN>
   ```

   Replace `<YOUR_API_TOKEN>` with your actual API token. This environment variable will be used automatically if you do not provide a token as a command-line argument.

## 3. Help

To see the help options for Penify-cli, you can use the following command:

```bash
penify-cli --help
```

This will display all available commands and options for using Penify-cli.

## 4. Usage

### 4.1 Using Simple Command (in a GIT enabled Repo)

You can use Penify-cli to track Git changes and generate documentation for only the modified lines:

```bash
penify-cli -gf <GIT_FOLDER_PATH>
```

This command will analyze the specified file, generate docstrings for the modified functions and classes, and update the files. If nothing is provided, it will take the default directory.

### 4.2 Git Hook

Penify-cli can be configured as a Git post-commit hook. Once set up, it will automatically generate documentation for any modifications made in your repository after each commit.

#### **Configuring the Post-Commit Hook:**

1. **Install the Post-Commit Hook:**

   Navigate to the root directory of your Git repository and run:

   ```bash
   penify-cli --install -gf <GIT_FOLDER_PATH>
   ```

   Replace `<GIT_FOLDER_PATH>` with the path to the folder containing your Git repository. This command will install the post-commit hook.

2. **How It Works:**

   After installation, every time you make a commit, the post-commit hook will trigger and automatically generate and update docstrings for any modified functions and classes in the latest commit.

3. **Example:**

   ```bash
   git commit -m "Updated some functions"
   ```

   After this commit, Penify-cli will run, analyze the modified files, generate the necessary docstrings, and update the files automatically.

4. **Uninstalling the Post-Commit Hook:**

   To remove the post-commit hook, use:

   ```bash
   penify-cli --uninstall -f <GIT_FOLDER_PATH>
   ```

### 4.3 Generating Documentation for a Full Repository

Penify-cli can generate documentation for all files in a repository, regardless of whether Git is installed or not:

```bash
penify-cli -cf <COMPLETE_FOLDER_PATH>
```

This command will scan the specified folder and generate docstrings for all files within it.

### 4.4 Generating Documentation for a Single File

If you want to generate docstrings for a specific file, you can use:

```bash
penify-cli -l <FILE_PATH>
```

This will analyze the file, generate the required docstrings for all functions and classes, and update the file.