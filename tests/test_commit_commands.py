import os
import sys
import pytest
from unittest.mock import patch, MagicMock, call

from penify_hook.commands.commit_commands import commit_code, setup_commit_parser, handle_commit

class TestCommitCommands:

    @pytest.fixture
    def mock_api_client(self):
        with patch('penify_hook.commands.commit_commands.APIClient') as mock:
            api_client_instance = MagicMock()
            mock.return_value = api_client_instance
            yield mock, api_client_instance

    @pytest.fixture
    def mock_llm_client(self):
        with patch('penify_hook.commands.commit_commands.LLMClient', create=True) as mock:
            llm_client_instance = MagicMock()
            mock.return_value = llm_client_instance
            yield mock, llm_client_instance

    @pytest.fixture
    def mock_jira_client(self):
        with patch('penify_hook.commands.commit_commands.JiraClient', create=True) as mock:
            jira_instance = MagicMock()
            jira_instance.is_connected.return_value = True
            mock.return_value = jira_instance
            yield mock, jira_instance

    @pytest.fixture
    def mock_commit_doc_gen(self):
        with patch('penify_hook.commands.commit_commands.CommitDocGenHook') as mock:
            doc_gen_instance = MagicMock()
            mock.return_value = doc_gen_instance
            yield mock, doc_gen_instance

    @pytest.fixture
    def mock_git_folder_search(self):
        with patch('penify_hook.commands.commit_commands.recursive_search_git_folder') as mock:
            mock.return_value = '/mock/git/folder'
            yield mock
            
    @pytest.fixture
    def mock_print_functions(self):
        with patch('penify_hook.commands.commit_commands.print_info') as mock_info, \
             patch('penify_hook.commands.commit_commands.print_warning') as mock_warning, \
             patch('penify_hook.commands.commit_commands.print_error', create=True) as mock_error:
            yield mock_info, mock_warning, mock_error

    def test_commit_code_with_llm_client(self, mock_api_client, mock_llm_client, mock_commit_doc_gen, 
                                        mock_git_folder_search, mock_print_functions):
        # Unpack mocks
        api_mock, api_instance = mock_api_client
        llm_mock, llm_instance = mock_llm_client
        doc_gen_mock, doc_gen_instance = mock_commit_doc_gen
        mock_info, mock_warning, mock_error = mock_print_functions
        
        # Call function with LLM parameters
        commit_code(
            api_url="http://api.example.com",
            token="api-token",
            message="test commit",
            open_terminal=False,
            generate_description=True,
            llm_model="gpt-4",
            llm_api_base="http://llm-api.example.com",
            llm_api_key="llm-api-key"
        )
        
        # Verify calls
        api_mock.assert_called_once_with("http://api.example.com", "api-token")
        llm_mock.assert_called_once_with(
            model="gpt-4",
            api_base="http://llm-api.example.com",
            api_key="llm-api-key"
        )
        mock_info.assert_called_once_with("Using LLM model: gpt-4")
        doc_gen_mock.assert_called_once_with('/mock/git/folder', api_instance, llm_instance, None)
        doc_gen_instance.run.assert_called_once_with("test commit", False, True)

    def test_commit_code_with_jira_client(self, mock_api_client, mock_llm_client, mock_jira_client,
                                         mock_commit_doc_gen, mock_git_folder_search, mock_print_functions):
        # Unpack mocks
        api_mock, api_instance = mock_api_client
        llm_mock, llm_instance = mock_llm_client
        jira_mock, jira_instance = mock_jira_client
        doc_gen_mock, doc_gen_instance = mock_commit_doc_gen
        mock_info, mock_warning, mock_error = mock_print_functions
        
        # Call function with JIRA parameters
        commit_code(
            api_url="http://api.example.com",
            token="api-token",
            message="test commit",
            open_terminal=False,
            generate_description=True,
            llm_model="gpt-4",
            llm_api_base="http://llm-api.example.com",
            llm_api_key="llm-api-key",
            jira_url="https://jira.example.com",
            jira_user="jira-user",
            jira_api_token="jira-token"
        )
        
        # Verify calls
        jira_mock.assert_called_once_with(
            jira_url="https://jira.example.com",
            jira_user="jira-user",
            jira_api_token="jira-token"
        )
        mock_info.assert_any_call("Connected to JIRA: https://jira.example.com")
        doc_gen_mock.assert_called_once_with('/mock/git/folder', api_instance, llm_instance, jira_instance)

    def test_commit_code_with_jira_connection_failure(self, mock_api_client, mock_llm_client, mock_jira_client,
                                                    mock_commit_doc_gen, mock_git_folder_search, mock_print_functions):
        # Setup jira connection failure
        api_mock, api_instance = mock_api_client
        llm_mock, llm_instance = mock_llm_client
        jira_mock, jira_instance = mock_jira_client
        jira_instance.is_connected.return_value = False
        mock_info, mock_warning, mock_error = mock_print_functions
        
        commit_code(
            api_url="http://api.example.com",
            token="api-token",
            message="test commit",
            open_terminal=False,
            generate_description=True,
            llm_model=None,
            jira_url="https://jira.example.com",
            jira_user="jira-user",
            jira_api_token="jira-token"
        )
        
        # Verify JIRA warning
        mock_warning.assert_called_once_with("Failed to connect to JIRA: https://jira.example.com")
        mock_commit_doc_gen[0].assert_called_once_with('/mock/git/folder', api_instance, None, None)

    def test_commit_code_error_handling(self, mock_api_client, mock_commit_doc_gen, mock_git_folder_search):
        # Setup to raise an exception
        mock_commit_doc_gen[0].side_effect = Exception("Test error")
        
        with patch('sys.exit') as mock_exit, \
             patch('builtins.print') as mock_print:
            
            commit_code(
                api_url="http://api.example.com",
                token="api-token",
                message="test commit",
                open_terminal=False,
                generate_description=True
            )
            
            mock_print.assert_called_once_with("Error: Test error")
            mock_exit.assert_called_once_with(1)

    def test_setup_commit_parser(self):
        parser = MagicMock()
        setup_commit_parser(parser)
        
        # Verify parser configuration
        assert parser.add_argument.call_count == 3
        parser.add_argument.assert_any_call("-m", "--message", required=False, help="Commit with contextual commit message.", default="N/A")
        parser.add_argument.assert_any_call("-e", "--terminal", action="store_true", help="Open edit terminal before committing.")
        parser.add_argument.assert_any_call("-d", "--description", action="store_false", help="It will generate commit message with title and description.", default=False)

    @patch('penify_hook.commands.commit_commands.get_jira_config')
    @patch('penify_hook.commands.commit_commands.get_llm_config')
    @patch('penify_hook.commands.commit_commands.get_token')
    @patch('penify_hook.commands.commit_commands.commit_code')
    @patch('penify_hook.commands.commit_commands.print_info')
    @patch('penify_hook.commands.commit_commands.API_URL', "http://api.example.com")
    def test_handle_commit(self, mock_print_info, mock_commit_code, mock_get_token, 
                         mock_get_llm_config, mock_get_jira_config):
        # Setup mocks
        mock_get_llm_config.return_value = {
            'model': 'test-model',
            'api_base': 'http://llm-api.example.com',
            'api_key': 'llm-key'
        }
        mock_get_token.return_value = 'api-token'
        mock_get_jira_config.return_value = {
            'url': 'https://jira.example.com',
            'username': 'jira-user',
            'api_token': 'jira-token'
        }
        
        # Create args
        args = MagicMock()
        args.message = "test commit"
        args.terminal = True
        args.description = True
        
        # Call function
        handle_commit(args)
        
        # Verify
        mock_print_info.assert_called_with("Generate Commit Description: True")
        mock_commit_code.assert_called_once_with(
            "http://api.example.com", 'api-token', "test commit", True, True,
            'test-model', 'http://llm-api.example.com', 'llm-key',
            'https://jira.example.com', 'jira-user', 'jira-token'
        )
