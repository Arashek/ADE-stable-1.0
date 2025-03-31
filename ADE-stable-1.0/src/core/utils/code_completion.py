from typing import Dict, Any, List, Optional, Tuple
import logging
import re
from collections import defaultdict

logger = logging.getLogger(__name__)

class CodeCompletion:
    """Utility class for code completion and suggestions."""

    # Common trigger characters for different languages
    TRIGGER_CHARACTERS = {
        "python": [".", "(", "[", "{", "'", '"', " ", "\t"],
        "javascript": [".", "(", "[", "{", "'", '"', " ", "\t", "`"],
        "java": [".", "(", "[", "{", "'", '"', " ", "\t"],
        "cpp": [".", "->", "::", "(", "[", "{", "'", '"', " ", "\t"],
        "typescript": [".", "(", "[", "{", "'", '"', " ", "\t", "`"],
        "go": [".", "(", "[", "{", "'", '"', " ", "\t"],
        "rust": [".", "::", "(", "[", "{", "'", '"', " ", "\t"],
        "php": [".", "->", "::", "(", "[", "{", "'", '"', " ", "\t"],
        "ruby": [".", "(", "[", "{", "'", '"', " ", "\t", "@", "$"],
        "swift": [".", "(", "[", "{", "'", '"', " ", "\t"],
        "kotlin": [".", "(", "[", "{", "'", '"', " ", "\t"],
        "scala": [".", "(", "[", "{", "'", '"', " ", "\t"],
        "haskell": [".", "(", "[", "{", "'", '"', " ", "\t", "`"],
        "fsharp": [".", "(", "[", "{", "'", '"', " ", "\t"],
        "clojure": [".", "(", "[", "{", "'", '"', " ", "\t"],
        "lisp": [".", "(", "[", "{", "'", '"', " ", "\t"],
        "sql": [".", "(", "[", "{", "'", '"', " ", "\t", "@"],
        "graphql": [".", "(", "[", "{", "'", '"', " ", "\t", "@"],
        "terraform": [".", "(", "[", "{", "'", '"', " ", "\t", "$"],
        "yaml": [".", "(", "[", "{", "'", '"', " ", "\t", "-"],
        "json": [".", "(", "[", "{", "'", '"', " ", "\t"],
        "markdown": [".", "(", "[", "{", "'", '"', " ", "\t", "#", "-", "*", "`"],
        "html": [".", "(", "[", "{", "'", '"', " ", "\t", "<", "/"],
        "css": [".", "(", "[", "{", "'", '"', " ", "\t", "@", "#", "."],
        "shell": [".", "(", "[", "{", "'", '"', " ", "\t", "$", "@", "#"],
        "powershell": [".", "(", "[", "{", "'", '"', " ", "\t", "$", "@", "#"]
    }

    # Common completion items for different languages
    COMMON_COMPLETIONS = {
        "python": [
            {"label": "def", "kind": "keyword", "detail": "Define a function"},
            {"label": "class", "kind": "keyword", "detail": "Define a class"},
            {"label": "import", "kind": "keyword", "detail": "Import a module"},
            {"label": "from", "kind": "keyword", "detail": "Import from module"},
            {"label": "return", "kind": "keyword", "detail": "Return from function"},
            {"label": "if", "kind": "keyword", "detail": "If statement"},
            {"label": "else", "kind": "keyword", "detail": "Else statement"},
            {"label": "elif", "kind": "keyword", "detail": "Else if statement"},
            {"label": "for", "kind": "keyword", "detail": "For loop"},
            {"label": "while", "kind": "keyword", "detail": "While loop"},
            {"label": "try", "kind": "keyword", "detail": "Try block"},
            {"label": "except", "kind": "keyword", "detail": "Except block"},
            {"label": "finally", "kind": "keyword", "detail": "Finally block"},
            {"label": "raise", "kind": "keyword", "detail": "Raise exception"},
            {"label": "with", "kind": "keyword", "detail": "With statement"},
            {"label": "as", "kind": "keyword", "detail": "As keyword"},
            {"label": "True", "kind": "constant", "detail": "True boolean"},
            {"label": "False", "kind": "constant", "detail": "False boolean"},
            {"label": "None", "kind": "constant", "detail": "None value"},
            {"label": "self", "kind": "variable", "detail": "Self reference"},
            {"label": "super", "kind": "function", "detail": "Super function"},
            {"label": "print", "kind": "function", "detail": "Print function"},
            {"label": "len", "kind": "function", "detail": "Length function"},
            {"label": "range", "kind": "function", "detail": "Range function"},
            {"label": "list", "kind": "class", "detail": "List class"},
            {"label": "dict", "kind": "class", "detail": "Dictionary class"},
            {"label": "set", "kind": "class", "detail": "Set class"},
            {"label": "tuple", "kind": "class", "detail": "Tuple class"},
            {"label": "str", "kind": "class", "detail": "String class"},
            {"label": "int", "kind": "class", "detail": "Integer class"},
            {"label": "float", "kind": "class", "detail": "Float class"},
            {"label": "bool", "kind": "class", "detail": "Boolean class"}
        ],
        "javascript": [
            {"label": "function", "kind": "keyword", "detail": "Define a function"},
            {"label": "class", "kind": "keyword", "detail": "Define a class"},
            {"label": "const", "kind": "keyword", "detail": "Constant declaration"},
            {"label": "let", "kind": "keyword", "detail": "Variable declaration"},
            {"label": "var", "kind": "keyword", "detail": "Variable declaration"},
            {"label": "return", "kind": "keyword", "detail": "Return from function"},
            {"label": "if", "kind": "keyword", "detail": "If statement"},
            {"label": "else", "kind": "keyword", "detail": "Else statement"},
            {"label": "for", "kind": "keyword", "detail": "For loop"},
            {"label": "while", "kind": "keyword", "detail": "While loop"},
            {"label": "try", "kind": "keyword", "detail": "Try block"},
            {"label": "catch", "kind": "keyword", "detail": "Catch block"},
            {"label": "finally", "kind": "keyword", "detail": "Finally block"},
            {"label": "throw", "kind": "keyword", "detail": "Throw exception"},
            {"label": "async", "kind": "keyword", "detail": "Async function"},
            {"label": "await", "kind": "keyword", "detail": "Await expression"},
            {"label": "true", "kind": "constant", "detail": "True boolean"},
            {"label": "false", "kind": "constant", "detail": "False boolean"},
            {"label": "null", "kind": "constant", "detail": "Null value"},
            {"label": "undefined", "kind": "constant", "detail": "Undefined value"},
            {"label": "this", "kind": "variable", "detail": "This reference"},
            {"label": "super", "kind": "function", "detail": "Super function"},
            {"label": "console", "kind": "object", "detail": "Console object"},
            {"label": "Math", "kind": "object", "detail": "Math object"},
            {"label": "Date", "kind": "class", "detail": "Date class"},
            {"label": "Array", "kind": "class", "detail": "Array class"},
            {"label": "Object", "kind": "class", "detail": "Object class"},
            {"label": "String", "kind": "class", "detail": "String class"},
            {"label": "Number", "kind": "class", "detail": "Number class"},
            {"label": "Boolean", "kind": "class", "detail": "Boolean class"},
            {"label": "Promise", "kind": "class", "detail": "Promise class"}
        ]
    }

    @staticmethod
    def get_completion_context(
        code: str,
        position: Dict[str, int],
        language: str
    ) -> Dict[str, Any]:
        """Get context for code completion."""
        try:
            # Get the line up to the cursor position
            lines = code.splitlines()
            line_number = position["line"] - 1
            character = position["character"]
            
            if line_number >= len(lines):
                return {"prefix": "", "context": {}}
            
            current_line = lines[line_number]
            prefix = current_line[:character]
            
            # Get the word being completed
            word_match = re.search(r'\w*$', prefix)
            word = word_match.group() if word_match else ""
            
            # Get the trigger character
            trigger_char = prefix[-1] if prefix else ""
            
            # Get the context before the cursor
            context = {
                "line": line_number + 1,
                "character": character,
                "word": word,
                "trigger_char": trigger_char,
                "prefix": prefix,
                "line_content": current_line,
                "is_trigger_char": trigger_char in CodeCompletion.TRIGGER_CHARACTERS.get(language, []),
                "is_word_boundary": bool(word_match),
                "is_whitespace": trigger_char.isspace() if trigger_char else False,
                "is_operator": trigger_char in "+-*/%&|^~=<>!@#$^&*()[]{}|\\:;\"'`?.,",
                "is_dot": trigger_char == ".",
                "is_colon": trigger_char == ":",
                "is_paren": trigger_char in "()",
                "is_bracket": trigger_char in "[]",
                "is_brace": trigger_char in "{}",
                "is_quote": trigger_char in "'\"`",
                "is_space": trigger_char == " ",
                "is_tab": trigger_char == "\t",
                "is_newline": trigger_char == "\n"
            }
            
            return context
            
        except Exception as e:
            logger.error(f"Error getting completion context: {str(e)}")
            return {"prefix": "", "context": {}}

    @staticmethod
    def get_completions(
        code: str,
        position: Dict[str, int],
        language: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Tuple[List[Dict[str, Any]], List[str]]:
        """Get code completion suggestions."""
        try:
            if context is None:
                context = CodeCompletion.get_completion_context(code, position, language)
            
            # Get common completions for the language
            completions = CodeCompletion.COMMON_COMPLETIONS.get(language, [])
            
            # Filter completions based on context
            filtered_completions = []
            for completion in completions:
                label = completion["label"]
                
                # Skip if the label doesn't match the prefix
                if context["word"] and not label.startswith(context["word"]):
                    continue
                
                # Skip if the trigger character doesn't match
                if context["trigger_char"] and not CodeCompletion._is_valid_trigger(
                    context["trigger_char"],
                    label,
                    language
                ):
                    continue
                
                filtered_completions.append(completion)
            
            # Get trigger characters for the language
            trigger_chars = CodeCompletion.TRIGGER_CHARACTERS.get(language, [])
            
            return filtered_completions, trigger_chars
            
        except Exception as e:
            logger.error(f"Error getting completions: {str(e)}")
            return [], []

    @staticmethod
    def _is_valid_trigger(
        trigger_char: str,
        label: str,
        language: str
    ) -> bool:
        """Check if a trigger character is valid for a completion label."""
        # Special cases for different languages
        if language == "python":
            if trigger_char == ".":
                return True  # Method/property access
            elif trigger_char == "(":
                return True  # Function call
            elif trigger_char == "[":
                return True  # List/dict access
            elif trigger_char == "{":
                return True  # Dict/set literal
            elif trigger_char in "'\"":
                return True  # String literal
            elif trigger_char.isspace():
                return True  # Word boundary
        elif language == "javascript":
            if trigger_char == ".":
                return True  # Method/property access
            elif trigger_char == "(":
                return True  # Function call
            elif trigger_char == "[":
                return True  # Array/object access
            elif trigger_char == "{":
                return True  # Object literal
            elif trigger_char in "'\"`":
                return True  # String literal
            elif trigger_char.isspace():
                return True  # Word boundary
        # Add more language-specific rules as needed
        
        return False

    @staticmethod
    def format_completion(
        completion: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Format a completion item with additional information."""
        try:
            formatted = completion.copy()
            
            # Add snippet if needed
            if "snippet" not in formatted:
                formatted["snippet"] = formatted["label"]
            
            # Add documentation if needed
            if "documentation" not in formatted:
                formatted["documentation"] = {
                    "kind": "markdown",
                    "value": f"```{context.get('language', '')}\n{formatted['label']}\n```\n\n{formatted.get('detail', '')}"
                }
            
            # Add text edit if needed
            if "textEdit" not in formatted:
                word = context.get("word", "")
                if word:
                    formatted["textEdit"] = {
                        "range": {
                            "start": {
                                "line": context["line"] - 1,
                                "character": context["character"] - len(word)
                            },
                            "end": {
                                "line": context["line"] - 1,
                                "character": context["character"]
                            }
                        },
                        "newText": formatted["label"]
                    }
            
            return formatted
            
        except Exception as e:
            logger.error(f"Error formatting completion: {str(e)}")
            return completion

    @staticmethod
    def get_completion_priority(
        completion: Dict[str, Any],
        context: Dict[str, Any]
    ) -> int:
        """Get the priority of a completion item."""
        priority = 0
        
        # Exact match gets highest priority
        if completion["label"] == context.get("word", ""):
            priority += 1000
        
        # Keyword completions get high priority
        if completion.get("kind") == "keyword":
            priority += 500
        
        # Function completions get medium priority
        elif completion.get("kind") == "function":
            priority += 300
        
        # Variable completions get lower priority
        elif completion.get("kind") == "variable":
            priority += 200
        
        # Other completions get lowest priority
        else:
            priority += 100
        
        return priority 