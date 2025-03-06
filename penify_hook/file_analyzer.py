import os
from git import Repo
from .api_client import APIClient
from tqdm import tqdm
from colorama import Fore, Style, init
import logging

# Initialize colorama for cross-platform colored terminal output
init(autoreset=True)

# Set up logger
logger = logging.getLogger(__name__)

class FileAnalyzerGenHook:
    def __init__(self, file_path: str, api_client: APIClient):
        self.file_path = file_path
        self.api_client = api_client
        self.supported_file_types = set(self.api_client.get_supported_file_types())

    def process_file(self, file_path):
        """Process a file by reading its content and sending it to an API for
        processing.

        This function checks if the provided file has a supported extension. If
        the file is valid, it reads the content of the file and sends it to an
        API client for further processing. If the API responds successfully, the
        original file content is replaced with the response.

        Args:
            file_path (str): The relative path to the file that needs to be processed.

        Returns:
            bool: True if the file was processed successfully, False otherwise.
        """
        file_abs_path = os.path.join(os.getcwd(), file_path)
        file_extension = os.path.splitext(file_path)[1].lower()

        if not file_extension:
            logger.info(f"File {file_path} has no extension. Skipping.")
            return False
        
        file_extension = file_extension[1:]  # Remove the leading dot

        if file_extension not in self.supported_file_types:
            logger.info(f"File type {file_extension} is not supported. Skipping {file_path}.")
            return False

        with open(file_abs_path, 'r') as file:
            content = file.read()

        modified_lines = [i for i in range(len(content.splitlines()))]
        
        # Send data to API
        response = self.api_client.send_file_for_docstring_generation(file_path, content, modified_lines)
        
        if response is None:
            return False
            
        if response == content:
            logger.info(f"No changes needed for {file_path}")
            return False
            
        # If the response is successful, replace the file content
        with open(file_abs_path, 'w') as file:
            file.write(response)
        logger.info(f"Updated file {file_path} with generated documentation")
        return True

    def run(self):
        """Run the post-commit hook.

        This method executes the post-commit hook by processing a specified
        file. It attempts to process the file located at `self.file_path`. If an
        error occurs during the processing, it catches the exception and prints
        an error message indicating that the file was not processed. The method
        displays a progress bar and colored output to provide visual feedback on
        the processing status.
        """
        logger.info(f"{Fore.CYAN}Starting file analysis processing{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Starting file analysis for {Fore.YELLOW}{self.file_path}{Style.RESET_ALL}")
        
        # Create a progress bar with appropriate stages
        stages = ["Validating file", "Reading content", "Processing", "Writing changes"]
        
        with tqdm(total=len(stages), desc=f"{Fore.CYAN}Processing file{Style.RESET_ALL}", 
                 unit="step", ncols=80, ascii=True) as pbar:
            try:
                # Validate and read file
                pbar.set_description(f"{Fore.CYAN}Validating file{Style.RESET_ALL}")
                file_display = f"{Fore.YELLOW}{self.file_path}{Style.RESET_ALL}"
                print(f"\n{Fore.BLUE}Processing file: {file_display}")
                pbar.update(1)
                
                # Process file
                pbar.set_description(f"{Fore.CYAN}Processing{Style.RESET_ALL}")
                pbar.update(1)
                
                result = self.process_file(self.file_path)
                
                # Update progress
                pbar.set_description(f"{Fore.CYAN}Writing changes{Style.RESET_ALL}")
                pbar.update(2)  # Skip to completion
                
                # Display appropriate message based on result
                if result:
                    print(f"  {Fore.GREEN}✓ Documentation updated for {file_display}{Style.RESET_ALL}")
                else:
                    print(f"  {Fore.WHITE}○ No changes needed for {file_display}{Style.RESET_ALL}")
                    
            except Exception as e:
                error_msg = f"Error processing file [{self.file_path}]: {str(e)}"
                logger.error(error_msg)
                print(f"  {Fore.RED}✗ {error_msg}{Style.RESET_ALL}")
                # Ensure progress bar completes even on error
                remaining = len(stages) - pbar.n
                if remaining > 0:
                    pbar.update(remaining)
                    
        print(f"\n{Fore.CYAN}✓ File analysis complete{Style.RESET_ALL}")
