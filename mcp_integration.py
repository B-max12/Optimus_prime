# mcp_integration.py
import json
import requests
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

@dataclass
class Tool:
    """MCP Tool definition"""
    name: str
    description: str
    input_schema: Dict
    output_schema: Dict
    
    def to_mcp_format(self):
        return {
            'name': self.name,
            'description': self.description,
            'inputSchema': self.input_schema,
            'outputSchema': self.output_schema
        }

class MCPClient:
    """
    MCP Client for connecting to Model Context Protocol servers
    """
    
    def __init__(self, server_url: str = "http://localhost:3000"):
        self.server_url = server_url
        self.session_id = None
        self.available_tools = []
    
    def connect(self) -> bool:
        """Connect to MCP server"""
        try:
            response = requests.post(
                f"{self.server_url}/connect",
                json={'client': 'optimus_prime'}
            )
            if response.status_code == 200:
                data = response.json()
                self.session_id = data.get('session_id')
                self.available_tools = data.get('tools', [])
                return True
        except Exception as e:
            print(f"MCP Connection error: {e}")
        return False
    
    def list_tools(self) -> List[Dict]:
        """List available tools from MCP server"""
        try:
            response = requests.get(
                f"{self.server_url}/tools",
                headers={'X-Session-ID': self.session_id}
            )
            if response.status_code == 200:
                self.available_tools = response.json().get('tools', [])
                return self.available_tools
        except Exception as e:
            print(f"MCP List tools error: {e}")
        return []
    
    def call_tool(self, tool_name: str, arguments: Dict) -> Optional[Dict]:
        """Call a tool through MCP"""
        try:
            response = requests.post(
                f"{self.server_url}/tools/{tool_name}/call",
                headers={'X-Session-ID': self.session_id},
                json={'arguments': arguments}
            )
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"MCP Tool call error for {tool_name}: {e}")
        return None
    
    def get_context(self, query: str) -> Optional[Dict]:
        """Get relevant context for a query"""
        try:
            response = requests.post(
                f"{self.server_url}/context",
                headers={'X-Session-ID': self.session_id},
                json={'query': query}
            )
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"MCP Context error: {e}")
        return None
    
    def disconnect(self):
        """Disconnect from MCP server"""
        if self.session_id:
            try:
                requests.post(
                    f"{self.server_url}/disconnect",
                    headers={'X-Session-ID': self.session_id}
                )
            except:
                pass
            self.session_id = None

class MCPServerEmulator:
    """
    Simple MCP Server emulator for demonstration
    """
    
    def __init__(self):
        self.tools = self._initialize_tools()
        self.sessions = {}
    
    def _initialize_tools(self) -> Dict[str, Tool]:
        """Initialize MCP tools for Optimus Prime"""
        tools = {
            'search_web': Tool(
                name='search_web',
                description='Search the web for information',
                input_schema={
                    'type': 'object',
                    'properties': {
                        'query': {'type': 'string', 'description': 'Search query'},
                        'limit': {'type': 'integer', 'description': 'Number of results'}
                    },
                    'required': ['query']
                },
                output_schema={
                    'type': 'object',
                    'properties': {
                        'results': {'type': 'array', 'items': {'type': 'string'}},
                        'count': {'type': 'integer'}
                    }
                }
            ),
            'analyze_text': Tool(
                name='analyze_text',
                description='Analyze text for sentiment, entities, etc.',
                input_schema={
                    'type': 'object',
                    'properties': {
                        'text': {'type': 'string', 'description': 'Text to analyze'},
                        'analysis_type': {'type': 'string', 'enum': ['sentiment', 'entities', 'summary']}
                    },
                    'required': ['text']
                },
                output_schema={
                    'type': 'object',
                    'properties': {
                        'analysis': {'type': 'object'},
                        'summary': {'type': 'string'}
                    }
                }
            ),
            'code_generation': Tool(
                name='code_generation',
                description='Generate code based on requirements',
                input_schema={
                    'type': 'object',
                    'properties': {
                        'description': {'type': 'string', 'description': 'Code description'},
                        'language': {'type': 'string', 'description': 'Programming language'},
                        'complexity': {'type': 'string', 'enum': ['simple', 'medium', 'complex']}
                    },
                    'required': ['description', 'language']
                },
                output_schema={
                    'type': 'object',
                    'properties': {
                        'code': {'type': 'string'},
                        'explanation': {'type': 'string'},
                        'language': {'type': 'string'}
                    }
                }
            )
        }
        return tools
    
    def handle_request(self, endpoint: str, data: Dict, session_id: str = None) -> Dict:
        """Handle MCP requests"""
        if endpoint == '/connect':
            session_id = f"session_{len(self.sessions)}"
            self.sessions[session_id] = {
                'created_at': json.dumps(data),
                'last_active': json.dumps(data)
            }
            return {
                'session_id': session_id,
                'tools': [tool.to_mcp_format() for tool in self.tools.values()]
            }
        
        elif endpoint == '/tools':
            if session_id not in self.sessions:
                return {'error': 'Invalid session'}
            return {'tools': [tool.to_mcp_format() for tool in self.tools.values()]}
        
        elif endpoint.startswith('/tools/') and '/call' in endpoint:
            tool_name = endpoint.split('/')[2]
            if tool_name in self.tools:
                return self._execute_tool(tool_name, data.get('arguments', {}))
        
        elif endpoint == '/context':
            return self._get_context(data.get('query', ''))
        
        elif endpoint == '/disconnect':
            if session_id in self.sessions:
                del self.sessions[session_id]
            return {'status': 'disconnected'}
        
        return {'error': 'Invalid endpoint'}
    
    def _execute_tool(self, tool_name: str, arguments: Dict) -> Dict:
        """Execute MCP tool"""
        if tool_name == 'search_web':
            query = arguments.get('query', '')
            limit = arguments.get('limit', 3)
            # Simulate web search
            return {
                'results': [
                    f"Result 1 for: {query}",
                    f"Result 2 for: {query}",
                    f"Result 3 for: {query}"
                ][:limit],
                'count': limit
            }
        
        elif tool_name == 'analyze_text':
            text = arguments.get('text', '')
            analysis_type = arguments.get('analysis_type', 'sentiment')
            
            if analysis_type == 'sentiment':
                return {
                    'analysis': {
                        'sentiment': 'positive',
                        'confidence': 0.85,
                        'keywords': text.split()[:5]
                    },
                    'summary': f"Text appears positive with keywords: {', '.join(text.split()[:3])}"
                }
        
        elif tool_name == 'code_generation':
            description = arguments.get('description', '')
            language = arguments.get('language', 'python')
            
            return {
                'code': f"# Generated {language} code\n# {description}\ndef main():\n    print('Hello from generated code!')\n\nif __name__ == '__main__':\n    main()",
                'explanation': f"Generated {language} code for: {description}",
                'language': language
            }
        
        return {'error': f'Tool {tool_name} not implemented'}

    def _get_context(self, query: str) -> Dict:
        """Get context for query"""
        # Simulate context retrieval
        return {
            'context': [
                f"Relevant information about: {query}",
                "Additional context from knowledge base",
                "Historical interaction data"
            ],
            'relevance_score': 0.92
        }

class MCPManager:
    """
    Integrates MCP with Optimus Prime
    """
    
    def __init__(self):
        self.mcp_client = MCPClient()
        self.mcp_server = MCPServerEmulator()
        self.is_connected = False
    
    def connect_to_server(self, server_url: str = None):
        """Connect to external MCP server"""
        if server_url:
            self.mcp_client.server_url = server_url
        
        self.is_connected = self.mcp_client.connect()
        return self.is_connected
    
    def use_local_server(self):
        """Use local MCP server emulator"""
        self.is_connected = True
        return True
    
    def get_tools(self):
        """Get available MCP tools"""
        if self.is_connected:
            return self.mcp_client.list_tools()
        else:
            return [tool.to_mcp_format() for tool in self.mcp_server.tools.values()]
    
    def execute_mcp_tool(self, tool_name: str, arguments: Dict):
        """Execute MCP tool"""
        if self.is_connected and hasattr(self.mcp_client, 'call_tool'):
            return self.mcp_client.call_tool(tool_name, arguments)
        else:
            return self.mcp_server.handle_request(
                f'/tools/{tool_name}/call',
                {'arguments': arguments},
                'local_session'
            )
    
    def get_context_for_query(self, query: str):
        """Get MCP context for query"""
        if self.is_connected and hasattr(self.mcp_client, 'get_context'):
            return self.mcp_client.get_context(query)
        else:
            return self.mcp_server.handle_request(
                '/context',
                {'query': query},
                'local_session'
            )