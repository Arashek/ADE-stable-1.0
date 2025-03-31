import pytest
from src.core.security.command_validator import CommandValidator, CommandCategory, ValidationResult

@pytest.fixture
def validator():
    return CommandValidator()

def test_safe_commands(validator):
    safe_commands = [
        "ls",
        "pwd",
        "echo hello",
        "cat file.txt",
        "grep pattern file",
        "find . -name '*.py'",
        "git status",
        "docker ps"
    ]
    
    for command in safe_commands:
        result = validator.validate_command(command)
        assert result.is_safe, f"Command '{command}' should be safe"
        assert result.category == CommandCategory.SAFE
        assert result.reason == "Command matches safe pattern"
        assert result.matched_pattern != ""

def test_dangerous_commands(validator):
    dangerous_commands = [
        ("rm -rf /", CommandCategory.SYSTEM),
        ("sudo su", CommandCategory.PROCESS),
        ("chmod 777 file", CommandCategory.SYSTEM),
        ("wget http://example.com", CommandCategory.NETWORK),
        ("python script.py", CommandCategory.DANGEROUS),
        ("bash script.sh", CommandCategory.DANGEROUS),
        ("mv file1 file2", CommandCategory.FILE),
        ("cp file1 file2", CommandCategory.FILE)
    ]
    
    for command, expected_category in dangerous_commands:
        result = validator.validate_command(command)
        assert not result.is_safe, f"Command '{command}' should be dangerous"
        assert result.category == expected_category
        assert result.reason != ""
        assert result.matched_pattern != ""

def test_empty_command(validator):
    result = validator.validate_command("")
    assert not result.is_safe
    assert result.category == CommandCategory.DANGEROUS
    assert result.reason == "Empty command"
    assert result.matched_pattern == ""

def test_unknown_command(validator):
    result = validator.validate_command("unknown_command")
    assert not result.is_safe
    assert result.category == CommandCategory.DANGEROUS
    assert result.reason == "Command does not match any safe patterns"
    assert result.matched_pattern == ""

def test_command_sanitization(validator):
    test_cases = [
        ("ls; rm -rf /", "ls"),
        ("echo hello && sudo su", "echo hello"),
        ("cat file.txt > output.txt", "cat file.txt"),
        ("grep pattern || dangerous", "grep pattern"),
        ("find . -name '*.py' >> log.txt", "find . -name '*.py'")
    ]
    
    for input_command, expected_output in test_cases:
        sanitized = validator.sanitize_command(input_command)
        assert sanitized == expected_output, f"Failed to sanitize '{input_command}'"

def test_get_allowed_commands(validator):
    allowed = validator.get_allowed_commands()
    assert isinstance(allowed, set)
    assert len(allowed) > 0
    assert all(isinstance(pattern, str) for pattern in allowed)

def test_get_blocked_commands(validator):
    blocked = validator.get_blocked_commands()
    assert isinstance(blocked, set)
    assert len(blocked) > 0
    assert all(isinstance(pattern, str) for pattern in blocked)

def test_command_with_arguments(validator):
    test_cases = [
        ("ls -la", False),
        ("echo 'Hello World'", True),
        ("cat /etc/passwd", True),
        ("find . -type f -name '*.txt'", True),
        ("grep -r 'pattern' .", True),
        ("docker run -it ubuntu", True)
    ]
    
    for command, expected_safe in test_cases:
        result = validator.validate_command(command)
        assert result.is_safe == expected_safe, f"Unexpected safety result for '{command}'"

def test_command_with_paths(validator):
    test_cases = [
        ("cat ./file.txt", True),
        ("cat ../file.txt", True),
        ("cat /etc/passwd", True),
        ("rm ./file.txt", False),
        ("rm ../file.txt", False),
        ("rm /etc/passwd", False)
    ]
    
    for command, expected_safe in test_cases:
        result = validator.validate_command(command)
        assert result.is_safe == expected_safe, f"Unexpected safety result for '{command}'"

def test_command_with_special_characters(validator):
    test_cases = [
        ("echo $HOME", True),
        ("echo ${PATH}", True),
        ("echo `whoami`", True),
        ("echo $(whoami)", True),
        ("ls | grep pattern", True),
        ("cat file.txt | grep pattern", True)
    ]
    
    for command, expected_safe in test_cases:
        sanitized = validator.sanitize_command(command)
        result = validator.validate_command(sanitized)
        assert result.is_safe == expected_safe, f"Unexpected safety result for '{command}'" 