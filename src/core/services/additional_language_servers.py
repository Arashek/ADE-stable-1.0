from typing import Dict, Any, List, Optional, Tuple
from .language_servers import LanguageServer

class GoLanguageServer(LanguageServer):
    """Go language server using gopls."""
    def __init__(self):
        super().__init__(
            server_path="gopls",
            server_args=["serve"]
        )

    async def diagnose(self, code: str, file_path: Optional[str] = None, config: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Get diagnostics for Go code."""
        request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "textDocument/diagnostic",
            "params": {
                "textDocument": {
                    "uri": f"file://{file_path}" if file_path else "file:///tmp/temp.go",
                    "languageId": "go",
                    "version": 1,
                    "text": code
                }
            }
        }
        await self.send_request(request)
        response = await self.receive_response()
        return response.get("result", {}).get("diagnostics", [])

    async def format(self, code: str, file_path: Optional[str] = None, style_config: Optional[Dict[str, Any]] = None) -> Tuple[str, List[Dict[str, Any]]]:
        """Format Go code using gofmt."""
        request = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "textDocument/formatting",
            "params": {
                "textDocument": {
                    "uri": f"file://{file_path}" if file_path else "file:///tmp/temp.go",
                    "languageId": "go",
                    "version": 1,
                    "text": code
                },
                "options": style_config or {
                    "tabSize": 4,
                    "insertSpaces": False
                }
            }
        }
        await self.send_request(request)
        response = await self.receive_response()
        changes = response.get("result", [])
        return code, changes

    async def complete(self, code: str, position: Dict[str, int], context: Optional[Dict[str, Any]] = None) -> Tuple[List[Dict[str, Any]], List[str]]:
        """Get completion suggestions for Go code."""
        request = {
            "jsonrpc": "2.0",
            "id": 5,
            "method": "textDocument/completion",
            "params": {
                "textDocument": {
                    "uri": "file:///tmp/temp.go",
                    "languageId": "go",
                    "version": 1,
                    "text": code
                },
                "position": position,
                "context": context or {}
            }
        }
        await self.send_request(request)
        response = await self.receive_response()
        result = response.get("result", {})
        return result.get("items", []), result.get("triggerCharacters", [])

    async def hover(self, code: str, position: Dict[str, int], context: Optional[Dict[str, Any]] = None) -> Tuple[List[Dict[str, Any]], Optional[Dict[str, Any]]]:
        """Get hover information for Go code."""
        request = {
            "jsonrpc": "2.0",
            "id": 6,
            "method": "textDocument/hover",
            "params": {
                "textDocument": {
                    "uri": "file:///tmp/temp.go",
                    "languageId": "go",
                    "version": 1,
                    "text": code
                },
                "position": position
            }
        }
        await self.send_request(request)
        response = await self.receive_response()
        result = response.get("result", {})
        return result.get("contents", []), result.get("range")

    async def definition(self, code: str, position: Dict[str, int], context: Optional[Dict[str, Any]] = None) -> Tuple[List[Dict[str, Any]], Optional[str]]:
        """Find definition locations for Go code."""
        request = {
            "jsonrpc": "2.0",
            "id": 7,
            "method": "textDocument/definition",
            "params": {
                "textDocument": {
                    "uri": "file:///tmp/temp.go",
                    "languageId": "go",
                    "version": 1,
                    "text": code
                },
                "position": position
            }
        }
        await self.send_request(request)
        response = await self.receive_response()
        result = response.get("result", [])
        return result, result[0].get("uri") if result else None

    async def references(self, code: str, position: Dict[str, int], context: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Find references to a symbol."""
        request = {
            "jsonrpc": "2.0",
            "id": 8,
            "method": "textDocument/references",
            "params": {
                "textDocument": {
                    "uri": "file:///tmp/temp.go",
                    "languageId": "go",
                    "version": 1,
                    "text": code
                },
                "position": position,
                "context": {"includeDeclaration": True}
            }
        }
        await self.send_request(request)
        response = await self.receive_response()
        return response.get("result", [])

    async def rename(self, code: str, position: Dict[str, int], new_name: str) -> Dict[str, Any]:
        """Rename a symbol."""
        request = {
            "jsonrpc": "2.0",
            "id": 9,
            "method": "textDocument/rename",
            "params": {
                "textDocument": {
                    "uri": "file:///tmp/temp.go",
                    "languageId": "go",
                    "version": 1,
                    "text": code
                },
                "position": position,
                "newName": new_name
            }
        }
        await self.send_request(request)
        response = await self.receive_response()
        return response.get("result", {})

class RustLanguageServer(LanguageServer):
    """Rust language server using rust-analyzer."""
    def __init__(self):
        super().__init__(
            server_path="rust-analyzer",
            server_args=["--stdio"]
        )

    async def diagnose(self, code: str, file_path: Optional[str] = None, config: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Get diagnostics for Rust code."""
        request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "textDocument/diagnostic",
            "params": {
                "textDocument": {
                    "uri": f"file://{file_path}" if file_path else "file:///tmp/temp.rs",
                    "languageId": "rust",
                    "version": 1,
                    "text": code
                }
            }
        }
        await self.send_request(request)
        response = await self.receive_response()
        return response.get("result", {}).get("diagnostics", [])

    async def format(self, code: str, file_path: Optional[str] = None, style_config: Optional[Dict[str, Any]] = None) -> Tuple[str, List[Dict[str, Any]]]:
        """Format Rust code using rustfmt."""
        request = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "textDocument/formatting",
            "params": {
                "textDocument": {
                    "uri": f"file://{file_path}" if file_path else "file:///tmp/temp.rs",
                    "languageId": "rust",
                    "version": 1,
                    "text": code
                },
                "options": style_config or {
                    "tabSize": 4,
                    "insertSpaces": True
                }
            }
        }
        await self.send_request(request)
        response = await self.receive_response()
        changes = response.get("result", [])
        return code, changes

    async def complete(self, code: str, position: Dict[str, int], context: Optional[Dict[str, Any]] = None) -> Tuple[List[Dict[str, Any]], List[str]]:
        """Get completion suggestions for Rust code."""
        request = {
            "jsonrpc": "2.0",
            "id": 5,
            "method": "textDocument/completion",
            "params": {
                "textDocument": {
                    "uri": "file:///tmp/temp.rs",
                    "languageId": "rust",
                    "version": 1,
                    "text": code
                },
                "position": position,
                "context": context or {}
            }
        }
        await self.send_request(request)
        response = await self.receive_response()
        result = response.get("result", {})
        return result.get("items", []), result.get("triggerCharacters", [])

    async def hover(self, code: str, position: Dict[str, int], context: Optional[Dict[str, Any]] = None) -> Tuple[List[Dict[str, Any]], Optional[Dict[str, Any]]]:
        """Get hover information for Rust code."""
        request = {
            "jsonrpc": "2.0",
            "id": 6,
            "method": "textDocument/hover",
            "params": {
                "textDocument": {
                    "uri": "file:///tmp/temp.rs",
                    "languageId": "rust",
                    "version": 1,
                    "text": code
                },
                "position": position
            }
        }
        await self.send_request(request)
        response = await self.receive_response()
        result = response.get("result", {})
        return result.get("contents", []), result.get("range")

    async def definition(self, code: str, position: Dict[str, int], context: Optional[Dict[str, Any]] = None) -> Tuple[List[Dict[str, Any]], Optional[str]]:
        """Find definition locations for Rust code."""
        request = {
            "jsonrpc": "2.0",
            "id": 7,
            "method": "textDocument/definition",
            "params": {
                "textDocument": {
                    "uri": "file:///tmp/temp.rs",
                    "languageId": "rust",
                    "version": 1,
                    "text": code
                },
                "position": position
            }
        }
        await self.send_request(request)
        response = await self.receive_response()
        result = response.get("result", [])
        return result, result[0].get("uri") if result else None

    async def code_action(self, code: str, range: Dict[str, Any], context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get code actions for the given range."""
        request = {
            "jsonrpc": "2.0",
            "id": 8,
            "method": "textDocument/codeAction",
            "params": {
                "textDocument": {
                    "uri": "file:///tmp/temp.rs",
                    "languageId": "rust",
                    "version": 1,
                    "text": code
                },
                "range": range,
                "context": context
            }
        }
        await self.send_request(request)
        response = await self.receive_response()
        return response.get("result", [])

class CppLanguageServer(LanguageServer):
    """C++ language server using clangd."""
    def __init__(self):
        super().__init__(
            server_path="clangd",
            server_args=["--background-index"]
        )

    async def diagnose(self, code: str, file_path: Optional[str] = None, config: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Get diagnostics for C++ code."""
        request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "textDocument/diagnostic",
            "params": {
                "textDocument": {
                    "uri": f"file://{file_path}" if file_path else "file:///tmp/temp.cpp",
                    "languageId": "cpp",
                    "version": 1,
                    "text": code
                }
            }
        }
        await self.send_request(request)
        response = await self.receive_response()
        return response.get("result", {}).get("diagnostics", [])

    async def format(self, code: str, file_path: Optional[str] = None, style_config: Optional[Dict[str, Any]] = None) -> Tuple[str, List[Dict[str, Any]]]:
        """Format C++ code using clang-format."""
        request = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "textDocument/formatting",
            "params": {
                "textDocument": {
                    "uri": f"file://{file_path}" if file_path else "file:///tmp/temp.cpp",
                    "languageId": "cpp",
                    "version": 1,
                    "text": code
                },
                "options": style_config or {
                    "tabSize": 4,
                    "insertSpaces": True
                }
            }
        }
        await self.send_request(request)
        response = await self.receive_response()
        changes = response.get("result", [])
        return code, changes

    async def complete(self, code: str, position: Dict[str, int], context: Optional[Dict[str, Any]] = None) -> Tuple[List[Dict[str, Any]], List[str]]:
        """Get completion suggestions for C++ code."""
        request = {
            "jsonrpc": "2.0",
            "id": 5,
            "method": "textDocument/completion",
            "params": {
                "textDocument": {
                    "uri": "file:///tmp/temp.cpp",
                    "languageId": "cpp",
                    "version": 1,
                    "text": code
                },
                "position": position,
                "context": context or {}
            }
        }
        await self.send_request(request)
        response = await self.receive_response()
        result = response.get("result", {})
        return result.get("items", []), result.get("triggerCharacters", [])

    async def hover(self, code: str, position: Dict[str, int], context: Optional[Dict[str, Any]] = None) -> Tuple[List[Dict[str, Any]], Optional[Dict[str, Any]]]:
        """Get hover information for C++ code."""
        request = {
            "jsonrpc": "2.0",
            "id": 6,
            "method": "textDocument/hover",
            "params": {
                "textDocument": {
                    "uri": "file:///tmp/temp.cpp",
                    "languageId": "cpp",
                    "version": 1,
                    "text": code
                },
                "position": position
            }
        }
        await self.send_request(request)
        response = await self.receive_response()
        result = response.get("result", {})
        return result.get("contents", []), result.get("range")

    async def definition(self, code: str, position: Dict[str, int], context: Optional[Dict[str, Any]] = None) -> Tuple[List[Dict[str, Any]], Optional[str]]:
        """Find definition locations for C++ code."""
        request = {
            "jsonrpc": "2.0",
            "id": 7,
            "method": "textDocument/definition",
            "params": {
                "textDocument": {
                    "uri": "file:///tmp/temp.cpp",
                    "languageId": "cpp",
                    "version": 1,
                    "text": code
                },
                "position": position
            }
        }
        await self.send_request(request)
        response = await self.receive_response()
        result = response.get("result", [])
        return result, result[0].get("uri") if result else None

    async def semantic_highlighting(self, code: str, file_path: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get semantic highlighting information."""
        request = {
            "jsonrpc": "2.0",
            "id": 8,
            "method": "textDocument/semanticHighlighting",
            "params": {
                "textDocument": {
                    "uri": f"file://{file_path}" if file_path else "file:///tmp/temp.cpp",
                    "languageId": "cpp",
                    "version": 1,
                    "text": code
                }
            }
        }
        await self.send_request(request)
        response = await self.receive_response()
        return response.get("result", [])

class PHPLanguageServer(LanguageServer):
    """PHP language server using Intelephense."""
    def __init__(self):
        super().__init__(
            server_path="intelephense",
            server_args=["--stdio"]
        )

    async def diagnose(self, code: str, file_path: Optional[str] = None, config: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Get diagnostics for PHP code."""
        request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "textDocument/diagnostic",
            "params": {
                "textDocument": {
                    "uri": f"file://{file_path}" if file_path else "file:///tmp/temp.php",
                    "languageId": "php",
                    "version": 1,
                    "text": code
                }
            }
        }
        await self.send_request(request)
        response = await self.receive_response()
        return response.get("result", {}).get("diagnostics", [])

    async def format(self, code: str, file_path: Optional[str] = None, style_config: Optional[Dict[str, Any]] = None) -> Tuple[str, List[Dict[str, Any]]]:
        """Format PHP code using PHP_CodeSniffer."""
        request = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "textDocument/formatting",
            "params": {
                "textDocument": {
                    "uri": f"file://{file_path}" if file_path else "file:///tmp/temp.php",
                    "languageId": "php",
                    "version": 1,
                    "text": code
                },
                "options": style_config or {
                    "tabSize": 4,
                    "insertSpaces": True
                }
            }
        }
        await self.send_request(request)
        response = await self.receive_response()
        changes = response.get("result", [])
        return code, changes

    async def complete(self, code: str, position: Dict[str, int], context: Optional[Dict[str, Any]] = None) -> Tuple[List[Dict[str, Any]], List[str]]:
        """Get completion suggestions for PHP code."""
        request = {
            "jsonrpc": "2.0",
            "id": 5,
            "method": "textDocument/completion",
            "params": {
                "textDocument": {
                    "uri": "file:///tmp/temp.php",
                    "languageId": "php",
                    "version": 1,
                    "text": code
                },
                "position": position,
                "context": context or {}
            }
        }
        await self.send_request(request)
        response = await self.receive_response()
        result = response.get("result", {})
        return result.get("items", []), result.get("triggerCharacters", [])

    async def hover(self, code: str, position: Dict[str, int], context: Optional[Dict[str, Any]] = None) -> Tuple[List[Dict[str, Any]], Optional[Dict[str, Any]]]:
        """Get hover information for PHP code."""
        request = {
            "jsonrpc": "2.0",
            "id": 6,
            "method": "textDocument/hover",
            "params": {
                "textDocument": {
                    "uri": "file:///tmp/temp.php",
                    "languageId": "php",
                    "version": 1,
                    "text": code
                },
                "position": position
            }
        }
        await self.send_request(request)
        response = await self.receive_response()
        result = response.get("result", {})
        return result.get("contents", []), result.get("range")

    async def definition(self, code: str, position: Dict[str, int], context: Optional[Dict[str, Any]] = None) -> Tuple[List[Dict[str, Any]], Optional[str]]:
        """Find definition locations for PHP code."""
        request = {
            "jsonrpc": "2.0",
            "id": 7,
            "method": "textDocument/definition",
            "params": {
                "textDocument": {
                    "uri": "file:///tmp/temp.php",
                    "languageId": "php",
                    "version": 1,
                    "text": code
                },
                "position": position
            }
        }
        await self.send_request(request)
        response = await self.receive_response()
        result = response.get("result", [])
        return result, result[0].get("uri") if result else None

    async def workspace_symbol(self, query: str) -> List[Dict[str, Any]]:
        """Search for symbols in the workspace."""
        request = {
            "jsonrpc": "2.0",
            "id": 8,
            "method": "workspace/symbol",
            "params": {
                "query": query
            }
        }
        await self.send_request(request)
        response = await self.receive_response()
        return response.get("result", []) 