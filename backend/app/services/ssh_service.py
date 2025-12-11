import asyncssh
import asyncio
import os
from typing import AsyncGenerator
import logging

from ..models.node import Node
from ..security import decrypt_password

logger = logging.getLogger(__name__)

class SSHManager:
    """
    Manages SSH connections and remote command execution.
    """

    async def _create_client_connection(self, node: Node, tunnel: asyncssh.SSHClientConnection = None, gateway_node: Node = None) -> asyncssh.SSHClientConnection:
        """
        Creates a raw SSH connection object (helper).
        """
        try:
            client_keys = None
            password = None

            if node.ssh_key_path:
                client_keys = [os.path.expanduser(node.ssh_key_path)]
            elif node.encrypted_password:
                password = decrypt_password(node.encrypted_password)

            # Fallback: If target node has no credentials and we have a gateway, try using gateway's credentials
            if not client_keys and not password and gateway_node:
                # logger.debug(f"Target node {node.host} has no credentials, using gateway {gateway_node.host} credentials.")
                # Logic copied from frontend/nodes.py behavior
                if gateway_node.ssh_key_path:
                    client_keys = [os.path.expanduser(gateway_node.ssh_key_path)]
                elif gateway_node.encrypted_password:
                    password = decrypt_password(gateway_node.encrypted_password)

            # Debug log (sanitized)
            safe_pwd = '***' if password else 'None'
            # logger.debug(f"SSH Connecting to {node.host}:{node.port} (User: {node.username}, Key: {client_keys}, Pwd: {safe_pwd})")
            print(f"DEBUG: SSH Connecting to {node.host}:{node.port} (User: {node.username}, Key: {client_keys}, Pwd: {safe_pwd})")

            connect_kwargs = {
                "host": node.host,
                "port": node.port,
                "username": node.username,
                "password": password,
                "client_keys": client_keys,
                "known_hosts": None # For simplicity
            }
            
            # Remove keys with None values (except known_hosts which is explicitly None for now)
            # asyncssh will use defaults/config if username/client_keys are not provided
            connect_kwargs = {k: v for k, v in connect_kwargs.items() if v is not None or k == "known_hosts"}

            if tunnel:
                return await tunnel.connect_ssh(**connect_kwargs)
            else:
                return await asyncssh.connect(**connect_kwargs)

        except Exception as e:
            logger.error(f"Failed to connect to {node.host}: {e}")
            raise

    async def connection_context(self, node: Node, gateway_node: Node = None):
        """
        Context manager for SSH connection, handling optional gateway tunneling.
        """
        if gateway_node and node.id != gateway_node.id and not node.is_center:
             print(f"DEBUG: Attempting SSH tunnel via gateway: {gateway_node.host}")
             # Connect to gateway first
             gateway_conn = await self._create_client_connection(gateway_node)
             try:
                 print("DEBUG: Gateway connection established. Tunneling to target...")
                 # Tunnel through gateway
                 target_conn = await self._create_client_connection(node, tunnel=gateway_conn, gateway_node=gateway_node)
                 try:
                     print("DEBUG: Target connection established via tunnel.")
                     yield target_conn
                 finally:
                     target_conn.close()
             finally:
                 gateway_conn.close()
        else:
             print("DEBUG: Attempting direct SSH connection...")
             # Direct connection
             conn = await self._create_client_connection(node)
             try:
                 yield conn
             finally:
                 conn.close()

    async def execute_command(self, node: Node, command: str, gateway_node: Node = None) -> str:
        """
        Executes a command on the remote node and returns stdout.
        """
        async for conn in self.connection_context(node, gateway_node):
            result = await conn.run(command)
            if result.exit_status != 0:
                logger.error(f"Command failed on {node.host}: {result.stderr}")
                raise Exception(f"Command failed: {result.stderr}")
            return result.stdout

    async def stream_log(self, node: Node, log_path: str, gateway_node: Node = None) -> AsyncGenerator[str, None]:
        """
        Streams the tail of a log file from the remote node.
        """
        async for conn in self.connection_context(node, gateway_node):
            # simple tail -f
            async with conn.create_process(f"tail -f {log_path}", stderr=asyncssh.STDOUT) as process:
                async for line in process.stdout:
                    yield line

    async def test_connection(self, node: Node, gateway_node: Node = None) -> bool:
        """
        Tests connectivity to the node. Returns True if successful, raises exception otherwise.
        """
        async for conn in self.connection_context(node, gateway_node):
            return True
        return False

ssh_manager = SSHManager()
