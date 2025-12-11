
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from app.services.ssh_service import SSHManager
# from backend.app.models.node import Node # Avoid SQLAlchemy issues

class MockNode:
    def __init__(self, id, host, port, username, is_center, ssh_key_path=None, encrypted_password=None):
        self.id = id
        self.host = host
        self.port = port
        self.username = username
        self.is_center = is_center
        self.ssh_key_path = ssh_key_path
        self.encrypted_password = encrypted_password

def run_async(coro):
    return asyncio.run(coro)

def test_ssh_connection_with_gateway():
    async def _test():
        # Setup
        ssh_manager = SSHManager()
        
        target_node = MockNode(id=2, host="target", port=22, username="user", is_center=0)
        gateway_node = MockNode(id=1, host="gateway", port=22, username="user", is_center=1)
        
        # Mocking _create_client_connection
        mock_conn = MagicMock()
        mock_conn.connect_ssh = AsyncMock() # This is called for the tunnel
        mock_conn.close = MagicMock()
        
        ssh_manager._create_client_connection = AsyncMock(return_value=mock_conn)
        
        # Execution
        # Iterate over the async generator
        async for conn in ssh_manager.connection_context(target_node, gateway_node):
            pass
            
        # Verification
        # _create_client_connection should be called twice: 
        # 1. For gateway
        # 2. For target (passed as tunnel)
        assert ssh_manager._create_client_connection.call_count == 2
        
        # First call should be for gateway
        args1, _ = ssh_manager._create_client_connection.call_args_list[0]
        assert args1[0] == gateway_node
        
        # Second call should be for target, with tunnel
        args2, kwargs2 = ssh_manager._create_client_connection.call_args_list[1]
        assert args2[0] == target_node
        assert kwargs2['tunnel'] == mock_conn

    run_async(_test())

def test_ssh_connection_without_gateway():
    async def _test():
        # Setup
        ssh_manager = SSHManager()
        
        target_node = MockNode(id=2, host="target", port=22, username="user", is_center=0)
        
        mock_conn = MagicMock()
        mock_conn.close = MagicMock()
        ssh_manager._create_client_connection = AsyncMock(return_value=mock_conn)
        
        # Execution
        async for conn in ssh_manager.connection_context(target_node):
            pass
        
        # Verification
        # Should be called once for target
        assert ssh_manager._create_client_connection.call_count == 1
        args, kwargs = ssh_manager._create_client_connection.call_args
        assert args[0] == target_node
        assert 'tunnel' not in kwargs or kwargs['tunnel'] is None

    run_async(_test())
