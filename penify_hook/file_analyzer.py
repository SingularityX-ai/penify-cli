import os
import sys
from git import Repo
from tqdm import tqdm
import time

from penify_hook.base_analyzer import BaseAnalyzer
from penify_hook.utils import get_repo_details, recursive_search_git_folder
from .api_client import APIClient
import logging
from .ui_utils import (
    format_highlight, print_info, print_success, print_warning, print_error,
    print_status, create_stage_progress_bar,
    update_stage, format_file_path
)

# Set up logger
logger = logging.getLogger(__name__)

class FileAnalyzerGenHook(BaseAnalyzer):
    def __init__(self, file_path: str, api_client: APIClient):
        self.file_path = file_path
        super().__init__(file_path, api_client)
        


    def process_file(self, file_path, pbar):
        """Process a file by reading its content and sending it to an API for
        processing.

        This function checks if the provided file has a supported extension. If
        the file is valid, it reads the content of the file and sends it to an
        API client for further processing. If the API responds successfully, the
        original file content is replaced with the response.

        Args:
            file_path (str): The relative path to the file that needs to be processed.
            pbar (tqdm): Progress bar to update during processing.

        Returns:
            bool: True if the file was processed successfully, False otherwise.
        """
        file_abs_path = os.path.join(os.getcwd(), file_path)
        file_extension = os.path.splitext(file_path)[1].lower()
        
        # --- STAGE 1: Validating ---
        update_stage(pbar, "Validating")        
        if not file_extension:
            logger.info(f"File {file_path} has no extension. Skipping.")
            return False
        
        file_extension = file_extension[1:]  # Remove the leading dot

        if file_extension not in self.supported_file_types:
            logger.info(f"File type {file_extension} is not supported. Skipping {file_path}.")
            return False

        # Update progress bar to indicate we're moving to next stage
        pbar.update(1)
        
        # --- STAGE 2: Reading content ---
        update_stage(pbar, "Reading content")        
        try:
            with open(file_abs_path, 'r') as file:
                content = file.read()
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {str(e)}")
            return False

        modified_lines = [i for i in range(len(content.splitlines()))]
        
        # Update progress bar to indicate we're moving to next stage
        pbar.update(1)
        
        # --- STAGE 3: Documenting ---
        update_stage(pbar, "Documenting")
        
        response = self.api_client.send_file_for_docstring_generation(file_path, content, modified_lines, self.repo_details)
        
        if response is None:
            return False
            
        if response == content:
            logger.info(f"No changes needed for {file_path}")
            return False
        
        # Update progress bar to indicate we're moving to next stage
        pbar.update(1)
        
        # --- STAGE 4: Writing changes ---
        update_stage(pbar, "Writing changes")
        
        try:
            with open(file_abs_path, 'w') as file:
                file.write(response)
            logger.info(f"Updated file {file_path} with generated documentation")
            
            # Mark final stage as complete
            pbar.update(1)
            return True
        except Exception as e:
            logger.error(f"Error writing file {file_path}: {str(e)}")
            return False
    
    def print_processing(self, file_path):
        """Print a processing message for a file."""
        formatted_path = format_file_path(file_path)
        print(f"\n{format_highlight(f'Processing file: {formatted_path}')}")

    def run(self):
        """Run the post-commit hook.

        This method executes the post-commit hook by processing a specified
        file. It attempts to process the file located at `self.file_path`. If an
        error occurs during the processing, it catches the exception and prints
        an error message indicating that the file was not processed. The method
        displays a progress bar and colored output to provide visual feedback on
        the processing status.
        """
        
        # Create a progress bar with appropriate stages
        stages = ["Validating", "Reading content", "Documenting", "Writing changes", "Completed"]
        pbar, _ = create_stage_progress_bar(stages, f"Starting documenting")
        
        try:
            # Print a clear indication of which file is being processed
            # self.print_processing(self.file_path)
            
            # Process the file
            result = self.process_file(self.file_path, pbar)
            
            # Ensure all stages are completed
            remaining_steps = len(stages) - pbar.n
            pbar.update(remaining_steps)
            
                
            # Display appropriate message based on result
            remaining = len(stages) - pbar.n
            if remaining > 0:
                pbar.update(remaining)
            update_stage(pbar, "Complete")
            pbar.clear()
            pbar.close()
                
        except Exception as e:
            remaining = len(stages) - pbar.n
            if remaining > 0:
                pbar.update(remaining)
            update_stage(pbar, "Complete")
            pbar.clear()
            pbar.close()
            print_status('error', e)
            sys.exit(1)
            
            # Ensure progress bar completes even on error
        if result:
            print_success(f"\n✓ Documentation updated for {self.relative_file_path}")
        else:
            print_success(f"\n✓ No changes needed for {self.relative_file_path}")
                
