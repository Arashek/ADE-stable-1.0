import pytest
import asyncio
from pathlib import Path
from backend.services.agents.specialized.security_agent import SecurityAgent
from backend.services.agents.specialized.performance_agent import PerformanceAgent
from backend.services.agents.specialized.validation_agent import ValidationAgent
from backend.services.agents.specialized.architecture_agent import ArchitectureAgent

@pytest.fixture
def test_code_dir():
    return Path(__file__).parent / 'test_code'

@pytest.fixture
def security_agent():
    return SecurityAgent()

@pytest.fixture
def performance_agent():
    return PerformanceAgent()

@pytest.fixture
def validation_agent():
    return ValidationAgent()

@pytest.fixture
def architecture_agent():
    return ArchitectureAgent()

@pytest.mark.asyncio
async def test_security_agent_vulnerability_detection(security_agent, test_code_dir):
    # Test code with known vulnerabilities
    test_code = """
    def process_user_input():
        user_input = input()
        eval(user_input)  # Security vulnerability
        
    def execute_query(user_data):
        query = f"SELECT * FROM users WHERE id = {user_data}"  # SQL injection
        cursor.execute(query)
    """
    
    vulnerabilities = await security_agent.analyze_code(
        test_code, 
        str(test_code_dir / "test_security.py")
    )
    
    assert len(vulnerabilities) >= 2
    assert any(v.description.lower().count('eval') for v in vulnerabilities)
    assert any(v.description.lower().count('sql injection') for v in vulnerabilities)

@pytest.mark.asyncio
async def test_performance_agent_pattern_detection(performance_agent, test_code_dir):
    # Test code with performance issues
    test_code = """
    def get_user_data():
        users = []
        for user_id in user_ids:
            user = User.objects.filter(id=user_id).first()  # N+1 query
            users.append(user)
        return users
        
    def process_large_list():
        large_list = [i for i in range(10000)]  # Large data structure
        for i in large_list:
            for j in large_list:  # Nested loop
                print(i * j)
    """
    
    issues = await performance_agent.analyze_code(
        test_code,
        str(test_code_dir / "test_performance.py")
    )
    
    assert len(issues) >= 2
    assert any(i.description.lower().count('n+1') for i in issues)
    assert any(i.description.lower().count('nested loop') for i in issues)

@pytest.mark.asyncio
async def test_validation_agent_code_quality(validation_agent, test_code_dir):
    # Test code with style and complexity issues
    test_code = """
    class badClassName:  # Wrong naming convention
        def TOO_MANY_PARAMS(self, a, b, c, d, e, f, g):  # Too many parameters
            pass
            
        def very_long_function(self):
            # ... imagine 100 lines of code here
            pass
    """
    
    issues = await validation_agent.validate_code(
        test_code,
        str(test_code_dir / "test_validation.py")
    )
    
    assert len(issues) >= 2
    assert any(i.category == "style" for i in issues)
    assert any(i.category == "complexity" for i in issues)

@pytest.mark.asyncio
async def test_architecture_agent_pattern_detection(architecture_agent, test_code_dir):
    # Test project structure
    test_project = {
        "entities/user.py": """
            class User:
                def __init__(self, id, name):
                    self.id = id
                    self.name = name
        """,
        "use_cases/user_service.py": """
            class UserService:
                def __init__(self, user_repository):
                    self.user_repository = user_repository
                
                def get_user(self, user_id):
                    return self.user_repository.get(user_id)
        """,
        "interfaces/user_repository.py": """
            class UserRepository:
                def get(self, user_id):
                    pass
        """
    }
    
    # Create test files
    for path, content in test_project.items():
        file_path = test_code_dir / path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content)
    
    issues = await architecture_agent.analyze_architecture(str(test_code_dir))
    
    # Should detect Clean Architecture pattern
    assert any(i.description.count('Clean Architecture') for i in issues) == 0

@pytest.mark.asyncio
async def test_multi_agent_analysis(
    security_agent,
    performance_agent,
    validation_agent,
    architecture_agent,
    test_code_dir
):
    # Test code with multiple issues
    test_code = """
    class BadService:  # Wrong naming convention
        def process_data(self, user_input):
            # Security issue
            eval(user_input)
            
            # Performance issue
            results = []
            for i in range(1000):
                for j in range(1000):
                    results.append(i * j)
            
            # Architecture issue
            global_state.update(results)
    """
    
    # Run all agents
    security_issues = await security_agent.analyze_code(
        test_code,
        str(test_code_dir / "test_multi.py")
    )
    performance_issues = await performance_agent.analyze_code(
        test_code,
        str(test_code_dir / "test_multi.py")
    )
    validation_issues = await validation_agent.validate_code(
        test_code,
        str(test_code_dir / "test_multi.py")
    )
    
    # Verify each agent found their specific issues
    assert len(security_issues) > 0
    assert len(performance_issues) > 0
    assert len(validation_issues) > 0

@pytest.mark.asyncio
async def test_agent_suggestions(
    security_agent,
    performance_agent,
    validation_agent,
    test_code_dir
):
    # Test code with issues
    test_code = """
    def vulnerable_function(user_input):
        # Security issue
        exec(user_input)
        
        # Performance issue
        results = []
        for i in range(10000):
            results.append(i)
            
        # Validation issue
        global_var = 'bad practice'
    """
    
    # Get suggestions from each agent
    security_issues = await security_agent.analyze_code(
        test_code,
        str(test_code_dir / "test_suggestions.py")
    )
    performance_issues = await performance_agent.analyze_code(
        test_code,
        str(test_code_dir / "test_suggestions.py")
    )
    validation_issues = await validation_agent.validate_code(
        test_code,
        str(test_code_dir / "test_suggestions.py")
    )
    
    # Verify each agent provides actionable suggestions
    for issue in security_issues + performance_issues + validation_issues:
        assert issue.fix_suggestion is not None
        assert len(issue.fix_suggestion) > 0

@pytest.mark.asyncio
async def test_domain_specific_validation(validation_agent, test_code_dir):
    # Test financial domain code
    financial_code = """
    def process_payment(amount):
        # Using float for money
        total = float(amount)
        
        # Missing transaction handling
        db.execute("UPDATE balance SET amount = amount - %s", (total,))
    """
    
    issues = await validation_agent.validate_code(
        financial_code,
        str(test_code_dir / "test_financial.py"),
        domain="finance"
    )
    
    assert len(issues) > 0
    assert any(i.category == "domain" for i in issues)

@pytest.mark.asyncio
async def test_cross_agent_correlation(
    security_agent,
    performance_agent,
    validation_agent,
    test_code_dir
):
    # Test code with interrelated issues
    test_code = """
    def process_user_data(user_input):
        # Security + Performance issue
        results = []
        for i in range(1000):
            results.append(eval(user_input))  # Both security and performance
            
        # Validation + Security issue
        global_data = results  # Global state + potential tainted data
    """
    
    # Run all agents
    security_issues = await security_agent.analyze_code(
        test_code,
        str(test_code_dir / "test_correlation.py")
    )
    performance_issues = await performance_agent.analyze_code(
        test_code,
        str(test_code_dir / "test_correlation.py")
    )
    validation_issues = await validation_agent.validate_code(
        test_code,
        str(test_code_dir / "test_correlation.py")
    )
    
    # Verify issues are correlated
    assert len(security_issues) > 0
    assert len(performance_issues) > 0
    assert len(validation_issues) > 0
    
    # Check if issues reference the same line numbers
    security_lines = {i.location.split(':')[1] for i in security_issues}
    performance_lines = {i.location.split(':')[1] for i in performance_issues}
    validation_lines = {i.location.split(':')[1] for i in validation_issues}
    
    # There should be some overlap in the detected lines
    assert len(security_lines & performance_lines) > 0
