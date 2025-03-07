import pytest
import json
import http.server
import threading
import socketserver
import time
from unittest.mock import patch, MagicMock, mock_open
import webbrowser

from penify_hook.commands.config_commands import config_llm_web, config_jira_web


class TestWebConfig:
    
    @patch('webbrowser.open')
    @patch('socketserver.TCPServer')
    @patch('pkg_resources.resource_filename')
    def test_config_llm_web_server_setup(self, mock_resource_filename, mock_server, mock_webbrowser):
        # Setup mocks
        mock_resource_filename.return_value = 'mock/template/path'
        mock_server_instance = MagicMock()
        mock_server.return_value.__enter__.return_value = mock_server_instance
        
        # Mock the serve_forever method to stop after being called once
        def stop_server_after_call():
            mock_server_instance.shutdown()
        mock_server_instance.serve_forever.side_effect = stop_server_after_call
        
        # Call function with patched webbrowser
        with patch('builtins.print'):  # Suppress print statements
            config_llm_web()
        
        # Verify webbrowser was opened
        mock_webbrowser.assert_called_once()
        assert mock_webbrowser.call_args[0][0].startswith('http://localhost:')
        
        # Verify server was started
        mock_server.assert_called_once()
        mock_server_instance.serve_forever.assert_called_once()

    @patch('webbrowser.open')
    @patch('socketserver.TCPServer')
    @patch('pkg_resources.resource_filename')
    def test_config_jira_web_server_setup(self, mock_resource_filename, mock_server, mock_webbrowser):
        # Setup mocks
        mock_resource_filename.return_value = 'mock/template/path'
        mock_server_instance = MagicMock()
        mock_server.return_value.__enter__.return_value = mock_server_instance
        
        # Mock the serve_forever method to stop after being called once
        def stop_server_after_call():
            mock_server_instance.shutdown()
        mock_server_instance.serve_forever.side_effect = stop_server_after_call
        
        # Call function with patched webbrowser
        with patch('builtins.print'):  # Suppress print statements
            config_jira_web()
        
        # Verify webbrowser was opened
        mock_webbrowser.assert_called_once()
        assert mock_webbrowser.call_args[0][0].startswith('http://localhost:')
        
        # Verify server was started
        mock_server.assert_called_once()
        mock_server_instance.serve_forever.assert_called_once()
