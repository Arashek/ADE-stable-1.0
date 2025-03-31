from typing import Dict, Any, Optional, List
import logging
import re
import os
from pathlib import Path

logger = logging.getLogger(__name__)

class CodeFormatter:
    """Utility class for code formatting and style enforcement."""

    # Common indentation styles
    INDENT_STYLES = {
        "spaces": " ",
        "tabs": "\t"
    }

    # Common line ending styles
    LINE_ENDINGS = {
        "lf": "\n",
        "crlf": "\r\n",
        "cr": "\r"
    }

    # Common quote styles
    QUOTE_STYLES = {
        "single": "'",
        "double": '"'
    }

    @staticmethod
    def format_code(
        code: str,
        language: str,
        style: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Format code according to specified style rules."""
        if style is None:
            style = CodeFormatter.get_default_style(language)

        try:
            # Apply formatting rules
            formatted_code = code
            changes = []

            # Normalize line endings
            if style.get("line_ending"):
                formatted_code, line_changes = CodeFormatter._normalize_line_endings(
                    formatted_code,
                    style["line_ending"]
                )
                changes.extend(line_changes)

            # Apply indentation
            if style.get("indent_style") and style.get("indent_size"):
                formatted_code, indent_changes = CodeFormatter._apply_indentation(
                    formatted_code,
                    style["indent_style"],
                    style["indent_size"]
                )
                changes.extend(indent_changes)

            # Apply quote style
            if style.get("quote_style"):
                formatted_code, quote_changes = CodeFormatter._normalize_quotes(
                    formatted_code,
                    style["quote_style"]
                )
                changes.extend(quote_changes)

            # Apply max line length
            if style.get("max_line_length"):
                formatted_code, length_changes = CodeFormatter._enforce_line_length(
                    formatted_code,
                    style["max_line_length"]
                )
                changes.extend(length_changes)

            # Apply trailing whitespace rules
            if style.get("trim_trailing_whitespace", True):
                formatted_code, whitespace_changes = CodeFormatter._trim_trailing_whitespace(
                    formatted_code
                )
                changes.extend(whitespace_changes)

            # Apply final newline rule
            if style.get("insert_final_newline", True):
                formatted_code, newline_changes = CodeFormatter._ensure_final_newline(
                    formatted_code
                )
                changes.extend(newline_changes)

            return {
                "formatted_code": formatted_code,
                "changes": changes,
                "style_applied": style
            }

        except Exception as e:
            logger.error(f"Error formatting code: {str(e)}")
            return {
                "formatted_code": code,
                "changes": [],
                "error": str(e)
            }

    @staticmethod
    def get_default_style(language: str) -> Dict[str, Any]:
        """Get default style rules for a language."""
        # Common defaults
        defaults = {
            "indent_style": "spaces",
            "indent_size": 4,
            "line_ending": "lf",
            "quote_style": "double",
            "max_line_length": 80,
            "trim_trailing_whitespace": True,
            "insert_final_newline": True
        }

        # Language-specific overrides
        language_overrides = {
            "python": {
                "indent_size": 4,
                "max_line_length": 79,
                "quote_style": "single"
            },
            "javascript": {
                "indent_size": 2,
                "max_line_length": 100,
                "quote_style": "single"
            },
            "java": {
                "indent_size": 4,
                "max_line_length": 120
            },
            "cpp": {
                "indent_size": 4,
                "max_line_length": 100
            }
        }

        # Merge defaults with language-specific overrides
        style = defaults.copy()
        if language in language_overrides:
            style.update(language_overrides[language])

        return style

    @staticmethod
    def _normalize_line_endings(
        code: str,
        line_ending: str
    ) -> tuple[str, List[Dict[str, Any]]]:
        """Normalize line endings in code."""
        changes = []
        normalized = code.replace("\r\n", "\n").replace("\r", "\n")
        target = CodeFormatter.LINE_ENDINGS.get(line_ending, "\n")
        
        if normalized != code:
            changes.append({
                "type": "line_ending",
                "line": 1,
                "column": 1,
                "message": f"Normalized line endings to {line_ending}"
            })
        
        return normalized.replace("\n", target), changes

    @staticmethod
    def _apply_indentation(
        code: str,
        indent_style: str,
        indent_size: int
    ) -> tuple[str, List[Dict[str, Any]]]:
        """Apply indentation rules to code."""
        changes = []
        lines = code.splitlines()
        formatted_lines = []
        indent_char = CodeFormatter.INDENT_STYLES.get(indent_style, " ")
        current_indent = 0

        for i, line in enumerate(lines, 1):
            # Count leading whitespace
            leading_spaces = len(line) - len(line.lstrip())
            current_indent = leading_spaces // indent_size

            # Apply new indentation
            new_indent = current_indent * indent_size
            formatted_line = indent_char * new_indent + line.lstrip()
            
            if formatted_line != line:
                changes.append({
                    "type": "indentation",
                    "line": i,
                    "column": 1,
                    "message": f"Adjusted indentation to {new_indent} spaces"
                })
            
            formatted_lines.append(formatted_line)

        return "\n".join(formatted_lines), changes

    @staticmethod
    def _normalize_quotes(
        code: str,
        quote_style: str
    ) -> tuple[str, List[Dict[str, Any]]]:
        """Normalize quote style in code."""
        changes = []
        target_quote = CodeFormatter.QUOTE_STYLES.get(quote_style, '"')
        other_quote = '"' if target_quote == "'" else "'"
        
        # Simple regex to match string literals
        pattern = f"{other_quote}[^{other_quote}]*{other_quote}"
        matches = re.finditer(pattern, code)
        
        for match in matches:
            start, end = match.span()
            line = code[:start].count('\n') + 1
            column = start - code.rfind('\n', 0, start) if '\n' in code[:start] else start + 1
            
            changes.append({
                "type": "quote_style",
                "line": line,
                "column": column,
                "message": f"Changed quote style to {quote_style}"
            })
        
        formatted_code = re.sub(pattern, lambda m: target_quote + m.group()[1:-1] + target_quote, code)
        return formatted_code, changes

    @staticmethod
    def _enforce_line_length(
        code: str,
        max_length: int
    ) -> tuple[str, List[Dict[str, Any]]]:
        """Enforce maximum line length."""
        changes = []
        lines = code.splitlines()
        formatted_lines = []

        for i, line in enumerate(lines, 1):
            if len(line) > max_length:
                # Simple line breaking - this could be enhanced with more sophisticated rules
                words = line.split()
                current_line = []
                current_length = 0
                
                for word in words:
                    if current_length + len(word) + 1 <= max_length:
                        current_line.append(word)
                        current_length += len(word) + 1
                    else:
                        formatted_lines.append(" ".join(current_line))
                        current_line = [word]
                        current_length = len(word)
                
                if current_line:
                    formatted_lines.append(" ".join(current_line))
                
                changes.append({
                    "type": "line_length",
                    "line": i,
                    "column": max_length + 1,
                    "message": f"Split line to enforce maximum length of {max_length}"
                })
            else:
                formatted_lines.append(line)

        return "\n".join(formatted_lines), changes

    @staticmethod
    def _trim_trailing_whitespace(
        code: str
    ) -> tuple[str, List[Dict[str, Any]]]:
        """Remove trailing whitespace from lines."""
        changes = []
        lines = code.splitlines()
        formatted_lines = []

        for i, line in enumerate(lines, 1):
            stripped = line.rstrip()
            if stripped != line:
                changes.append({
                    "type": "whitespace",
                    "line": i,
                    "column": len(stripped) + 1,
                    "message": "Removed trailing whitespace"
                })
            formatted_lines.append(stripped)

        return "\n".join(formatted_lines), changes

    @staticmethod
    def _ensure_final_newline(
        code: str
    ) -> tuple[str, List[Dict[str, Any]]]:
        """Ensure file ends with a newline."""
        changes = []
        if not code.endswith("\n"):
            changes.append({
                "type": "newline",
                "line": code.count("\n") + 1,
                "column": len(code) - code.rfind("\n") if "\n" in code else len(code),
                "message": "Added final newline"
            })
            code += "\n"
        return code, changes

    @staticmethod
    def detect_style(code: str) -> Dict[str, Any]:
        """Detect code style from existing code."""
        style = {
            "indent_style": "spaces",
            "indent_size": 4,
            "line_ending": "lf",
            "quote_style": "double",
            "max_line_length": 80
        }

        # Detect indentation style and size
        lines = code.splitlines()
        for line in lines:
            if line.startswith("\t"):
                style["indent_style"] = "tabs"
                break
            elif line.startswith(" "):
                indent_size = len(line) - len(line.lstrip())
                if indent_size > 0:
                    style["indent_size"] = indent_size
                    break

        # Detect line endings
        if "\r\n" in code:
            style["line_ending"] = "crlf"
        elif "\r" in code:
            style["line_ending"] = "cr"

        # Detect quote style
        single_quotes = code.count("'")
        double_quotes = code.count('"')
        if single_quotes > double_quotes:
            style["quote_style"] = "single"

        # Detect max line length
        max_length = max(len(line) for line in lines)
        style["max_line_length"] = max_length

        return style 