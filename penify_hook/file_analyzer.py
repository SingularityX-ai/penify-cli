import os
from git import Repo
from tqdm import tqdm
from .api_client import APIClient
import logging
from .ui_utils import (
    format_highlight, print_info, print_success, print_warning, print_error,
    print_status, create_stage_progress_bar,
    update_stage, format_file_path
)

# Set up logger
logger = logging.getLogger(__name__)

class FileAnalyzerGenHook:
    def __init__(self, file_path: str, api_client: APIClient):
        self.file_path = file_path
        self.api_client = api_client
        self.supported_file_types = set(self.api_client.get_supported_file_types())

    def process_file(self, file_path, pbar: tqdm):
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
        # self.print_processing(self.file_path)
        
        # First update the stage, then increment the progress
        update_stage(pbar, "Validating")
        pbar.update(1)  # Complete first stage
        
        if not file_extension:
            logger.info(f"File {file_path} has no extension. Skipping.")
            return False
        
        file_extension = file_extension[1:]  # Remove the leading dot

        if file_extension not in self.supported_file_types:
            logger.info(f"File type {file_extension} is not supported. Skipping {file_path}.")
            return False

        # Read content - first update stage, then progress
        update_stage(pbar, "Reading content")
        pbar.update(1)
        
        with open(file_abs_path, 'r') as file:
            content = file.read()

        modified_lines = [i for i in range(len(content.splitlines()))]
        
        # Process with API - first update stage, then progress
        update_stage(pbar, "Documenting")
        pbar.update(1)
        
        response = self.api_client.send_file_for_docstring_generation(file_path, content, modified_lines)
        
        if response is None:
            return False
            
        if response == content:
            logger.info(f"No changes needed for {file_path}")
            return False
        
        # Write changes - first update stage, then progress
        update_stage(pbar, "Writing changes")
        pbar.update(1)
        
        with open(file_abs_path, 'w') as file:
            file.write(response)
        logger.info(f"Updated file {file_path} with generated documentation")
        return True
    
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
        stages = ["INIT", "Validating", "Reading content", "Documenting", "Writing changes"]
        pbar, _ = create_stage_progress_bar(stages, f"Starting file documentation")
        
        try:
            result = self.process_file(self.file_path, pbar)
            
            # Ensure all stages are completed
            remaining_steps = len(stages) - pbar.n
            if remaining_steps > 0:
                pbar.update(remaining_steps)
                
            # Display appropriate message based on result
            if result:
                print_status('success', f"Documentation updated for {self.file_path}")
            else:
                print_status('warning', f"No changes needed for {self.file_path}")
                
        except Exception as e:
            error_msg = f"Error processing file [{self.file_path}]: {str(e)}"
            logger.error(error_msg)
            print_status('error', error_msg)
            
            # Ensure progress bar completes even on error
            remaining = len(stages) - pbar.n
            if remaining > 0:
                pbar.update(remaining)
                
        print_success("\n✓ File analysis complete")
