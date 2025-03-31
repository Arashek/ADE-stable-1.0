from typing import Dict, Any, List, Optional, Tuple
from .language_servers import LanguageServer

class RubyLanguageServer(LanguageServer):
    """Ruby language server using Solargraph."""
    def __init__(self):
        super().__init__(
            server_path="solargraph",
            server_args=["socket", "--port", "7658"]
        )

    async def diagnose(self, code: str, file_path: Optional[str] = None, config: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Get diagnostics for Ruby code."""
        request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "textDocument/diagnostic",
            "params": {
                "textDocument": {
                    "uri": f"file://{file_path}" if file_path else "file:///tmp/temp.rb",
                    "languageId": "ruby",
                    "version": 1,
                    "text": code
                }
            }
        }
        await self.send_request(request)
        response = await self.receive_response()
        return response.get("result", {}).get("diagnostics", [])

    async def format(self, code: str, file_path: Optional[str] = None, style_config: Optional[Dict[str, Any]] = None) -> Tuple[str, List[Dict[str, Any]]]:
        """Format Ruby code using rubocop."""
        request = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "textDocument/formatting",
            "params": {
                "textDocument": {
                    "uri": f"file://{file_path}" if file_path else "file:///tmp/temp.rb",
                    "languageId": "ruby",
                    "version": 1,
                    "text": code
                },
                "options": style_config or {
                    "tabSize": 2,
                    "insertSpaces": True
                }
            }
        }
        await self.send_request(request)
        response = await self.receive_response()
        changes = response.get("result", [])
        return code, changes

    async def complete(self, code: str, position: Dict[str, int], context: Optional[Dict[str, Any]] = None) -> Tuple[List[Dict[str, Any]], List[str]]:
        """Get completion suggestions for Ruby code."""
        request = {
            "jsonrpc": "2.0",
            "id": 5,
            "method": "textDocument/completion",
            "params": {
                "textDocument": {
                    "uri": "file:///tmp/temp.rb",
                    "languageId": "ruby",
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
        """Get hover information for Ruby code."""
        request = {
            "jsonrpc": "2.0",
            "id": 6,
            "method": "textDocument/hover",
            "params": {
                "textDocument": {
                    "uri": "file:///tmp/temp.rb",
                    "languageId": "ruby",
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
        """Find definition locations for Ruby code."""
        request = {
            "jsonrpc": "2.0",
            "id": 7,
            "method": "textDocument/definition",
            "params": {
                "textDocument": {
                    "uri": "file:///tmp/temp.rb",
                    "languageId": "ruby",
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

class SwiftLanguageServer(LanguageServer):
    """Swift language server using SourceKit-LSP."""
    def __init__(self):
        super().__init__(
            server_path="sourcekit-lsp",
            server_args=["--stdio"]
        )

    async def diagnose(self, code: str, file_path: Optional[str] = None, config: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Get diagnostics for Swift code."""
        request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "textDocument/diagnostic",
            "params": {
                "textDocument": {
                    "uri": f"file://{file_path}" if file_path else "file:///tmp/temp.swift",
                    "languageId": "swift",
                    "version": 1,
                    "text": code
                }
            }
        }
        await self.send_request(request)
        response = await self.receive_response()
        return response.get("result", {}).get("diagnostics", [])

    async def format(self, code: str, file_path: Optional[str] = None, style_config: Optional[Dict[str, Any]] = None) -> Tuple[str, List[Dict[str, Any]]]:
        """Format Swift code using swift-format."""
        request = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "textDocument/formatting",
            "params": {
                "textDocument": {
                    "uri": f"file://{file_path}" if file_path else "file:///tmp/temp.swift",
                    "languageId": "swift",
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
        """Get completion suggestions for Swift code."""
        request = {
            "jsonrpc": "2.0",
            "id": 5,
            "method": "textDocument/completion",
            "params": {
                "textDocument": {
                    "uri": "file:///tmp/temp.swift",
                    "languageId": "swift",
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
        """Get hover information for Swift code."""
        request = {
            "jsonrpc": "2.0",
            "id": 6,
            "method": "textDocument/hover",
            "params": {
                "textDocument": {
                    "uri": "file:///tmp/temp.swift",
                    "languageId": "swift",
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
        """Find definition locations for Swift code."""
        request = {
            "jsonrpc": "2.0",
            "id": 7,
            "method": "textDocument/definition",
            "params": {
                "textDocument": {
                    "uri": "file:///tmp/temp.swift",
                    "languageId": "swift",
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

class KotlinLanguageServer(LanguageServer):
    """Kotlin language server using Kotlin Language Server."""
    def __init__(self):
        super().__init__(
            server_path="kotlin-language-server",
            server_args=["--stdio"]
        )

    async def diagnose(self, code: str, file_path: Optional[str] = None, config: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Get diagnostics for Kotlin code."""
        request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "textDocument/diagnostic",
            "params": {
                "textDocument": {
                    "uri": f"file://{file_path}" if file_path else "file:///tmp/temp.kt",
                    "languageId": "kotlin",
                    "version": 1,
                    "text": code
                }
            }
        }
        await self.send_request(request)
        response = await self.receive_response()
        return response.get("result", {}).get("diagnostics", [])

    async def format(self, code: str, file_path: Optional[str] = None, style_config: Optional[Dict[str, Any]] = None) -> Tuple[str, List[Dict[str, Any]]]:
        """Format Kotlin code using ktlint."""
        request = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "textDocument/formatting",
            "params": {
                "textDocument": {
                    "uri": f"file://{file_path}" if file_path else "file:///tmp/temp.kt",
                    "languageId": "kotlin",
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
        """Get completion suggestions for Kotlin code."""
        request = {
            "jsonrpc": "2.0",
            "id": 5,
            "method": "textDocument/completion",
            "params": {
                "textDocument": {
                    "uri": "file:///tmp/temp.kt",
                    "languageId": "kotlin",
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
        """Get hover information for Kotlin code."""
        request = {
            "jsonrpc": "2.0",
            "id": 6,
            "method": "textDocument/hover",
            "params": {
                "textDocument": {
                    "uri": "file:///tmp/temp.kt",
                    "languageId": "kotlin",
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
        """Find definition locations for Kotlin code."""
        request = {
            "jsonrpc": "2.0",
            "id": 7,
            "method": "textDocument/definition",
            "params": {
                "textDocument": {
                    "uri": "file:///tmp/temp.kt",
                    "languageId": "kotlin",
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

class ScalaLanguageServer(LanguageServer):
    """Scala language server using Metals."""
    def __init__(self):
        super().__init__(
            server_path="metals",
            server_args=["--stdio"]
        )

    async def diagnose(self, code: str, file_path: Optional[str] = None, config: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Get diagnostics for Scala code."""
        request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "textDocument/diagnostic",
            "params": {
                "textDocument": {
                    "uri": f"file://{file_path}" if file_path else "file:///tmp/temp.scala",
                    "languageId": "scala",
                    "version": 1,
                    "text": code
                }
            }
        }
        await self.send_request(request)
        response = await self.receive_response()
        return response.get("result", {}).get("diagnostics", [])

    async def format(self, code: str, file_path: Optional[str] = None, style_config: Optional[Dict[str, Any]] = None) -> Tuple[str, List[Dict[str, Any]]]:
        """Format Scala code using scalafmt."""
        request = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "textDocument/formatting",
            "params": {
                "textDocument": {
                    "uri": f"file://{file_path}" if file_path else "file:///tmp/temp.scala",
                    "languageId": "scala",
                    "version": 1,
                    "text": code
                },
                "options": style_config or {
                    "tabSize": 2,
                    "insertSpaces": True
                }
            }
        }
        await self.send_request(request)
        response = await self.receive_response()
        changes = response.get("result", [])
        return code, changes

    async def complete(self, code: str, position: Dict[str, int], context: Optional[Dict[str, Any]] = None) -> Tuple[List[Dict[str, Any]], List[str]]:
        """Get completion suggestions for Scala code."""
        request = {
            "jsonrpc": "2.0",
            "id": 5,
            "method": "textDocument/completion",
            "params": {
                "textDocument": {
                    "uri": "file:///tmp/temp.scala",
                    "languageId": "scala",
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
        """Get hover information for Scala code."""
        request = {
            "jsonrpc": "2.0",
            "id": 6,
            "method": "textDocument/hover",
            "params": {
                "textDocument": {
                    "uri": "file:///tmp/temp.scala",
                    "languageId": "scala",
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
        """Find definition locations for Scala code."""
        request = {
            "jsonrpc": "2.0",
            "id": 7,
            "method": "textDocument/definition",
            "params": {
                "textDocument": {
                    "uri": "file:///tmp/temp.scala",
                    "languageId": "scala",
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