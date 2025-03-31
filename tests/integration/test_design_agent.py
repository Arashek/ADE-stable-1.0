import pytest
import asyncio
from pathlib import Path
from backend.services.agents.specialized.design_agent import DesignAgent

@pytest.fixture
def test_design_dir():
    return Path(__file__).parent / 'test_design'

@pytest.fixture
def design_agent():
    return DesignAgent()

@pytest.mark.asyncio
async def test_accessibility_issues(design_agent, test_design_dir):
    # Test code with accessibility issues
    html_with_issues = """
    <div>
        <img src="image.jpg" />  <!-- Missing alt text -->
        <div tabindex="0" role="button">Click me</div>  <!-- No keyboard event handler -->
        <div style="color: #aaa; background-color: #eee;">Low contrast text</div>
    </div>
    """
    
    issues = await design_agent.analyze_design(
        html_with_issues, 
        str(test_design_dir / "accessibility.html")
    )
    
    assert len(issues) >= 1
    assert any('alt text' in i.description.lower() for i in issues)
    
    # Test code with proper accessibility
    html_accessible = """
    <div>
        <img src="image.jpg" alt="Descriptive alt text" />
        <button>Click me</button>
        <div style="color: #000; background-color: #fff;">High contrast text</div>
    </div>
    """
    
    issues = await design_agent.analyze_design(
        html_accessible, 
        str(test_design_dir / "accessibility_good.html")
    )
    
    # Should have fewer issues
    assert len([i for i in issues if 'alt text' in i.description.lower()]) == 0

@pytest.mark.asyncio
async def test_responsive_design(design_agent, test_design_dir):
    # Test code with responsive issues
    non_responsive_css = """
    .container {
        width: 1200px;  /* Fixed width */
    }
    
    .text {
        font-size: 16px;  /* Fixed font size */
    }
    
    .button {
        width: 200px;
        height: 50px;
    }
    """
    
    issues = await design_agent.analyze_design(
        non_responsive_css, 
        str(test_design_dir / "non_responsive.css")
    )
    
    assert len(issues) >= 1
    assert any('fixed' in i.description.lower() or 'pixel' in i.description.lower() for i in issues)
    
    # Test responsive code
    responsive_css = """
    .container {
        width: 100%;
        max-width: 1200px;
    }
    
    .text {
        font-size: 1rem;
    }
    
    .button {
        width: 100%;
        max-width: 200px;
        height: auto;
        padding: 0.75rem 1.5rem;
    }
    
    @media (max-width: 768px) {
        .text {
            font-size: 0.875rem;
        }
    }
    """
    
    issues = await design_agent.analyze_design(
        responsive_css, 
        str(test_design_dir / "responsive.css")
    )
    
    # Should have fewer responsive issues
    assert len([i for i in issues if 'responsive' in i.category.lower()]) < 2

@pytest.mark.asyncio
async def test_framework_specific(design_agent, test_design_dir):
    # Test React component
    react_component = """
    import React, { useState, useEffect } from 'react';
    
    function UserList() {
        const [users, setUsers] = useState([]);
        const [loading, setLoading] = useState(true);
        
        useEffect(() => {
            fetch('/api/users')
                .then(res => res.json())
                .then(data => {
                    setUsers(data);
                    setLoading(false);
                })
                .catch(err => {
                    console.error(err);
                    setLoading(false);
                });
        }, []);
        
        if (loading) return <div className="loading-spinner"></div>;
        
        if (users.length === 0) return <div className="empty-state">No users found</div>;
        
        return (
            <div className="user-list">
                {users.map(user => (
                    <div className="user-card">
                        <h3>{user.name}</h3>
                        <p>{user.email}</p>
                    </div>
                ))}
            </div>
        );
    }
    
    export default UserList;
    """
    
    issues = await design_agent.analyze_design(
        react_component, 
        str(test_design_dir / "UserList.jsx"),
        framework="react"
    )
    
    # Should detect missing key prop in React
    assert any('key prop' in i.description.lower() for i in issues)
    
    # Fixed React component
    fixed_react = """
    import React, { useState, useEffect } from 'react';
    
    function UserList() {
        const [users, setUsers] = useState([]);
        const [loading, setLoading] = useState(true);
        const [error, setError] = useState(null);
        
        useEffect(() => {
            fetch('/api/users')
                .then(res => res.json())
                .then(data => {
                    setUsers(data);
                    setLoading(false);
                })
                .catch(err => {
                    setError('Failed to load users');
                    setLoading(false);
                });
        }, []);
        
        if (loading) return <div className="loading-spinner"></div>;
        
        if (error) return <div className="error-state">{error}</div>;
        
        if (users.length === 0) return <div className="empty-state">No users found</div>;
        
        return (
            <div className="user-list">
                {users.map(user => (
                    <div className="user-card" key={user.id}>
                        <h3>{user.name}</h3>
                        <p>{user.email}</p>
                    </div>
                ))}
            </div>
        );
    }
    
    export default UserList;
    """
    
    issues = await design_agent.analyze_design(
        fixed_react, 
        str(test_design_dir / "UserListFixed.jsx"),
        framework="react"
    )
    
    # Should not have the key prop issue
    assert not any('key prop' in i.description.lower() for i in issues)

@pytest.mark.asyncio
async def test_design_patterns(design_agent, test_design_dir):
    # Missing loading and empty states
    missing_patterns = """
    function ProductList() {
        const products = fetchProducts();
        
        return (
            <div>
                {products.map(product => (
                    <ProductCard product={product} key={product.id} />
                ))}
            </div>
        );
    }
    """
    
    issues = await design_agent.analyze_design(
        missing_patterns, 
        str(test_design_dir / "missing_patterns.js")
    )
    
    # Should detect missing loading or empty states
    pattern_issues = [i for i in issues if 'pattern' in i.category.lower()]
    assert len(pattern_issues) >= 1
    
    # With proper patterns
    good_patterns = """
    function ProductList() {
        const [products, setProducts] = useState([]);
        const [isLoading, setIsLoading] = useState(true);
        const [error, setError] = useState(null);
        
        useEffect(() => {
            fetch('/api/products')
                .then(res => res.json())
                .then(data => {
                    setProducts(data);
                    setIsLoading(false);
                })
                .catch(err => {
                    setError('Failed to load products');
                    setIsLoading(false);
                });
        }, []);
        
        if (isLoading) {
            return (
                <div className="skeleton-loader">
                    <div className="skeleton-card"></div>
                    <div className="skeleton-card"></div>
                    <div className="skeleton-card"></div>
                </div>
            );
        }
        
        if (error) {
            return (
                <div className="error-state">
                    <p>{error}</p>
                    <button onClick={retry}>Try Again</button>
                </div>
            );
        }
        
        if (products.length === 0) {
            return (
                <div className="empty-state">
                    <p>No products found</p>
                    <button onClick={showAll}>View All Categories</button>
                </div>
            );
        }
        
        return (
            <div>
                {products.map(product => (
                    <ProductCard product={product} key={product.id} />
                ))}
            </div>
        );
    }
    """
    
    issues = await design_agent.analyze_design(
        good_patterns, 
        str(test_design_dir / "good_patterns.js")
    )
    
    # Should have fewer pattern issues
    pattern_issues = [i for i in issues if i.category.lower() == 'patterns']
    assert len(pattern_issues) == 0

@pytest.mark.asyncio
async def test_usability_issues(design_agent, test_design_dir):
    # Test form with usability issues
    form_with_issues = """
    <form>
        <input type="text" placeholder="Name" />
        <input type="email" placeholder="Email" />
        <input type="password" placeholder="Password" />
        <button type="submit">Submit</button>
    </form>
    """
    
    issues = await design_agent.analyze_design(
        form_with_issues, 
        str(test_design_dir / "form_issues.html")
    )
    
    # Should detect missing labels
    assert any('label' in i.description.lower() for i in issues)
    
    # Improved form
    improved_form = """
    <form>
        <div class="form-group">
            <label for="name">Name</label>
            <input type="text" id="name" name="name" />
        </div>
        <div class="form-group">
            <label for="email">Email</label>
            <input type="email" id="email" name="email" />
        </div>
        <div class="form-group">
            <label for="password">Password</label>
            <input type="password" id="password" name="password" />
            <small class="help-text">Password must be at least 8 characters</small>
        </div>
        <button type="submit">Submit</button>
    </form>
    """
    
    issues = await design_agent.analyze_design(
        improved_form, 
        str(test_design_dir / "form_improved.html")
    )
    
    # Should not have the label issue
    assert not any('missing form labels' in i.description.lower() for i in issues)

@pytest.mark.asyncio
async def test_consistency_analysis(design_agent, test_design_dir):
    # Code with inconsistent styling
    inconsistent_css = """
    .button-primary {
        background-color: #007bff;
        padding: 10px;
        border-radius: 4px;
    }
    
    .btn-secondary {
        background-color: #6d6d6d;
        padding: 12px 15px;
        border-radius: 5px;
    }
    
    .action_button {
        background: green;
        padding: 11px;
        border-radius: 3px;
    }
    """
    
    issues = await design_agent.analyze_design(
        inconsistent_css, 
        str(test_design_dir / "inconsistent.css")
    )
    
    # Should detect consistency issues
    consistency_issues = [i for i in issues if 'consistency' in i.category.lower()]
    assert len(consistency_issues) >= 1
    
    # Consistent styling
    consistent_css = """
    :root {
        --color-primary: #007bff;
        --color-secondary: #6d6d6d;
        --color-success: #28a745;
        --spacing-sm: 0.5rem;
        --spacing-md: 1rem;
        --spacing-lg: 1.5rem;
        --border-radius: 4px;
    }
    
    .button {
        padding: var(--spacing-md);
        border-radius: var(--border-radius);
        border: none;
    }
    
    .button-primary {
        background-color: var(--color-primary);
    }
    
    .button-secondary {
        background-color: var(--color-secondary);
    }
    
    .button-success {
        background-color: var(--color-success);
    }
    """
    
    issues = await design_agent.analyze_design(
        consistent_css, 
        str(test_design_dir / "consistent.css")
    )
    
    # Should have fewer consistency issues
    consistency_issues = [i for i in issues if 'consistency' in i.category.lower()]
    assert len(consistency_issues) < 2

@pytest.mark.asyncio
async def test_dark_mode_support(design_agent, test_design_dir):
    # CSS without dark mode
    no_dark_mode = """
    body {
        background-color: #ffffff;
        color: #333333;
    }
    
    .card {
        background-color: #f8f8f8;
        color: #222222;
        border: 1px solid #dddddd;
    }
    """
    
    improved_dark_mode = """
    :root {
        --bg-primary: #ffffff;
        --text-primary: #333333;
        --bg-secondary: #f8f8f8;
        --text-secondary: #222222;
        --border-color: #dddddd;
    }
    
    @media (prefers-color-scheme: dark) {
        :root {
            --bg-primary: #121212;
            --text-primary: #f0f0f0;
            --bg-secondary: #1e1e1e;
            --text-secondary: #e0e0e0;
            --border-color: #333333;
        }
    }
    
    body {
        background-color: var(--bg-primary);
        color: var(--text-primary);
    }
    
    .card {
        background-color: var(--bg-secondary);
        color: var(--text-secondary);
        border: 1px solid var(--border-color);
    }
    """
    
    # Save both files for testing
    dark_mode_dir = test_design_dir / "dark_mode"
    dark_mode_dir.mkdir(parents=True, exist_ok=True)
    
    with open(dark_mode_dir / "no_dark_mode.css", "w") as f:
        f.write(no_dark_mode)
    
    with open(dark_mode_dir / "dark_mode.css", "w") as f:
        f.write(improved_dark_mode)
    
    # Testing the implementation
    issues_before = await design_agent._check_design_consistency(
        no_dark_mode, 
        str(dark_mode_dir / "no_dark_mode.css")
    )
    
    issues_after = await design_agent._check_design_consistency(
        improved_dark_mode, 
        str(dark_mode_dir / "dark_mode.css")
    )
    
    # The improved version should have fewer consistency issues
    assert len(issues_after) <= len(issues_before)

@pytest.mark.asyncio
async def test_mobile_first_approach(design_agent, test_design_dir):
    # Desktop-first approach
    desktop_first = """
    .container {
        width: 1200px;
    }
    
    @media (max-width: 992px) {
        .container {
            width: 970px;
        }
    }
    
    @media (max-width: 768px) {
        .container {
            width: 750px;
        }
    }
    
    @media (max-width: 576px) {
        .container {
            width: 100%;
        }
    }
    """
    
    # Mobile-first approach
    mobile_first = """
    .container {
        width: 100%;
    }
    
    @media (min-width: 576px) {
        .container {
            width: 540px;
        }
    }
    
    @media (min-width: 768px) {
        .container {
            width: 720px;
        }
    }
    
    @media (min-width: 992px) {
        .container {
            width: 960px;
        }
    }
    
    @media (min-width: 1200px) {
        .container {
            width: 1140px;
        }
    }
    """
    
    # Save both files for testing
    responsive_dir = test_design_dir / "responsive"
    responsive_dir.mkdir(parents=True, exist_ok=True)
    
    with open(responsive_dir / "desktop_first.css", "w") as f:
        f.write(desktop_first)
    
    with open(responsive_dir / "mobile_first.css", "w") as f:
        f.write(mobile_first)
    
    # Testing both approaches
    desktop_first_issues = await design_agent._check_responsive_design(
        desktop_first, 
        str(responsive_dir / "desktop_first.css")
    )
    
    mobile_first_issues = await design_agent._check_responsive_design(
        mobile_first, 
        str(responsive_dir / "mobile_first.css")
    )
    
    # Mobile-first should have fewer responsive issues
    assert len(mobile_first_issues) <= len(desktop_first_issues)

@pytest.mark.asyncio
async def test_multi_framework_detection(design_agent):
    # React code
    react_code = """
    import React, { useState } from 'react';
    
    function Counter() {
        const [count, setCount] = useState(0);
        return (
            <div>
                <p>Count: {count}</p>
                <button onClick={() => setCount(count + 1)}>Increment</button>
            </div>
        );
    }
    """
    
    # Vue code
    vue_code = """
    <template>
        <div>
            <p>Count: {{ count }}</p>
            <button @click="increment">Increment</button>
        </div>
    </template>
    
    <script>
    export default {
        data() {
            return {
                count: 0
            }
        },
        methods: {
            increment() {
                this.count++
            }
        }
    }
    </script>
    """
    
    # Angular code
    angular_code = """
    import { Component } from '@angular/core';
    
    @Component({
        selector: 'app-counter',
        template: `
            <div>
                <p>Count: {{ count }}</p>
                <button (click)="increment()">Increment</button>
            </div>
        `
    })
    export class CounterComponent {
        count = 0;
        
        increment() {
            this.count++;
        }
    }
    """
    
    # Test framework detection
    react_framework = design_agent._detect_framework(react_code, "counter.jsx")
    vue_framework = design_agent._detect_framework(vue_code, "counter.vue")
    angular_framework = design_agent._detect_framework(angular_code, "counter.component.ts")
    
    assert react_framework == 'react'
    assert vue_framework == 'vue'
    assert angular_framework == 'angular'
