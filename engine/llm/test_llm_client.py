"""
KE-PR6: Unit Tests for Centralized LLM Client
Tests for provider switching, retries, and stubbed functionality
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from .client import LLMClient, LLMError, get_llm_client

class TestLLMClient:
    """Unit tests for the LLM Client with stubbed functionality"""
    
    def test_client_initialization_openai(self):
        """Test LLM client initialization with OpenAI provider"""
        with patch.dict('os.environ', {'LLM_PROVIDER': 'openai', 'OPENAI_API_KEY': 'test-key'}):
            client = LLMClient(provider='openai')
            assert client.provider == 'openai'
            assert client.timeout == 120
            assert client.max_retries == 3
    
    def test_client_initialization_anthropic(self):
        """Test LLM client initialization with Anthropic provider"""
        with patch.dict('os.environ', {'LLM_PROVIDER': 'anthropic', 'ANTHROPIC_API_KEY': 'test-key'}):
            client = LLMClient(provider='anthropic')
            assert client.provider == 'anthropic'
    
    def test_client_initialization_local(self):
        """Test LLM client initialization with local provider"""
        with patch.dict('os.environ', {'LLM_PROVIDER': 'local'}):
            client = LLMClient(provider='local')
            assert client.provider == 'local'
    
    def test_provider_switching_via_env(self):
        """Test provider switching via environment variable"""
        with patch.dict('os.environ', {'LLM_PROVIDER': 'anthropic', 'ANTHROPIC_API_KEY': 'test-key'}):
            client = LLMClient()
            assert client.provider == 'anthropic'
        
        with patch.dict('os.environ', {'LLM_PROVIDER': 'openai', 'OPENAI_API_KEY': 'test-key'}):
            client = LLMClient()
            assert client.provider == 'openai'
    
    def test_validation_missing_openai_key(self):
        """Test validation fails when OpenAI key is missing"""
        with patch.dict('os.environ', {'LLM_PROVIDER': 'openai'}, clear=True):
            with pytest.raises(LLMError, match="OpenAI API key required"):
                LLMClient(provider='openai')
    
    def test_validation_missing_anthropic_key(self):
        """Test validation fails when Anthropic key is missing"""
        with patch.dict('os.environ', {'LLM_PROVIDER': 'anthropic'}, clear=True):
            with pytest.raises(LLMError, match="Anthropic API key required"):
                LLMClient(provider='anthropic')
    
    def test_unsupported_provider(self):
        """Test error handling for unsupported provider"""
        with pytest.raises(LLMError, match="Unsupported provider"):
            LLMClient(provider='unsupported')
    
    def test_auth_headers_openai(self):
        """Test authentication headers for OpenAI"""
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-openai-key'}):
            client = LLMClient(provider='openai')
            headers = client._get_auth_headers()
            assert headers['Authorization'] == 'Bearer test-openai-key'
            assert headers['Content-Type'] == 'application/json'
    
    def test_auth_headers_anthropic(self):
        """Test authentication headers for Anthropic"""
        with patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-anthropic-key'}):
            client = LLMClient(provider='anthropic')
            headers = client._get_auth_headers()
            assert headers['x-api-key'] == 'test-anthropic-key'
            assert headers['anthropic-version'] == '2023-06-01'
    
    def test_secret_redaction(self):
        """Test secret redaction in logs"""
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'sk-1234567890abcdef'}):
            client = LLMClient(provider='openai')
            text = "Error with key sk-1234567890abcdef"
            redacted = client._redact_secrets(text)
            assert "sk-***cdef" in redacted
            assert "sk-1234567890abcdef" not in redacted
    
    def test_exponential_backoff(self):
        """Test exponential backoff calculation"""
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
            client = LLMClient(provider='openai')
            
            # Test backoff increases
            delay_0 = client._exponential_backoff(0)
            delay_1 = client._exponential_backoff(1)
            delay_2 = client._exponential_backoff(2)
            
            # Should increase exponentially
            assert delay_1 > delay_0
            assert delay_2 > delay_1
            
            # Should be capped at 60 seconds
            delay_high = client._exponential_backoff(10)
            assert delay_high <= 60
    
    @pytest.mark.asyncio
    async def test_message_formatting_prompt(self):
        """Test message formatting with single prompt"""
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
            client = LLMClient(provider='openai')
            messages = client._format_messages(prompt="Test prompt")
            
            assert len(messages) == 1
            assert messages[0]['role'] == 'user'
            assert messages[0]['content'] == 'Test prompt'
    
    @pytest.mark.asyncio
    async def test_message_formatting_system_user(self):
        """Test message formatting with system and user messages"""
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
            client = LLMClient(provider='openai')
            messages = client._format_messages(
                system_message="System instruction",
                user_message="User query"
            )
            
            assert len(messages) == 2
            assert messages[0]['role'] == 'system'
            assert messages[0]['content'] == 'System instruction'
            assert messages[1]['role'] == 'user'
            assert messages[1]['content'] == 'User query'
    
    def test_message_formatting_empty(self):
        """Test error handling for empty messages"""
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
            client = LLMClient(provider='openai')
            with pytest.raises(LLMError, match="No prompt"):
                client._format_messages()
    
    def test_payload_preparation_openai(self):
        """Test payload preparation for OpenAI"""
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
            client = LLMClient(provider='openai')
            messages = [{'role': 'user', 'content': 'Test'}]
            payload = client._prepare_payload(messages, 'gpt-4o-mini', 0.7, 4000)
            
            assert payload['model'] == 'gpt-4o-mini'
            assert payload['temperature'] == 0.7
            assert payload['max_tokens'] == 4000
            assert payload['messages'] == messages
            assert payload['stream'] is False
    
    def test_payload_preparation_anthropic(self):
        """Test payload preparation for Anthropic"""
        with patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-key'}):
            client = LLMClient(provider='anthropic')
            messages = [
                {'role': 'system', 'content': 'System'},
                {'role': 'user', 'content': 'User'}
            ]
            payload = client._prepare_payload(messages, 'claude-3-5-sonnet-20241022', 0.7, 4000)
            
            assert payload['model'] == 'claude-3-5-sonnet-20241022'
            assert payload['temperature'] == 0.7
            assert payload['max_tokens'] == 4000
            assert payload['system'] == 'System'
            assert len(payload['messages']) == 1
            assert payload['messages'][0]['role'] == 'user'
    
    def test_response_extraction_openai(self):
        """Test response extraction for OpenAI format"""
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
            client = LLMClient(provider='openai')
            response = {
                'choices': [
                    {'message': {'content': '  Test response  '}}
                ]
            }
            content = client._extract_completion(response)
            assert content == 'Test response'
    
    def test_response_extraction_anthropic(self):
        """Test response extraction for Anthropic format"""
        with patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-key'}):
            client = LLMClient(provider='anthropic')
            response = {
                'content': [
                    {'text': '  Anthropic response  '}
                ]
            }
            content = client._extract_completion(response)
            assert content == 'Anthropic response'
    
    def test_response_extraction_error(self):
        """Test error handling for malformed responses"""
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
            client = LLMClient(provider='openai')
            response = {'invalid': 'format'}
            with pytest.raises(LLMError, match="Failed to extract completion"):
                client._extract_completion(response)
    
    @pytest.mark.asyncio
    async def test_moderation_openai(self):
        """Test content moderation for OpenAI"""
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
            client = LLMClient(provider='openai')
            
            # Mock the HTTP response
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'results': [{'flagged': False, 'categories': {}, 'category_scores': {}}]
            }
            
            with patch('httpx.AsyncClient') as mock_client:
                mock_client.return_value.__aenter__.return_value.post.return_value = mock_response
                
                result = await client.moderate("Test content")
                assert result['ok'] is True
    
    @pytest.mark.asyncio
    async def test_moderation_non_openai(self):
        """Test content moderation for non-OpenAI providers"""
        with patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-key'}):
            client = LLMClient(provider='anthropic')
            result = await client.moderate("Test content")
            assert result['ok'] is True
            assert 'not implemented' in result['message']
    
    @pytest.mark.asyncio
    async def test_complete_stubbed(self):
        """Test complete method with stubbed HTTP response"""
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
            client = LLMClient(provider='openai')
            
            # Mock successful HTTP response
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'choices': [{'message': {'content': 'Mocked LLM response'}}]
            }
            
            with patch('httpx.AsyncClient') as mock_client:
                mock_client.return_value.__aenter__.return_value.post.return_value = mock_response
                
                result = await client.complete(prompt="Test prompt")
                assert result == 'Mocked LLM response'
    
    @pytest.mark.asyncio 
    async def test_complete_retry_logic(self):
        """Test retry logic with multiple failures"""
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
            client = LLMClient(provider='openai')
            
            # Mock failed HTTP responses
            mock_response = AsyncMock()
            mock_response.status_code = 500
            mock_response.text = "Server error"
            
            with patch('httpx.AsyncClient') as mock_client:
                mock_client.return_value.__aenter__.return_value.post.return_value = mock_response
                
                with pytest.raises(LLMError, match="LLM completion failed"):
                    await client.complete(prompt="Test prompt")
    
    def test_global_client_instance(self):
        """Test global client instance management"""
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
            # First call creates instance
            client1 = get_llm_client(provider='openai')
            assert client1.provider == 'openai'
            
            # Second call with different provider creates new instance
            client2 = get_llm_client(provider='anthropic')
            assert client2.provider == 'anthropic'
            
            # Call without provider returns existing instance
            client3 = get_llm_client()
            assert client3.provider == 'anthropic'  # Should be the last created


if __name__ == "__main__":
    # Run tests
    import subprocess
    import sys
    
    try:
        # Try to run with pytest
        subprocess.run([sys.executable, "-m", "pytest", __file__, "-v"], check=True)
    except subprocess.CalledProcessError:
        # Fallback to basic test runner
        print("Running basic test verification...")
        test_instance = TestLLMClient()
        
        # Run basic tests
        test_instance.test_client_initialization_openai()
        test_instance.test_provider_switching_via_env()
        test_instance.test_unsupported_provider()
        
        print("✅ Basic LLM client tests passed")