import pytest
import sys
import os
from argparse import ArgumentParser
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from penify_hook.commands.doc_commands import (
    generate_doc,
    setup_docgen_parser,
    handle_docgen
)


@patch('penify_hook.file_analyzer.FileAnalyzerGenHook')
@patch('penify_hook.git_analyzer.GitDocGenHook')
@patch('penify_hook.folder_analyzer.FolderAnalyzerGenHook')
@patch('penify_hook.api_client.APIClient')
@patch('penify_hook.commands.doc_commands.os.getcwd')
def test_generate_doc_no_location(mock_getcwd, mock_api_client, 
                                 mock_folder_analyzer, mock_file_analyzer, 
                                 mock_git_analyzer):
    # Setup
    mock_api_instance = MagicMock()
    mock_api_client.return_value = mock_api_instance
    mock_getcwd.return_value = '/fake/current/dir'
    mock_git_instance = MagicMock()
    mock_git_analyzer.return_value = mock_git_instance
    
    # Call function
    generate_doc('http://api.example.com', 'fake-token', None)
    
    # Assertions
    mock_api_client.assert_called_once_with('http://api.example.com', 'fake-token')
    mock_git_analyzer.assert_called_once_with('/fake/current/dir', mock_api_instance)
    mock_git_instance.run.assert_called_once()
    # mock_file_analyzer.assert_not_called()
    # mock_folder_analyzer.assert_not_called()


@patch('penify_hook.git_analyzer.GitDocGenHook')
@patch('penify_hook.folder_analyzer.FolderAnalyzerGenHook')
@patch('penify_hook.api_client.APIClient')
@patch('penify_hook.api_client.APIClient')
def test_generate_doc_file_location(mock_api_client, mock_folder_analyzer, 
                                   mock_file_analyzer, mock_git_analyzer):
    # Setup
    mock_api_instance = MagicMock()
    mock_api_client.return_value = mock_api_instance
    mock_file_instance = MagicMock()
    mock_file_analyzer.return_value = mock_file_instance
    
    # Call function
    generate_doc('http://api.example.com', 'fake-token', 'example.py')
    
    # Assertions
    mock_api_client.assert_called_once_with('http://api.example.com', 'fake-token')
    mock_file_analyzer.assert_called_once_with('example.py', mock_api_instance)
    mock_file_instance.run.assert_called_once()
    mock_git_analyzer.assert_not_called()
    mock_folder_analyzer.assert_not_called()


@patch('penify_hook.commands.doc_commands.GitDocGenHook')
@patch('penify_hook.commands.doc_commands.FileAnalyzerGenHook')
@patch('penify_hook.commands.doc_commands.FolderAnalyzerGenHook')
@patch('penify_hook.api_client.APIClient')
def test_generate_doc_folder_location(mock_api_client, mock_folder_analyzer, 
                                     mock_file_analyzer, mock_git_analyzer):
    # Setup
    mock_api_instance = MagicMock()
    mock_api_client.return_value = mock_api_instance
    mock_folder_instance = MagicMock()
    mock_folder_analyzer.return_value = mock_folder_instance
    
    # Call function
    generate_doc('http://api.example.com', 'fake-token', 'src')
    
    # Assertions
    mock_api_client.assert_called_once_with('http://api.example.com', 'fake-token')
    mock_folder_analyzer.assert_called_once_with('src', mock_api_instance)
    mock_folder_instance.run.assert_called_once()
    mock_git_analyzer.assert_not_called()
    mock_file_analyzer.assert_not_called()


@patch('sys.exit')
@patch('penify_hook.commands.doc_commands.GitDocGenHook')
@patch('penify_hook.api_client.APIClient')
def test_generate_doc_error_handling(mock_api_client, mock_git_analyzer, mock_exit):
    # Setup
    mock_api_instance = MagicMock()
    mock_api_client.return_value = mock_api_instance
    mock_git_analyzer.side_effect = Exception("Test error")
    
    # Call function
    generate_doc('http://api.example.com', 'fake-token', None)
    
    # Assertions
    mock_exit.assert_called_once_with(1)


def test_setup_docgen_parser():
    parser = ArgumentParser()
    setup_docgen_parser(parser)
    
    # Check that docgen options are properly set up
    args = parser.parse_args(['-l', 'test_location'])
    assert args.location == 'test_location'
    
    # Check install-hook subcommand
    args = parser.parse_args(['install-hook', '-l', 'hook_location'])
    assert args.docgen_subcommand == 'install-hook'
    assert args.location == 'hook_location'
    
    # Check uninstall-hook subcommand
    args = parser.parse_args(['uninstall-hook', '-l', 'hook_location'])
    assert args.docgen_subcommand == 'uninstall-hook'
    assert args.location == 'hook_location'


@patch('penify_hook.commands.doc_commands.install_git_hook')
@patch('penify_hook.commands.doc_commands.uninstall_git_hook')
@patch('penify_hook.commands.doc_commands.generate_doc')
@patch('penify_hook.commands.doc_commands.get_token')
@patch('sys.exit')
def test_handle_docgen_install_hook(mock_exit, mock_get_token, mock_generate_doc, 
                                   mock_uninstall_hook, mock_install_hook):
    # Setup
    mock_get_token.return_value = 'fake-token'
    
    # Test install-hook subcommand
    args = MagicMock(docgen_subcommand='install-hook', location='hook_location')
    handle_docgen(args)
    mock_install_hook.assert_called_once_with('hook_location', 'fake-token')
    mock_generate_doc.assert_not_called()
    mock_uninstall_hook.assert_not_called()


@patch('penify_hook.commands.doc_commands.install_git_hook')
@patch('penify_hook.commands.doc_commands.uninstall_git_hook')
@patch('penify_hook.commands.doc_commands.generate_doc')
@patch('penify_hook.commands.doc_commands.get_token')
@patch('sys.exit')
def test_handle_docgen_uninstall_hook(mock_exit, mock_get_token, mock_generate_doc, 
                                     mock_uninstall_hook, mock_install_hook):
    # Setup
    mock_get_token.return_value = 'fake-token'
    
    # Test uninstall-hook subcommand
    args = MagicMock(docgen_subcommand='uninstall-hook', location='hook_location')
    handle_docgen(args)
    mock_uninstall_hook.assert_called_once_with('hook_location')
    mock_generate_doc.assert_not_called()
    mock_install_hook.assert_not_called()


@patch('penify_hook.commands.doc_commands.install_git_hook')
@patch('penify_hook.commands.doc_commands.uninstall_git_hook')
@patch('penify_hook.commands.doc_commands.generate_doc')
@patch('penify_hook.commands.doc_commands.get_token')
def test_handle_docgen_generate(mock_get_token, mock_generate_doc, 
                               mock_uninstall_hook, mock_install_hook):
    # Setup
    mock_get_token.return_value = 'fake-token'
    
    # Test direct documentation generation
    args = MagicMock(docgen_subcommand=None, location='doc_location')
    handle_docgen(args)
    mock_generate_doc.assert_called_once()
    mock_install_hook.assert_not_called()
    mock_uninstall_hook.assert_not_called()


@patch('penify_hook.commands.doc_commands.get_token')
@patch('sys.exit')
def test_handle_docgen_no_token(mock_exit, mock_get_token):
    # Test with no token
    mock_get_token.return_value = None
    args = MagicMock(docgen_subcommand=None, location='doc_location')
    handle_docgen(args)
    mock_exit.assert_called_once_with(1)


@patch('penify_hook.commands.doc_commands.os.getcwd')
@patch('penify_hook.api_client.APIClient')
def test_generate_doc_with_file_exception(mock_api_client, mock_getcwd):
    # Setup
    mock_api_client.side_effect = Exception("API error")
    mock_getcwd.return_value = '/fake/current/dir'
    
    # Test file location with exception
    with pytest.raises(SystemExit):
        generate_doc('http://api.example.com', 'fake-token', 'example.py')


@patch('penify_hook.commands.doc_commands.os.getcwd')
@patch('penify_hook.api_client.APIClient')
def test_generate_doc_with_folder_exception(mock_api_client, mock_getcwd):
    # Setup
    mock_api_client.side_effect = Exception("API error")
    mock_getcwd.return_value = '/fake/current/dir'
    
    # Test folder location with exception
    with pytest.raises(SystemExit):
        generate_doc('http://api.example.com', 'fake-token', 'src_folder')
