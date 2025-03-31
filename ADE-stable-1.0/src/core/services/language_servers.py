import logging
from typing import Dict, Any, List, Optional, Tuple
import asyncio
import json
import subprocess
from pathlib import Path
import os
from .language_servers import (
    PythonLanguageServer,
    TypeScriptLanguageServer,
    JavaLanguageServer,
    HTMLLanguageServer,
    CSSLanguageServer,
    GoLanguageServer,
    RustLanguageServer,
    CppLanguageServer,
    PHPLanguageServer
)
from .more_language_servers import (
    RubyLanguageServer,
    SwiftLanguageServer,
    KotlinLanguageServer,
    ScalaLanguageServer
)
from ..models.language_models import LanguageServer
from ..config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LanguageServer:
    """Base class for language servers."""
    def __init__(self, server_path: str, server_args: List[str]):
        self.server_path = server_path
        self.server_args = server_args
        self.process = None
        self.initialized = False
        self.capabilities = {}

    async def start(self):
        """Start the language server process."""
        try:
            self.process = await asyncio.create_subprocess_exec(
                self.server_path,
                *self.server_args,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await self.initialize()
        except Exception as e:
            logger.error(f"Error starting language server: {str(e)}")
            raise

    async def initialize(self):
        """Initialize the language server."""
        if not self.initialized:
            # Send initialize request
            initialize_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "processId": os.getpid(),
                    "rootUri": None,
                    "capabilities": {}
                }
            }
            await self.send_request(initialize_request)
            
            # Wait for initialize response
            response = await self.receive_response()
            self.capabilities = response.get("result", {}).get("capabilities", {})
            self.initialized = True

    async def send_request(self, request: Dict[str, Any]):
        """Send a request to the language server."""
        if not self.process:
            await self.start()
        
        request_str = json.dumps(request) + "\n"
        self.process.stdin.write(request_str.encode())
        await self.process.stdin.drain()

    async def receive_response(self) -> Dict[str, Any]:
        """Receive a response from the language server."""
        if not self.process:
            raise RuntimeError("Language server not started")
        
        response = await self.process.stdout.readline()
        return json.loads(response.decode())

    async def diagnose(self, code: str, file_path: Optional[str] = None, config: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Get diagnostics for the code."""
        raise NotImplementedError

    async def format(self, code: str, file_path: Optional[str] = None, style_config: Optional[Dict[str, Any]] = None) -> Tuple[str, List[Dict[str, Any]]]:
        """Format the code."""
        raise NotImplementedError

    async def complete(self, code: str, position: Dict[str, int], context: Optional[Dict[str, Any]] = None) -> Tuple[List[Dict[str, Any]], List[str]]:
        """Get completion suggestions."""
        raise NotImplementedError

    async def hover(self, code: str, position: Dict[str, int], context: Optional[Dict[str, Any]] = None) -> Tuple[List[Dict[str, Any]], Optional[Dict[str, Any]]]:
        """Get hover information."""
        raise NotImplementedError

    async def definition(self, code: str, position: Dict[str, int], context: Optional[Dict[str, Any]] = None) -> Tuple[List[Dict[str, Any]], Optional[str]]:
        """Find definition locations."""
        raise NotImplementedError

    async def stop(self):
        """Stop the language server."""
        if self.process:
            # Send shutdown request
            shutdown_request = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "shutdown"
            }
            await self.send_request(shutdown_request)
            
            # Wait for shutdown response
            await self.receive_response()
            
            # Send exit notification
            exit_notification = {
                "jsonrpc": "2.0",
                "method": "exit"
            }
            await self.send_request(exit_notification)
            
            # Terminate process
            self.process.terminate()
            await self.process.wait()
            self.process = None
            self.initialized = False

class PythonLanguageServer(LanguageServer):
    """Python language server using Pyright."""
    def __init__(self):
        super().__init__(
            server_path="pyright-langserver",
            server_args=["--stdio"]
        )

    async def diagnose(self, code: str, file_path: Optional[str] = None, config: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Get diagnostics for Python code."""
        request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "textDocument/diagnostic",
            "params": {
                "textDocument": {
                    "uri": f"file://{file_path}" if file_path else "file:///tmp/temp.py",
                    "languageId": "python",
                    "version": 1,
                    "text": code
                }
            }
        }
        await self.send_request(request)
        response = await self.receive_response()
        return response.get("result", {}).get("diagnostics", [])

    async def format(self, code: str, file_path: Optional[str] = None, style_config: Optional[Dict[str, Any]] = None) -> Tuple[str, List[Dict[str, Any]]]:
        """Format Python code using black."""
        request = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "textDocument/formatting",
            "params": {
                "textDocument": {
                    "uri": f"file://{file_path}" if file_path else "file:///tmp/temp.py",
                    "languageId": "python",
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
        """Get completion suggestions for Python code."""
        request = {
            "jsonrpc": "2.0",
            "id": 5,
            "method": "textDocument/completion",
            "params": {
                "textDocument": {
                    "uri": "file:///tmp/temp.py",
                    "languageId": "python",
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
        """Get hover information for Python code."""
        request = {
            "jsonrpc": "2.0",
            "id": 6,
            "method": "textDocument/hover",
            "params": {
                "textDocument": {
                    "uri": "file:///tmp/temp.py",
                    "languageId": "python",
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
        """Find definition locations for Python code."""
        request = {
            "jsonrpc": "2.0",
            "id": 7,
            "method": "textDocument/definition",
            "params": {
                "textDocument": {
                    "uri": "file:///tmp/temp.py",
                    "languageId": "python",
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

class TypeScriptLanguageServer(LanguageServer):
    """TypeScript language server."""
    def __init__(self):
        super().__init__(
            server_path="typescript-language-server",
            server_args=["--stdio"]
        )

    async def diagnose(self, code: str, file_path: Optional[str] = None, config: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Get diagnostics for TypeScript code."""
        request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "textDocument/diagnostic",
            "params": {
                "textDocument": {
                    "uri": f"file://{file_path}" if file_path else "file:///tmp/temp.ts",
                    "languageId": "typescript",
                    "version": 1,
                    "text": code
                }
            }
        }
        await self.send_request(request)
        response = await self.receive_response()
        return response.get("result", {}).get("diagnostics", [])

    async def format(self, code: str, file_path: Optional[str] = None, style_config: Optional[Dict[str, Any]] = None) -> Tuple[str, List[Dict[str, Any]]]:
        """Format TypeScript code using prettier."""
        request = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "textDocument/formatting",
            "params": {
                "textDocument": {
                    "uri": f"file://{file_path}" if file_path else "file:///tmp/temp.ts",
                    "languageId": "typescript",
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
        """Get completion suggestions for TypeScript code."""
        request = {
            "jsonrpc": "2.0",
            "id": 5,
            "method": "textDocument/completion",
            "params": {
                "textDocument": {
                    "uri": "file:///tmp/temp.ts",
                    "languageId": "typescript",
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
        """Get hover information for TypeScript code."""
        request = {
            "jsonrpc": "2.0",
            "id": 6,
            "method": "textDocument/hover",
            "params": {
                "textDocument": {
                    "uri": "file:///tmp/temp.ts",
                    "languageId": "typescript",
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
        """Find definition locations for TypeScript code."""
        request = {
            "jsonrpc": "2.0",
            "id": 7,
            "method": "textDocument/definition",
            "params": {
                "textDocument": {
                    "uri": "file:///tmp/temp.ts",
                    "languageId": "typescript",
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

class JavaLanguageServer(LanguageServer):
    """Java language server using Eclipse JDT."""
    def __init__(self):
        super().__init__(
            server_path="jdt-language-server",
            server_args=["--stdio"]
        )

    async def diagnose(self, code: str, file_path: Optional[str] = None, config: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Get diagnostics for Java code."""
        request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "textDocument/diagnostic",
            "params": {
                "textDocument": {
                    "uri": f"file://{file_path}" if file_path else "file:///tmp/temp.java",
                    "languageId": "java",
                    "version": 1,
                    "text": code
                }
            }
        }
        await self.send_request(request)
        response = await self.receive_response()
        return response.get("result", {}).get("diagnostics", [])

    async def format(self, code: str, file_path: Optional[str] = None, style_config: Optional[Dict[str, Any]] = None) -> Tuple[str, List[Dict[str, Any]]]:
        """Format Java code."""
        request = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "textDocument/formatting",
            "params": {
                "textDocument": {
                    "uri": f"file://{file_path}" if file_path else "file:///tmp/temp.java",
                    "languageId": "java",
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
        """Get completion suggestions for Java code."""
        request = {
            "jsonrpc": "2.0",
            "id": 5,
            "method": "textDocument/completion",
            "params": {
                "textDocument": {
                    "uri": "file:///tmp/temp.java",
                    "languageId": "java",
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
        """Get hover information for Java code."""
        request = {
            "jsonrpc": "2.0",
            "id": 6,
            "method": "textDocument/hover",
            "params": {
                "textDocument": {
                    "uri": "file:///tmp/temp.java",
                    "languageId": "java",
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
        """Find definition locations for Java code."""
        request = {
            "jsonrpc": "2.0",
            "id": 7,
            "method": "textDocument/definition",
            "params": {
                "textDocument": {
                    "uri": "file:///tmp/temp.java",
                    "languageId": "java",
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

class HTMLLanguageServer(LanguageServer):
    """HTML language server."""
    def __init__(self):
        super().__init__(
            server_path="html-language-server",
            server_args=["--stdio"]
        )

    async def diagnose(self, code: str, file_path: Optional[str] = None, config: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Get diagnostics for HTML code."""
        request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "textDocument/diagnostic",
            "params": {
                "textDocument": {
                    "uri": f"file://{file_path}" if file_path else "file:///tmp/temp.html",
                    "languageId": "html",
                    "version": 1,
                    "text": code
                }
            }
        }
        await self.send_request(request)
        response = await self.receive_response()
        return response.get("result", {}).get("diagnostics", [])

    async def format(self, code: str, file_path: Optional[str] = None, style_config: Optional[Dict[str, Any]] = None) -> Tuple[str, List[Dict[str, Any]]]:
        """Format HTML code."""
        request = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "textDocument/formatting",
            "params": {
                "textDocument": {
                    "uri": f"file://{file_path}" if file_path else "file:///tmp/temp.html",
                    "languageId": "html",
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
        """Get completion suggestions for HTML code."""
        request = {
            "jsonrpc": "2.0",
            "id": 5,
            "method": "textDocument/completion",
            "params": {
                "textDocument": {
                    "uri": "file:///tmp/temp.html",
                    "languageId": "html",
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
        """Get hover information for HTML code."""
        request = {
            "jsonrpc": "2.0",
            "id": 6,
            "method": "textDocument/hover",
            "params": {
                "textDocument": {
                    "uri": "file:///tmp/temp.html",
                    "languageId": "html",
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
        """Find definition locations for HTML code."""
        request = {
            "jsonrpc": "2.0",
            "id": 7,
            "method": "textDocument/definition",
            "params": {
                "textDocument": {
                    "uri": "file:///tmp/temp.html",
                    "languageId": "html",
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

class CSSLanguageServer(LanguageServer):
    """CSS language server."""
    def __init__(self):
        super().__init__(
            server_path="css-language-server",
            server_args=["--stdio"]
        )

    async def diagnose(self, code: str, file_path: Optional[str] = None, config: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Get diagnostics for CSS code."""
        request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "textDocument/diagnostic",
            "params": {
                "textDocument": {
                    "uri": f"file://{file_path}" if file_path else "file:///tmp/temp.css",
                    "languageId": "css",
                    "version": 1,
                    "text": code
                }
            }
        }
        await self.send_request(request)
        response = await self.receive_response()
        return response.get("result", {}).get("diagnostics", [])

    async def format(self, code: str, file_path: Optional[str] = None, style_config: Optional[Dict[str, Any]] = None) -> Tuple[str, List[Dict[str, Any]]]:
        """Format CSS code."""
        request = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "textDocument/formatting",
            "params": {
                "textDocument": {
                    "uri": f"file://{file_path}" if file_path else "file:///tmp/temp.css",
                    "languageId": "css",
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
        """Get completion suggestions for CSS code."""
        request = {
            "jsonrpc": "2.0",
            "id": 5,
            "method": "textDocument/completion",
            "params": {
                "textDocument": {
                    "uri": "file:///tmp/temp.css",
                    "languageId": "css",
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
        """Get hover information for CSS code."""
        request = {
            "jsonrpc": "2.0",
            "id": 6,
            "method": "textDocument/hover",
            "params": {
                "textDocument": {
                    "uri": "file:///tmp/temp.css",
                    "languageId": "css",
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
        """Find definition locations for CSS code."""
        request = {
            "jsonrpc": "2.0",
            "id": 7,
            "method": "textDocument/definition",
            "params": {
                "textDocument": {
                    "uri": "file:///tmp/temp.css",
                    "languageId": "css",
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

class LanguageServerManager:
    """Manages language servers for different programming languages."""
    def __init__(self):
        self.servers: Dict[str, LanguageServer] = {}
        self.initialized = False
        self._load_language_servers()

    def _load_language_servers(self):
        """Load language server configurations from settings."""
        try:
            server_configs = settings.LANGUAGE_SERVERS
            for lang, config in server_configs.items():
                self.servers[lang] = LanguageServer(
                    name=config["name"],
                    command=config["command"],
                    args=config.get("args", []),
                    env=config.get("env", {}),
                    capabilities=config.get("capabilities", {}),
                    initialization_options=config.get("initialization_options", {})
                )
            self.initialized = True
        except Exception as e:
            logger.error(f"Error loading language servers: {str(e)}")
            raise

    def has_server(self, language: str) -> bool:
        """Check if a language server is available for the given language."""
        return language in self.servers

    def get_server(self, language: str) -> Optional[LanguageServer]:
        """Get the language server for the given language."""
        return self.servers.get(language)

    async def initialize_server(self, language: str) -> bool:
        """Initialize a language server if not already running."""
        if not self.has_server(language):
            return False

        server = self.servers[language]
        if not server.is_running():
            try:
                await server.start()
                return True
            except Exception as e:
                logger.error(f"Error initializing {language} server: {str(e)}")
                return False
        return True

    async def lint(self, language: str, code: str, file_path: Optional[str] = None) -> Dict[str, Any]:
        """Get linting results from the language server."""
        if not await self.initialize_server(language):
            raise RuntimeError(f"No language server available for {language}")

        server = self.servers[language]
        try:
            diagnostics = await server.diagnose(code, file_path)
            style_issues = await server.check_style(code, file_path)
            return {
                "diagnostics": diagnostics,
                "style_issues": style_issues
            }
        except Exception as e:
            logger.error(f"Error in lint: {str(e)}")
            raise

    async def format(self, language: str, code: str, file_path: Optional[str] = None) -> Dict[str, Any]:
        """Format code using the language server."""
        if not await self.initialize_server(language):
            raise RuntimeError(f"No language server available for {language}")

        server = self.servers[language]
        try:
            formatted_code, changes = await server.format(code, file_path)
            return {
                "formatted_code": formatted_code,
                "changes": changes
            }
        except Exception as e:
            logger.error(f"Error in format: {str(e)}")
            raise

    async def complete(self, language: str, code: str, position: Dict[str, int], file_path: Optional[str] = None) -> Dict[str, Any]:
        """Get completion suggestions from the language server."""
        if not await self.initialize_server(language):
            raise RuntimeError(f"No language server available for {language}")

        server = self.servers[language]
        try:
            suggestions, trigger_char = await server.complete(code, position, file_path)
            return {
                "suggestions": suggestions,
                "trigger_character": trigger_char
            }
        except Exception as e:
            logger.error(f"Error in complete: {str(e)}")
            raise

    async def hover(self, language: str, code: str, position: Dict[str, int], file_path: Optional[str] = None) -> Dict[str, Any]:
        """Get hover information from the language server."""
        if not await self.initialize_server(language):
            raise RuntimeError(f"No language server available for {language}")

        server = self.servers[language]
        try:
            contents, range_info = await server.hover(code, position, file_path)
            return {
                "contents": contents,
                "range": range_info
            }
        except Exception as e:
            logger.error(f"Error in hover: {str(e)}")
            raise

    async def definition(self, language: str, code: str, position: Dict[str, int], file_path: Optional[str] = None) -> Dict[str, Any]:
        """Find definition locations using the language server."""
        if not await self.initialize_server(language):
            raise RuntimeError(f"No language server available for {language}")

        server = self.servers[language]
        try:
            locations, symbol = await server.definition(code, position, file_path)
            return {
                "locations": locations,
                "symbol": symbol
            }
        except Exception as e:
            logger.error(f"Error in definition: {str(e)}")
            raise

    async def analyze(self, language: str, code: str, file_path: Optional[str] = None) -> Dict[str, Any]:
        """Perform code analysis using the language server."""
        if not await self.initialize_server(language):
            raise RuntimeError(f"No language server available for {language}")

        server = self.servers[language]
        try:
            analysis = await server.analyze(code, file_path)
            return analysis
        except Exception as e:
            logger.error(f"Error in analyze: {str(e)}")
            raise

    async def shutdown(self):
        """Shutdown all language servers."""
        for server in self.servers.values():
            try:
                await server.stop()
            except Exception as e:
                logger.error(f"Error shutting down server: {str(e)}") 