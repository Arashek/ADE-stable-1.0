from typing import Dict, Any, Optional
import json
from ..services.codebase_awareness import CodebaseAwarenessService, Symbol

class CodebaseHandler:
    def __init__(self, codebase_service: CodebaseAwarenessService):
        self.codebase_service = codebase_service

    def handle_message(self, event: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Handle incoming WebSocket messages related to codebase awareness."""
        handlers = {
            'codebase:analyze-file': self._handle_analyze_file,
            'codebase:get-dependencies': self._handle_get_dependencies,
            'codebase:get-symbols': self._handle_get_symbols,
            'codebase:get-structure': self._handle_get_structure,
            'codebase:find-references': self._handle_find_references,
            'codebase:get-definition': self._handle_get_definition,
            'codebase:file-changes': self._handle_file_changes
        }

        handler = handlers.get(event)
        if handler:
            return handler(data)
        return None

    def _handle_analyze_file(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle file analysis request."""
        file_path = data.get('path')
        if not file_path:
            return {'error': 'File path is required'}

        try:
            context = self.codebase_service.analyze_file(file_path)
            return {
                'path': context.path,
                'dependencies': context.dependencies,
                'imports': context.imports,
                'exports': context.exports,
                'symbols': [self._symbol_to_dict(s) for s in context.symbols]
            }
        except Exception as e:
            return {'error': str(e)}

    def _handle_get_dependencies(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle dependencies request."""
        file_path = data.get('path')
        if not file_path:
            return {'error': 'File path is required'}

        try:
            dependencies = self.codebase_service.get_dependencies(file_path)
            return {'dependencies': dependencies}
        except Exception as e:
            return {'error': str(e)}

    def _handle_get_symbols(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle symbols request."""
        file_path = data.get('path')
        if not file_path:
            return {'error': 'File path is required'}

        try:
            symbols = self.codebase_service.get_symbols(file_path)
            return {'symbols': [self._symbol_to_dict(s) for s in symbols]}
        except Exception as e:
            return {'error': str(e)}

    def _handle_get_structure(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle project structure request."""
        try:
            structure = self.codebase_service.project_structure
            return {
                'files': structure['files'],
                'directories': structure['directories'],
                'dependencies': structure['dependencies'],
                'symbols': {
                    path: [self._symbol_to_dict(s) for s in symbols]
                    for path, symbols in structure['symbols'].items()
                }
            }
        except Exception as e:
            return {'error': str(e)}

    def _handle_find_references(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle find references request."""
        symbol_data = data.get('symbol')
        if not symbol_data:
            return {'error': 'Symbol data is required'}

        try:
            symbol = self._dict_to_symbol(symbol_data)
            references = self.codebase_service.find_references(symbol)
            return {'references': [self._symbol_to_dict(r) for r in references]}
        except Exception as e:
            return {'error': str(e)}

    def _handle_get_definition(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle get definition request."""
        symbol_data = data.get('symbol')
        if not symbol_data:
            return {'error': 'Symbol data is required'}

        try:
            symbol = self._dict_to_symbol(symbol_data)
            definition = self.codebase_service.get_definition(symbol)
            return {'definition': self._symbol_to_dict(definition) if definition else None}
        except Exception as e:
            return {'error': str(e)}

    def _handle_file_changes(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle file changes notification."""
        file_path = data.get('path')
        change_type = data.get('type')
        content = data.get('content')

        if not file_path or not change_type:
            return {'error': 'File path and change type are required'}

        try:
            self.codebase_service.handle_file_change(file_path, change_type, content)
            return {'status': 'success'}
        except Exception as e:
            return {'error': str(e)}

    def _symbol_to_dict(self, symbol: Symbol) -> Dict[str, Any]:
        """Convert a Symbol object to a dictionary."""
        if not symbol:
            return None
        return {
            'name': symbol.name,
            'type': symbol.type,
            'location': symbol.location,
            'documentation': symbol.documentation
        }

    def _dict_to_symbol(self, data: Dict[str, Any]) -> Symbol:
        """Convert a dictionary to a Symbol object."""
        return Symbol(
            name=data['name'],
            type=data['type'],
            location=data['location'],
            documentation=data.get('documentation')
        ) 