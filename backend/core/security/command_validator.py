import re
from typing import List, Set, Tuple
from dataclasses import dataclass
from enum import Enum

class CommandCategory(Enum):
    SAFE = "safe"
    DANGEROUS = "dangerous"
    SYSTEM = "system"
    NETWORK = "network"
    FILE = "file"
    PROCESS = "process"

@dataclass
class ValidationResult:
    is_safe: bool
    category: CommandCategory
    reason: str
    matched_pattern: str = ""

class CommandValidator:
    def __init__(self):
        # Dangerous command patterns
        self.dangerous_patterns: List[Tuple[str, CommandCategory, str]] = [
            # System modification commands
            (r"^rm\s+.*", CommandCategory.SYSTEM, "File deletion command"),
            (r"^mkfs\s+.*", CommandCategory.SYSTEM, "Filesystem creation command"),
            (r"^dd\s+.*", CommandCategory.SYSTEM, "Raw disk operation"),
            (r"^chmod\s+.*", CommandCategory.SYSTEM, "Permission modification"),
            (r"^chown\s+.*", CommandCategory.SYSTEM, "Ownership modification"),
            
            # Process management
            (r"^sudo\s+.*", CommandCategory.PROCESS, "Privilege escalation"),
            (r"^su\s+.*", CommandCategory.PROCESS, "User switching"),
            (r"^kill\s+.*", CommandCategory.PROCESS, "Process termination"),
            (r"^pkill\s+.*", CommandCategory.PROCESS, "Process termination"),
            
            # Network operations
            (r"^nc\s+.*", CommandCategory.NETWORK, "Netcat command"),
            (r"^nmap\s+.*", CommandCategory.NETWORK, "Network scanning"),
            (r"^wget\s+.*", CommandCategory.NETWORK, "File download"),
            (r"^curl\s+.*", CommandCategory.NETWORK, "File download"),
            
            # File operations
            (r"^mv\s+.*", CommandCategory.FILE, "File movement"),
            (r"^cp\s+.*", CommandCategory.FILE, "File copying"),
            (r"^tar\s+.*", CommandCategory.FILE, "Archive operations"),
            (r"^zip\s+.*", CommandCategory.FILE, "Archive operations"),
            
            # Shell operations
            (r"^bash\s+.*", CommandCategory.DANGEROUS, "Shell execution"),
            (r"^sh\s+.*", CommandCategory.DANGEROUS, "Shell execution"),
            (r"^python\s+.*", CommandCategory.DANGEROUS, "Python execution"),
            (r"^perl\s+.*", CommandCategory.DANGEROUS, "Perl execution"),
        ]
        
        # Safe command patterns
        self.safe_patterns: List[str] = [
            r"^ls\s*$",
            r"^pwd\s*$",
            r"^echo\s+.*",
            r"^cat\s+.*",
            r"^grep\s+.*",
            r"^find\s+.*",
            r"^git\s+.*",
            r"^docker\s+.*",
        ]
        
        # Compile patterns for better performance
        self.dangerous_regex = [(re.compile(pattern), category, reason) 
                               for pattern, category, reason in self.dangerous_patterns]
        self.safe_regex = [re.compile(pattern) for pattern in self.safe_patterns]

    def validate_command(self, command: str) -> ValidationResult:
        """
        Validate a command and return a ValidationResult.
        
        Args:
            command: The command to validate
            
        Returns:
            ValidationResult containing safety status and details
        """
        # Remove leading/trailing whitespace
        command = command.strip()
        
        # Check for empty command
        if not command:
            return ValidationResult(
                is_safe=False,
                category=CommandCategory.DANGEROUS,
                reason="Empty command"
            )
        
        # Check for safe patterns first
        for pattern in self.safe_regex:
            if pattern.match(command):
                return ValidationResult(
                    is_safe=True,
                    category=CommandCategory.SAFE,
                    reason="Command matches safe pattern",
                    matched_pattern=pattern.pattern
                )
        
        # Check for dangerous patterns
        for pattern, category, reason in self.dangerous_regex:
            if pattern.match(command):
                return ValidationResult(
                    is_safe=False,
                    category=category,
                    reason=reason,
                    matched_pattern=pattern.pattern
                )
        
        # If no patterns match, consider it unsafe
        return ValidationResult(
            is_safe=False,
            category=CommandCategory.DANGEROUS,
            reason="Command does not match any safe patterns"
        )

    def is_safe(self, command: str) -> bool:
        """
        Quick check if a command is safe.
        
        Args:
            command: The command to check
            
        Returns:
            bool indicating if the command is safe
        """
        return self.validate_command(command).is_safe

    def sanitize_command(self, command: str) -> str:
        """
        Sanitize a command by removing potentially dangerous characters.
        
        Args:
            command: The command to sanitize
            
        Returns:
            Sanitized command string
        """
        # Remove control characters
        command = ''.join(char for char in command if char.isprintable())
        
        # Remove command chaining
        command = command.split(';')[0].split('&&')[0].split('||')[0]
        
        # Remove redirections
        command = command.split('>')[0].split('<')[0].split('>>')[0]
        
        return command.strip()

    def get_allowed_commands(self) -> Set[str]:
        """
        Get a set of all allowed command patterns.
        
        Returns:
            Set of allowed command patterns
        """
        return {pattern.pattern for pattern in self.safe_regex}

    def get_blocked_commands(self) -> Set[str]:
        """
        Get a set of all blocked command patterns.
        
        Returns:
            Set of blocked command patterns
        """
        return {pattern.pattern for pattern, _, _ in self.dangerous_patterns} 