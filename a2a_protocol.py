# a2a_protocol.py
import json
import socket
import threading
import time
from dataclasses import dataclass
from typing import Dict, Any, Optional
from enum import Enum

class MessageType(Enum):
    """A2A Protocol message types"""
    COMMAND = "command"
    RESPONSE = "response"
    STATUS = "status"
    ERROR = "error"
    HEARTBEAT = "heartbeat"
    DATA = "data"

@dataclass
class A2AMessage:
    """A2A Protocol message structure"""
    message_id: str
    sender: str
    receiver: str
    message_type: MessageType
    content: Dict[str, Any]
    timestamp: float
    correlation_id: Optional[str] = None
    
    def to_dict(self):
        return {
            'message_id': self.message_id,
            'sender': self.sender,
            'receiver': self.receiver,
            'message_type': self.message_type.value,
            'content': self.content,
            'timestamp': self.timestamp,
            'correlation_id': self.correlation_id
        }
    
    @classmethod
    def from_dict(cls, data: Dict):
        return cls(
            message_id=data['message_id'],
            sender=data['sender'],
            receiver=data['receiver'],
            message_type=MessageType(data['message_type']),
            content=data['content'],
            timestamp=data['timestamp'],
            correlation_id=data.get('correlation_id')
        )

class A2AAgent:
    """
    Agent-to-Agent communication protocol implementation
    """
    
    def __init__(self, agent_id: str, host: str = 'localhost', port: int = 8000):
        self.agent_id = agent_id
        self.host = host
        self.port = port
        self.peers = {}  # agent_id -> (host, port)
        self.message_handlers = {}
        self.is_running = False
        self.server_socket = None
        self.message_queue = []
        
        # Register default handlers
        self.register_handler(MessageType.COMMAND, self._handle_command)
        self.register_handler(MessageType.STATUS, self._handle_status)
        self.register_handler(MessageType.HEARTBEAT, self._handle_heartbeat)
    
    def register_handler(self, message_type: MessageType, handler):
        """Register a message handler"""
        self.message_handlers[message_type] = handler
    
    def add_peer(self, agent_id: str, host: str, port: int):
        """Add another agent as a peer"""
        self.peers[agent_id] = (host, port)
    
    def start(self):
        """Start the A2A server"""
        self.is_running = True
        
        # Start server thread
        server_thread = threading.Thread(target=self._run_server)
        server_thread.daemon = True
        server_thread.start()
        
        # Start heartbeat thread
        heartbeat_thread = threading.Thread(target=self._send_heartbeats)
        heartbeat_thread.daemon = True
        heartbeat_thread.start()
        
        print(f"A2A Agent {self.agent_id} started on {self.host}:{self.port}")
    
    def stop(self):
        """Stop the A2A server"""
        self.is_running = False
        if self.server_socket:
            self.server_socket.close()
    
    def send_message(self, receiver: str, message_type: MessageType, content: Dict) -> bool:
        """Send a message to another agent"""
        if receiver not in self.peers:
            print(f"Unknown peer: {receiver}")
            return False
        
        peer_host, peer_port = self.peers[receiver]
        message = A2AMessage(
            message_id=self._generate_message_id(),
            sender=self.agent_id,
            receiver=receiver,
            message_type=message_type,
            content=content,
            timestamp=time.time()
        )
        
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((peer_host, peer_port))
                s.sendall(json.dumps(message.to_dict()).encode('utf-8'))
            
            print(f"Sent {message_type.value} to {receiver}")
            return True
            
        except Exception as e:
            print(f"Error sending message to {receiver}: {e}")
            return False
    
    def broadcast(self, message_type: MessageType, content: Dict):
        """Broadcast message to all peers"""
        for peer in self.peers:
            self.send_message(peer, message_type, content)
    
    def _run_server(self):
        """Run the A2A server"""
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        
        while self.is_running:
            try:
                client_socket, address = self.server_socket.accept()
                client_thread = threading.Thread(
                    target=self._handle_client,
                    args=(client_socket, address)
                )
                client_thread.daemon = True
                client_thread.start()
            except:
                break
    
    def _handle_client(self, client_socket, address):
        """Handle incoming client connection"""
        try:
            data = b''
            while True:
                chunk = client_socket.recv(4096)
                if not chunk:
                    break
                data += chunk
            
            if data:
                message_dict = json.loads(data.decode('utf-8'))
                message = A2AMessage.from_dict(message_dict)
                self._process_message(message)
                
        except Exception as e:
            print(f"Error handling client {address}: {e}")
        finally:
            client_socket.close()
    
    def _process_message(self, message: A2AMessage):
        """Process incoming message"""
        print(f"Received {message.message_type.value} from {message.sender}")
        
        # Add to message queue
        self.message_queue.append(message)
        
        # Handle based on message type
        handler = self.message_handlers.get(message.message_type)
        if handler:
            response = handler(message)
            if response and message.sender in self.peers:
                self.send_message(
                    message.sender,
                    MessageType.RESPONSE,
                    {'response': response, 'original_message_id': message.message_id}
                )
    
    def _handle_command(self, message: A2AMessage) -> Dict:
        """Handle command messages"""
        command = message.content.get('command', '')
        print(f"Executing command from {message.sender}: {command}")
        
        # Simulate command execution
        # In real implementation, this would execute actual commands
        return {
            'status': 'success',
            'result': f"Command '{command}' executed",
            'execution_time': time.time() - message.timestamp
        }
    
    def _handle_status(self, message: A2AMessage) -> Dict:
        """Handle status messages"""
        return {
            'agent_id': self.agent_id,
            'status': 'active',
            'uptime': time.time() - message.timestamp,
            'queue_length': len(self.message_queue)
        }
    
    def _handle_heartbeat(self, message: A2AMessage) -> Dict:
        """Handle heartbeat messages"""
        return {'status': 'alive', 'timestamp': time.time()}
    
    def _send_heartbeats(self):
        """Send periodic heartbeats to all peers"""
        while self.is_running:
            time.sleep(30)  # Every 30 seconds
            self.broadcast(MessageType.HEARTBEAT, {'agent_id': self.agent_id})
    
    def _generate_message_id(self) -> str:
        """Generate unique message ID"""
        import uuid
        return str(uuid.uuid4())

class A2AManager:
    """
    Manages multiple A2A agents for Optimus Prime
    """
    
    def __init__(self):
        self.agents = {}
    
    def register_agent(self, agent_id: str, agent_type: str, host: str = 'localhost', port: int = None):
        """Register a new agent"""
        if port is None:
            port = 8000 + len(self.agents)  # Auto-assign port
        
        agent = A2AAgent(agent_id, host, port)
        
        # Connect to existing agents
        for existing_id, existing_agent in self.agents.items():
            agent.add_peer(existing_id, existing_agent.host, existing_agent.port)
            existing_agent.add_peer(agent_id, host, port)
        
        self.agents[agent_id] = {
            'agent': agent,
            'type': agent_type,
            'host': host,
            'port': port
        }
        
        return agent
    
    def start_all_agents(self):
        """Start all registered agents"""
        for agent_info in self.agents.values():
            agent_info['agent'].start()
    
    def get_agent(self, agent_id: str) -> Optional[A2AAgent]:
        """Get agent by ID"""
        return self.agents.get(agent_id, {}).get('agent')
    
    def send_command(self, from_agent: str, to_agent: str, command: str, params: Dict = None):
        """Send command between agents"""
        if params is None:
            params = {}
        
        if from_agent in self.agents and to_agent in self.agents:
            source_agent = self.agents[from_agent]['agent']
            return source_agent.send_message(
                to_agent,
                MessageType.COMMAND,
                {'command': command, 'parameters': params}
            )
        return False
    
    def get_agent_statuses(self):
        """Get status of all agents"""
        statuses = {}
        for agent_id, info in self.agents.items():
            statuses[agent_id] = {
                'type': info['type'],
                'host': info['host'],
                'port': info['port'],
                'peers': list(info['agent'].peers.keys())
            }
        return statuses