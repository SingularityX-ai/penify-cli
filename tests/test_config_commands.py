import os
import json
import pytest
from unittest.mock import patch, mock_open, MagicMock
from pathlib import Path

from penify_hook.commands.config_commands import (
    get_penify_config, 
    get_llm_config, 
    get_jira_config, 
    save_llm_config, 
    save_jira_config,
    get_token
)

class TestConfigCommands:
    
    @patch('penify_hook.utils.recursive_search_git_folder')
    @patch('penify_hook.commands.config_commands.Path')
    @patch('os.makedirs')
    @patch('builtins.open', new_callable=mock_open)
    def test_get_penify_config_existing_dir(self, mock_file_open, mock_makedirs, mock_path, mock_git_folder):
        # Mock git folder search
        mock_git_folder.return_value = '/mock/git/folder'
        
        # Mock Path operations
        mock_path_instance = MagicMock()
        mock_path.return_value = mock_path_instance
        mock_path_instance.__truediv__.return_value = mock_path_instance
        
        # Path exists for .penify dir
        mock_path_instance.exists.return_value = True
        
        # Call function
        result = get_penify_config()
        
        # Assertions
        mock_git_folder.assert_called_once_with(os.getcwd())
        mock_path.assert_called_once_with('/mock/git/folder')
        mock_path_instance.__truediv__.assert_called_with('.penify')
        assert mock_makedirs.call_count == 0  # Should not create directory
        
    @patch('penify_hook.utils.recursive_search_git_folder')
    @patch('penify_hook.commands.config_commands.Path')
    @patch('os.makedirs')
    @patch('builtins.open', new_callable=mock_open)
    def test_get_penify_config_new_dir(self, mock_file_open, mock_makedirs, mock_path, mock_git_folder):
        # Mock git folder search
        mock_git_folder.return_value = '/mock/git/folder'
        
        # Mock Path operations
        mock_path_instance = MagicMock()
        mock_path.return_value = mock_path_instance
        mock_path_instance.__truediv__.return_value = mock_path_instance
        
        # Path doesn't exist for .penify dir
        mock_path_instance.exists.side_effect = [False, False]
        
        # Call function
        result = get_penify_config()
        
        # Assertions
        mock_makedirs.assert_called_with(mock_path_instance, exist_ok=True)
        mock_file_open.assert_called_once()
        mock_file_open().write.assert_called_once_with('{}')
        
    @patch('penify_hook.commands.config_commands.get_penify_config')
    @patch('builtins.open', new_callable=mock_open, read_data='{"llm": {"model": "gpt-4", "api_base": "https://api.openai.com", "api_key": "test-key"}}')
    def test_get_llm_config_exists(self, mock_file_open, mock_get_config):
        # Setup mock
        mock_config_file = MagicMock()
        mock_config_file.exists.return_value = True
        mock_get_config.return_value = mock_config_file
        
        # Call function
        result = get_llm_config()
        
        # Assertions
        assert result == {
            'model': 'gpt-4', 
            'api_base': 'https://api.openai.com', 
            'api_key': 'test-key'
        }
        mock_file_open.assert_called_once_with(mock_config_file, 'r')
        
    @patch('penify_hook.commands.config_commands.get_penify_config')
    @patch('builtins.open', new_callable=mock_open, read_data='{}')
    def test_get_llm_config_empty(self, mock_file_open, mock_get_config):
        # Setup mock
        mock_config_file = MagicMock()
        mock_config_file.exists.return_value = True
        mock_get_config.return_value = mock_config_file
        
        # Call function
        result = get_llm_config()
        
        # Assertions
        assert result == {}
        mock_file_open.assert_called_once_with(mock_config_file, 'r')
        
    @patch('penify_hook.commands.config_commands.get_penify_config')
    @patch('builtins.open', new_callable=mock_open, read_data='invalid json')
    @patch('builtins.print')
    def test_get_llm_config_invalid_json(self, mock_print, mock_file_open, mock_get_config):
        # Setup mock
        mock_config_file = MagicMock()
        mock_config_file.exists.return_value = True
        mock_get_config.return_value = mock_config_file
        
        # Call function
        result = get_llm_config()
        
        # Assertions
        assert result == {}
        mock_print.assert_called_once()
        assert 'Error reading .penify config file' in mock_print.call_args[0][0]
        
    @patch('penify_hook.commands.config_commands.get_penify_config')
    @patch('builtins.open', new_callable=mock_open, read_data='{"jira": {"url": "https://jira.example.com", "username": "user", "api_token": "token"}}')
    def test_get_jira_config_exists(self, mock_file_open, mock_get_config):
        # Setup mock
        mock_config_file = MagicMock()
        mock_config_file.exists.return_value = True
        mock_get_config.return_value = mock_config_file
        
        # Call function
        result = get_jira_config()
        
        # Assertions
        assert result == {
            'url': 'https://jira.example.com',
            'username': 'user', 
            'api_token': 'token'
        }
        mock_file_open.assert_called_once_with(mock_config_file, 'r')
        
    @patch('penify_hook.commands.config_commands.get_penify_config')
    @patch('builtins.open', new_callable=mock_open)
    @patch('json.dump')
    @patch('builtins.print')
    def test_save_llm_config_success(self, mock_print, mock_json_dump, mock_file_open, mock_get_config):
        # Setup mock
        mock_config_file = MagicMock()
        mock_get_config.return_value = mock_config_file
        mock_file_open.return_value.__enter__.return_value = mock_file_open
        
        # Mock json.load to return empty dict when reading
        with patch('json.load', return_value={}):
            # Call function
            result = save_llm_config("gpt-4", "https://api.openai.com", "test-key")
            
            # Assertions
            assert result == True
            mock_json_dump.assert_called_once()
            expected_config = {
                'llm': {
                    'model': 'gpt-4',
                    'api_base': 'https://api.openai.com',
                    'api_key': 'test-key'
                }
            }
            assert mock_json_dump.call_args[0][0] == expected_config
            mock_print.assert_called_once()
            assert 'configuration saved' in mock_print.call_args[0][0]
        
    @patch('penify_hook.commands.config_commands.get_penify_config')
    @patch('builtins.open', side_effect=IOError("Permission denied"))
    @patch('builtins.print')
    def test_save_llm_config_failure(self, mock_print, mock_file_open, mock_get_config):
        # Setup mock
        mock_config_file = MagicMock()
        mock_config_file.exists.return_value = True
        mock_get_config.return_value = mock_config_file
    
        # Call function
        result = save_llm_config("gpt-4", "https://api.openai.com", "test-key")
        
        # Assert
        assert result is False
        mock_print.assert_called_with("Error saving LLM configuration: Permission denied")
        
    @patch('penify_hook.commands.config_commands.Path')
    @patch('builtins.open', new_callable=mock_open)
    @patch('json.dump')
    @patch('builtins.print')
    def test_save_jira_config_success(self, mock_print, mock_json_dump, mock_file_open, mock_path):
        # Setup mock
        mock_home_dir = MagicMock()
        mock_path.home.return_value = mock_home_dir
        mock_home_dir.__truediv__.return_value = mock_home_dir
        mock_home_dir.exists.return_value = True
        
        # Mock json.load to return empty dict when reading
        with patch('json.load', return_value={}):
            # Call function
            result = save_jira_config("https://jira.example.com", "user", "token")
            
            # Assertions
            assert result == True
            mock_json_dump.assert_called_once()
            expected_config = {
                'jira': {
                    'url': 'https://jira.example.com',
                    'username': 'user',
                    'api_token': 'token'
                }
            }
            assert mock_json_dump.call_args[0][0] == expected_config
            mock_print.assert_called_once()
            assert 'configuration saved' in mock_print.call_args[0][0]
            
    @patch('os.getenv')
    @patch('penify_hook.commands.config_commands.Path')
    @patch('builtins.open', new_callable=mock_open, read_data='{"api_keys": "config-token"}')
    def test_get_token_from_env(self, mock_file_open, mock_path, mock_getenv):
        # Setup mock for env var
        mock_getenv.return_value = "env-token"
        
        # Call function
        result = get_token()
        
        # Assertions
        assert result == "env-token"
        mock_getenv.assert_called_once_with('PENIFY_API_TOKEN')
        # File should not be read if env var exists
        assert mock_file_open.call_count == 0
        
    @patch('os.getenv')
    @patch('penify_hook.commands.config_commands.Path')
    @patch('builtins.open', new_callable=mock_open, read_data='{"api_keys": "config-token"}')
    def test_get_token_from_config(self, mock_file_open, mock_path, mock_getenv):
        # Setup mock for env var (not found)
        mock_getenv.return_value = None
        
        # Setup mock for config file
        mock_home_dir = MagicMock()
        mock_path.home.return_value = mock_home_dir
        mock_home_dir.__truediv__.return_value = mock_home_dir
        mock_home_dir.exists.return_value = True
        
        # Call function
        result = get_token()
        
        # Assertions
        assert result == "config-token"
        mock_getenv.assert_called_once_with('PENIFY_API_TOKEN')
        mock_file_open.assert_called_once_with(mock_home_dir, 'r')
        
    @patch('os.getenv')
    @patch('penify_hook.commands.config_commands.Path')
    @patch('builtins.open', new_callable=mock_open, read_data='{"other_key": "value"}')
    def test_get_token_not_found(self, mock_file_open, mock_path, mock_getenv):
        # Setup mock for env var (not found)
        mock_getenv.return_value = None
        
        # Setup mock for config file
        mock_home_dir = MagicMock()
        mock_path.home.return_value = mock_home_dir
        mock_home_dir.__truediv__.return_value = mock_home_dir
        mock_home_dir.exists.return_value = True
        
        # Call function
        result = get_token()
        
        # Assertions
        assert result is None
        mock_getenv.assert_called_once_with('PENIFY_API_TOKEN')
        mock_file_open.assert_called_once_with(mock_home_dir, 'r')
