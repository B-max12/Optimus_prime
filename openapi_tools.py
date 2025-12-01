# openapi_tools.py
import requests
import json
import yaml
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict

@dataclass
class OpenAPIOperation:
    """OpenAPI Operation definition"""
    operation_id: str
    summary: str
    description: str
    method: str
    path: str
    parameters: List[Dict]
    request_body: Optional[Dict] = None
    responses: Optional[Dict] = None

class OpenAPIClient:
    """
    Client for OpenAPI/Swagger services
    """
    
    def __init__(self):
        self.services = {}
        self.active_connections = {}
    
    def load_openapi_spec(self, service_name: str, spec_url: str) -> bool:
        """Load OpenAPI specification from URL"""
        try:
            response = requests.get(spec_url)
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '')
                
                if 'yaml' in content_type or spec_url.endswith('.yaml') or spec_url.endswith('.yml'):
                    spec = yaml.safe_load(response.text)
                else:
                    spec = response.json()
                
                self.services[service_name] = {
                    'spec': spec,
                    'base_url': spec.get('servers', [{}])[0].get('url', ''),
                    'operations': self._parse_operations(spec)
                }
                return True
        except Exception as e:
            print(f"Error loading OpenAPI spec for {service_name}: {e}")
        return False
    
    def _parse_operations(self, spec: Dict) -> Dict[str, OpenAPIOperation]:
        """Parse operations from OpenAPI spec"""
        operations = {}
        
        if 'paths' in spec:
            for path, methods in spec['paths'].items():
                for method, details in methods.items():
                    if method.lower() in ['get', 'post', 'put', 'delete', 'patch']:
                        op_id = details.get('operationId', f"{method}_{path.replace('/', '_').strip('_')}")
                        
                        operation = OpenAPIOperation(
                            operation_id=op_id,
                            summary=details.get('summary', ''),
                            description=details.get('description', ''),
                            method=method.upper(),
                            path=path,
                            parameters=details.get('parameters', []),
                            request_body=details.get('requestBody'),
                            responses=details.get('responses', {})
                        )
                        
                        operations[op_id] = operation
        
        return operations
    
    def connect_service(self, service_name: str, api_key: str = None, 
                       auth_token: str = None) -> bool:
        """Connect to an OpenAPI service"""
        if service_name not in self.services:
            print(f"Service {service_name} not loaded")
            return False
        
        self.active_connections[service_name] = {
            'api_key': api_key,
            'auth_token': auth_token,
            'connected_at': json.dumps(requests)
        }
        return True
    
    def call_operation(self, service_name: str, operation_id: str, 
                      params: Dict = None, data: Dict = None) -> Optional[Dict]:
        """Call an OpenAPI operation"""
        if service_name not in self.services:
            print(f"Service {service_name} not loaded")
            return None
        
        if operation_id not in self.services[service_name]['operations']:
            print(f"Operation {operation_id} not found in {service_name}")
            return None
        
        operation = self.services[service_name]['operations'][operation_id]
        base_url = self.services[service_name]['base_url']
        
        # Build URL
        url = f"{base_url}{operation.path}"
        
        # Replace path parameters
        if params:
            for param in operation.parameters:
                if param.get('in') == 'path' and param.get('name') in params:
                    url = url.replace(f"{{{param['name']}}}", str(params[param['name']]))
        
        # Prepare headers
        headers = {}
        if service_name in self.active_connections:
            conn = self.active_connections[service_name]
            if conn.get('api_key'):
                headers['X-API-Key'] = conn['api_key']
            if conn.get('auth_token'):
                headers['Authorization'] = f"Bearer {conn['auth_token']}"
        
        headers['Content-Type'] = 'application/json'
        
        try:
            if operation.method == 'GET':
                response = requests.get(url, headers=headers, params=params)
            elif operation.method == 'POST':
                response = requests.post(url, headers=headers, json=data or params)
            elif operation.method == 'PUT':
                response = requests.put(url, headers=headers, json=data or params)
            elif operation.method == 'DELETE':
                response = requests.delete(url, headers=headers, params=params)
            elif operation.method == 'PATCH':
                response = requests.patch(url, headers=headers, json=data or params)
            else:
                print(f"Unsupported method: {operation.method}")
                return None
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"API call failed: {response.status_code} - {response.text}")
                return {'error': f"API call failed: {response.status_code}"}
                
        except Exception as e:
            print(f"Error calling {operation_id}: {e}")
            return None
    
    def list_operations(self, service_name: str) -> List[Dict]:
        """List available operations for a service"""
        if service_name in self.services:
            return [
                {
                    'operation_id': op.operation_id,
                    'summary': op.summary,
                    'method': op.method,
                    'path': op.path,
                    'description': op.description[:100] + '...' if len(op.description) > 100 else op.description
                }
                for op in self.services[service_name]['operations'].values()
            ]
        return []
    
    def get_operation_details(self, service_name: str, operation_id: str) -> Optional[Dict]:
        """Get detailed information about an operation"""
        if service_name in self.services and operation_id in self.services[service_name]['operations']:
            operation = self.services[service_name]['operations'][operation_id]
            return asdict(operation)
        return None

class OpenAPIToolGenerator:
    """
    Generates tools from OpenAPI specifications
    """
    
    def __init__(self):
        self.openapi_client = OpenAPIClient()
    
    def register_service(self, service_name: str, spec_url: str, 
                        api_key: str = None) -> bool:
        """Register and load an OpenAPI service"""
        if self.openapi_client.load_openapi_spec(service_name, spec_url):
            if api_key:
                self.openapi_client.connect_service(service_name, api_key)
            return True
        return False
    
    def generate_tool_from_operation(self, service_name: str, operation_id: str):
        """Generate a tool wrapper for an OpenAPI operation"""
        if service_name not in self.openapi_client.services:
            return None
        
        if operation_id not in self.openapi_client.services[service_name]['operations']:
            return None
        
        operation = self.openapi_client.services[service_name]['operations'][operation_id]
        
        # Create tool definition
        tool_def = {
            'name': f"{service_name}_{operation_id}",
            'description': operation.summary or operation.description,
            'operation_id': operation_id,
            'service': service_name,
            'method': operation.method,
            'path': operation.path,
            'parameters': self._extract_parameters(operation),
            'execute': lambda **kwargs: self._execute_operation(
                service_name, operation_id, kwargs
            )
        }
        
        return tool_def
    
    def _extract_parameters(self, operation: OpenAPIOperation) -> List[Dict]:
        """Extract parameter definitions from operation"""
        params = []
        
        # Path parameters
        for param in operation.parameters:
            if param.get('in') == 'path':
                params.append({
                    'name': param['name'],
                    'type': param.get('schema', {}).get('type', 'string'),
                    'required': param.get('required', False),
                    'description': param.get('description', ''),
                    'in': 'path'
                })
        
        # Query parameters
        for param in operation.parameters:
            if param.get('in') == 'query':
                params.append({
                    'name': param['name'],
                    'type': param.get('schema', {}).get('type', 'string'),
                    'required': param.get('required', False),
                    'description': param.get('description', ''),
                    'in': 'query'
                })
        
        # Request body parameters
        if operation.request_body:
            content = operation.request_body.get('content', {})
            if 'application/json' in content:
                schema = content['application/json'].get('schema', {})
                if 'properties' in schema:
                    for prop_name, prop_schema in schema['properties'].items():
                        params.append({
                            'name': prop_name,
                            'type': prop_schema.get('type', 'string'),
                            'required': prop_name in schema.get('required', []),
                            'description': prop_schema.get('description', ''),
                            'in': 'body'
                        })
        
        return params
    
    def _execute_operation(self, service_name: str, operation_id: str, kwargs: Dict):
        """Execute the OpenAPI operation"""
        # Separate path, query, and body parameters
        path_params = {}
        query_params = {}
        body_params = {}
        
        operation = self.openapi_client.services[service_name]['operations'][operation_id]
        
        for param in operation.parameters:
            if param.get('in') == 'path' and param['name'] in kwargs:
                path_params[param['name']] = kwargs[param['name']]
            elif param.get('in') == 'query' and param['name'] in kwargs:
                query_params[param['name']] = kwargs[param['name']]
        
        if operation.request_body:
            content = operation.request_body.get('content', {})
            if 'application/json' in content:
                schema = content['application/json'].get('schema', {})
                if 'properties' in schema:
                    for prop_name in schema['properties']:
                        if prop_name in kwargs:
                            body_params[prop_name] = kwargs[prop_name]
        
        # Call the operation
        return self.openapi_client.call_operation(
            service_name, operation_id,
            params={**path_params, **query_params},
            data=body_params if body_params else None
        )
    
    def generate_all_tools(self, service_name: str) -> List[Dict]:
        """Generate tools for all operations in a service"""
        tools = []
        
        if service_name in self.openapi_client.services:
            operations = self.openapi_client.services[service_name]['operations']
            
            for operation_id in operations:
                tool = self.generate_tool_from_operation(service_name, operation_id)
                if tool:
                    tools.append(tool)
        
        return tools

# Example OpenAPI services for Optimus Prime
OPENAPI_SERVICES = {
    'weather': {
        'name': 'weather_api',
        'spec_url': 'https://api.openweathermap.org/api/v3/openapi.yaml',
        'description': 'Weather forecast API'
    },
    'news': {
        'name': 'news_api',
        'spec_url': 'https://newsapi.org/docs/openapi.yaml',
        'description': 'News headlines API'
    },
    'currency': {
        'name': 'currency_api',
        'spec_url': 'https://api.exchangerate-api.com/v4/latest/openapi.yaml',
        'description': 'Currency exchange API'
    },
    'github': {
        'name': 'github_api',
        'spec_url': 'https://api.github.com/openapi.yaml',
        'description': 'GitHub REST API'
    }
}