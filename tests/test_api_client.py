"""Tests for API client module."""

import pytest
from unittest.mock import Mock, patch
from src.ctfd_scraper.api_client import CTFdClient

def test_ctfd_client_initialization():
    """Test CTFdClient initialization."""
    client = CTFdClient()
    assert client.base_url is not None
    assert client.session is not None
    assert client.ctf_name is None

@patch('src.ctfd_scraper.api_client.requests.Session')
def test_get_ctf_name_from_title(mock_session):
    """Test CTF name extraction from HTML title."""
    client = CTFdClient()
    
    # Mock response with title
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.text = '<html><head><title>BITSCTF 2026 - CTFd</title></head></html>'
    client.session.get = Mock(return_value=mock_response)
    
    name = client.get_ctf_name()
    assert name == "BITSCTF 2026"

@patch('src.ctfd_scraper.api_client.requests.Session')
def test_get_ctf_name_fallback(mock_session):
    """Test CTF name fallback to default."""
    client = CTFdClient()
    
    # Mock failed response
    mock_response = Mock()
    mock_response.status_code = 404
    client.session.get = Mock(return_value=mock_response)
    
    name = client.get_ctf_name()
    assert name == "ctf"
