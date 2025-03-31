from typing import Dict, List, Optional, Set
import logging
from pathlib import Path
import json
import yaml
from dataclasses import dataclass
import re
from collections import defaultdict

from .template_manager import TemplateManager, TemplateMetadata

logger = logging.getLogger(__name__)

@dataclass
class LanguageConfig:
    """Configuration for a programming language"""
    name: str
    extensions: List[str]
    frameworks: List[str]
    templates: List[str]
    patterns: List[str]
    best_practices: Dict[str, str]
    linting_rules: Dict[str, str]
    formatting_rules: Dict[str, str]

class LanguageGenerator:
    """Handles language-specific code generation and analysis"""
    
    def __init__(self, template_manager: TemplateManager):
        self.template_manager = template_manager
        self._load_config()
        self._setup_languages()
        self._language_configs = {}
        
    def _load_config(self) -> None:
        """Load language generator configuration"""
        try:
            config_path = Path("src/core/codegen/config/languages.yaml")
            if config_path.exists():
                with open(config_path, "r") as f:
                    self.config = yaml.safe_load(f)
            else:
                logger.warning("Language configuration not found")
                self.config = {}
                
        except Exception as e:
            logger.error(f"Error loading language configuration: {str(e)}")
            self.config = {}
            
    def _setup_languages(self) -> None:
        """Setup language configurations"""
        try:
            # Frontend languages
            self._setup_frontend_languages()
            
            # Backend languages
            self._setup_backend_languages()
            
            # Mobile languages
            self._setup_mobile_languages()
            
            # Data languages
            self._setup_data_languages()
            
        except Exception as e:
            logger.error(f"Error setting up languages: {str(e)}")
            
    def _setup_frontend_languages(self) -> None:
        """Setup frontend language configurations"""
        # HTML/CSS
        self._language_configs["html"] = LanguageConfig(
            name="HTML",
            extensions=[".html", ".htm"],
            frameworks=["HTML5"],
            templates={
                "basic": {
                    "name": "Basic HTML Template",
                    "description": "Basic HTML5 template with meta tags",
                    "content": """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{title}}</title>
    <link rel="stylesheet" href="{{css_path}}">
</head>
<body>
    <header>
        <nav>
            {{navigation}}
        </nav>
    </header>
    <main>
        {{content}}
    </main>
    <footer>
        {{footer_content}}
    </footer>
    <script src="{{js_path}}"></script>
</body>
</html>"""
                },
                "responsive": {
                    "name": "Responsive HTML Template",
                    "description": "Responsive HTML5 template with media queries",
                    "content": """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{title}}</title>
    <link rel="stylesheet" href="{{css_path}}">
    <style>
        /* Mobile First */
        @media (min-width: 768px) {
            /* Tablet */
        }
        @media (min-width: 1024px) {
            /* Desktop */
        }
    </style>
</head>
<body>
    <header>
        <nav class="responsive-nav">
            {{navigation}}
        </nav>
    </header>
    <main>
        {{content}}
    </main>
    <footer>
        {{footer_content}}
    </footer>
    <script src="{{js_path}}"></script>
</body>
</html>"""
                }
            },
            patterns={
                "semantic": r"<header>|<nav>|<main>|<article>|<section>|<aside>|<footer>",
                "responsive": r"@media\s*\([^)]+\)\s*{",
                "accessibility": r"aria-|role="
            },
            best_practices={
                "semantic": "Use semantic HTML elements",
                "responsive": "Implement responsive design",
                "accessibility": "Include ARIA attributes",
                "performance": "Optimize images and assets",
                "seo": "Use proper meta tags"
            },
            linting_rules={
                "htmlhint": {
                    "rules": {
                        "attr-lowercase": True,
                        "attr-value-double-quotes": True,
                        "doctype-first": True,
                        "tag-pair": True,
                        "spec-char-escape": True
                    }
                }
            },
            formatting_rules={
                "indent": 4,
                "max-line-length": 120,
                "quote-style": "double"
            }
        )

        # CSS
        self._language_configs["css"] = LanguageConfig(
            name="CSS",
            extensions=[".css", ".scss", ".sass", ".less"],
            frameworks=["CSS3", "SASS", "LESS"],
            templates={
                "reset": {
                    "name": "CSS Reset",
                    "description": "Modern CSS reset template",
                    "content": """/* Modern CSS Reset */
*, *::before, *::after {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}

html {
    font-size: 16px;
    scroll-behavior: smooth;
}

body {
    min-height: 100vh;
    text-rendering: optimizeSpeed;
    line-height: 1.5;
}

ul, ol {
    list-style: none;
}

img, picture, video, canvas, svg {
    display: block;
    max-width: 100%;
}

input, button, textarea, select {
    font: inherit;
}"""
                },
                "variables": {
                    "name": "CSS Variables",
                    "description": "CSS custom properties template",
                    "content": """:root {
    /* Colors */
    --primary-color: {{primary_color}};
    --secondary-color: {{secondary_color}};
    --accent-color: {{accent_color}};
    --text-color: {{text_color}};
    --background-color: {{background_color}};
    
    /* Typography */
    --font-family: {{font_family}};
    --font-size-base: {{font_size_base}};
    --line-height-base: {{line_height_base}};
    
    /* Spacing */
    --spacing-unit: {{spacing_unit}};
    --container-width: {{container_width}};
    
    /* Breakpoints */
    --breakpoint-sm: {{breakpoint_sm}};
    --breakpoint-md: {{breakpoint_md}};
    --breakpoint-lg: {{breakpoint_lg}};
}"""
                }
            },
            patterns={
                "variables": r"--[\w-]+:",
                "media-queries": r"@media\s*\([^)]+\)\s*{",
                "animations": r"@keyframes\s+\w+\s*{",
                "flexbox": r"display:\s*flex",
                "grid": r"display:\s*grid"
            },
            best_practices={
                "variables": "Use CSS custom properties",
                "responsive": "Implement mobile-first design",
                "performance": "Optimize selectors and properties",
                "maintainability": "Use BEM naming convention",
                "accessibility": "Ensure sufficient contrast"
            },
            linting_rules={
                "stylelint": {
                    "rules": {
                        "indentation": 4,
                        "string-quotes": "double",
                        "no-duplicate-selectors": True,
                        "color-hex-case": "lower",
                        "color-hex-length": "short"
                    }
                }
            },
            formatting_rules={
                "indent": 4,
                "max-line-length": 80,
                "quote-style": "double"
            }
        )

        # React
        self._language_configs["react"] = LanguageConfig(
            name="React",
            extensions=[".jsx", ".tsx"],
            frameworks=["React", "Next.js", "Gatsby"],
            templates={
                "component": {
                    "name": "React Component",
                    "description": "Modern React component template with hooks",
                    "content": """import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';

const {{component_name}} = ({ {{props}} }) => {
    const [state, setState] = useState({{initial_state}});
    
    useEffect(() => {
        {{effect_code}}
    }, [{{dependencies}}]);
    
    const handleEvent = () => {
        {{event_handler}}
    };
    
    return (
        <div className="{{component_class}}">
            {{component_content}}
        </div>
    );
};

{{component_name}}.propTypes = {
    {{prop_types}}
};

export default {{component_name}};"""
                },
                "hook": {
                    "name": "Custom Hook",
                    "description": "React custom hook template",
                    "content": """import { useState, useEffect } from 'react';

const use{{hook_name}} = ({{parameters}}) => {
    const [state, setState] = useState({{initial_state}});
    
    useEffect(() => {
        {{effect_code}}
    }, [{{dependencies}}]);
    
    const methods = {
        {{methods}}
    };
    
    return [state, methods];
};

export default use{{hook_name}};"""
                }
            },
            patterns={
                "hooks": r"use[A-Z]\w+",
                "components": r"function\s+\w+\s*\([^)]*\)\s*{|const\s+\w+\s*=\s*\([^)]*\)\s*=>",
                "props": r"PropTypes\.\w+"
            },
            best_practices={
                "hooks": "Use custom hooks for reusable logic",
                "components": "Keep components small and focused",
                "performance": "Use React.memo and useMemo",
                "state": "Use appropriate state management",
                "testing": "Write unit tests for components"
            },
            linting_rules={
                "eslint": {
                    "rules": {
                        "react-hooks/rules-of-hooks": "error",
                        "react-hooks/exhaustive-deps": "warn",
                        "react/prop-types": "error",
                        "react/jsx-uses-react": "error"
                    }
                }
            },
            formatting_rules={
                "indent": 4,
                "max-line-length": 100,
                "quote-style": "single"
            }
        )

        # Vue.js
        self._language_configs["vue"] = LanguageConfig(
            name="Vue",
            extensions=[".vue"],
            frameworks=["Vue.js", "Nuxt.js"],
            templates={
                "component": {
                    "name": "Vue Component",
                    "description": "Vue 3 component template with Composition API",
                    "content": """<template>
    <div class="{{component_class}}">
        {{template_content}}
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';

const props = defineProps({
    {{props}}
});

const emit = defineEmits(['{{events}}']);

const state = ref({{initial_state}});

onMounted(() => {
    {{mounted_code}}
});

const methods = {
    {{methods}}
};
</script>

<style scoped>
{{styles}}
</style>"""
                },
                "directive": {
                    "name": "Custom Directive",
                    "description": "Vue custom directive template",
                    "content": """import { DirectiveBinding } from 'vue';

export const {{directive_name}} = {
    mounted(el: HTMLElement, binding: DirectiveBinding) {
        {{mounted_code}}
    },
    updated(el: HTMLElement, binding: DirectiveBinding) {
        {{updated_code}}
    },
    unmounted(el: HTMLElement) {
        {{unmounted_code}}
    }
};"""
                }
            },
            patterns={
                "components": r"<template>.*?</template>",
                "directives": r"v-[a-z]+",
                "props": r"defineProps\s*\(\s*{[^}]*}\s*\)"
            },
            best_practices={
                "composition": "Use Composition API",
                "components": "Keep components focused",
                "state": "Use Pinia for state management",
                "performance": "Use v-show for frequent toggles",
                "testing": "Write component tests"
            },
            linting_rules={
                "eslint": {
                    "rules": {
                        "vue/multi-word-component-names": "error",
                        "vue/no-unused-components": "error",
                        "vue/no-unused-vars": "error"
                    }
                }
            },
            formatting_rules={
                "indent": 4,
                "max-line-length": 100,
                "quote-style": "single"
            }
        )

        # Angular
        self._language_configs["angular"] = LanguageConfig(
            name="Angular",
            extensions=[".ts"],
            frameworks=["Angular"],
            templates={
                "component": {
                    "name": "Angular Component",
                    "description": "Angular component template",
                    "content": """import { Component, OnInit } from '@angular/core';
import { {{imports}} } from '{{module_path}}';

@Component({
    selector: '{{selector}}',
    templateUrl: './{{component_name}}.component.html',
    styleUrls: ['./{{component_name}}.component.scss']
})
export class {{component_name}}Component implements OnInit {
    {{properties}}
    
    constructor({{dependencies}}) {}
    
    ngOnInit(): void {
        {{initialization}}
    }
    
    {{methods}}
}"""
                },
                "service": {
                    "name": "Angular Service",
                    "description": "Angular service template",
                    "content": """import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Injectable({
    providedIn: 'root'
})
export class {{service_name}}Service {
    constructor(private http: HttpClient) {}
    
    {{methods}}
}"""
                }
            },
            patterns={
                "decorators": r"@\w+\s*\([^)]*\)",
                "components": r"@Component\s*\([^)]*\)",
                "services": r"@Injectable\s*\([^)]*\)"
            },
            best_practices={
                "architecture": "Follow Angular architecture",
                "components": "Use smart and presentational components",
                "state": "Use NgRx for state management",
                "performance": "Use OnPush change detection",
                "testing": "Write unit and e2e tests"
            },
            linting_rules={
                "tslint": {
                    "rules": {
                        "component-class-suffix": True,
                        "directive-class-suffix": True,
                        "no-input-rename": True,
                        "no-output-rename": True
                    }
                }
            },
            formatting_rules={
                "indent": 4,
                "max-line-length": 100,
                "quote-style": "single"
            }
        )

        # ... (keep existing React, TypeScript, and JavaScript configurations)

    def _setup_backend_languages(self) -> None:
        """Setup backend language configurations"""
        backend_languages = {
            "python": {
                "extensions": [".py"],
                "frameworks": ["django", "flask", "fastapi"],
                "templates": ["model", "view", "service", "test"],
                "patterns": ["mvc_pattern", "repository_pattern"],
                "best_practices": {
                    "type_hints": "Use type hints for better code clarity",
                    "docstrings": "Include docstrings for all public functions",
                    "error_handling": "Use specific exception types"
                },
                "linting_rules": {
                    "max_line_length": 88,
                    "import_order": "alphabetical",
                    "naming_convention": "snake_case"
                },
                "formatting_rules": {
                    "indent_size": 4,
                    "quote_style": "double"
                }
            },
            "java": {
                "extensions": [".java"],
                "frameworks": ["spring", "quarkus", "micronaut"],
                "templates": ["class", "interface", "enum", "test"],
                "patterns": ["mvc_pattern", "repository_pattern", "factory_pattern"],
                "best_practices": {
                    "immutability": "Use immutable objects where possible",
                    "dependency_injection": "Use constructor injection",
                    "exception_handling": "Use specific exceptions"
                },
                "linting_rules": {
                    "max_line_length": 120,
                    "naming_convention": "camelCase",
                    "class_structure": "standard"
                },
                "formatting_rules": {
                    "indent_size": 4,
                    "brace_style": "end_of_line"
                }
            }
        }
        
        for lang, config in backend_languages.items():
            self._language_configs[lang] = LanguageConfig(name=lang, **config)
            
        # C#
        self._language_configs["csharp"] = LanguageConfig(
            name="C#",
            extensions=[".cs"],
            frameworks=[".NET", "ASP.NET Core", "Entity Framework"],
            templates={
                "class": {
                    "name": "C# Class",
                    "description": "C# class template with properties and methods",
                    "content": """using System;
using System.Collections.Generic;

namespace {{namespace}}
{
    public class {{class_name}}
    {
        {{properties}}
        
        public {{class_name}}({{parameters}})
        {
            {{initialization}}
        }
        
        {{methods}}
    }
}"""
                },
                "controller": {
                    "name": "ASP.NET Controller",
                    "description": "ASP.NET Core controller template",
                    "content": """using Microsoft.AspNetCore.Mvc;
using System.Threading.Tasks;

namespace {{namespace}}.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class {{controller_name}}Controller : ControllerBase
    {
        private readonly {{service_type}} _service;
        
        public {{controller_name}}Controller({{service_type}} service)
        {
            _service = service;
        }
        
        [HttpGet]
        public async Task<IActionResult> Get()
        {
            {{implementation}}
        }
        
        {{actions}}
    }
}"""
                }
            },
            patterns={
                "classes": r"class\s+\w+\s*{|interface\s+\w+\s*{",
                "methods": r"public\s+\w+\s+\w+\s*\([^)]*\)\s*{|private\s+\w+\s+\w+\s*\([^)]*\)\s*{",
                "properties": r"public\s+\w+\s+\w+\s*{\s*get;\s*set;\s*}"
            },
            best_practices={
                "architecture": "Follow SOLID principles",
                "async": "Use async/await properly",
                "error": "Implement proper error handling",
                "testing": "Write unit tests",
                "security": "Implement proper authentication"
            },
            linting_rules={
                "stylecop": {
                    "rules": {
                        "SA1200": "Using directives must be placed within namespace",
                        "SA1309": "Field names must not begin with underscore",
                        "SA1633": "File must have header"
                    }
                }
            },
            formatting_rules={
                "indent": 4,
                "max-line-length": 120,
                "quote-style": "double"
            }
        )

        # Go
        self._language_configs["go"] = LanguageConfig(
            name="Go",
            extensions=[".go"],
            frameworks=["Gin", "Echo", "Fiber"],
            templates={
                "package": {
                    "name": "Go Package",
                    "description": "Go package template",
                    "content": """package {{package_name}}

import (
    {{imports}}
)

{{type_definitions}}

{{function_definitions}}"""
                },
                "handler": {
                    "name": "HTTP Handler",
                    "description": "Go HTTP handler template",
                    "content": """package {{package_name}}

import (
    "net/http"
    "github.com/gin-gonic/gin"
)

type {{handler_name}} struct {
    {{dependencies}}
}

func New{{handler_name}}({{parameters}}) *{{handler_name}} {
    return &{{handler_name}}{
        {{initialization}}
    }
}

func (h *{{handler_name}}) Handle(c *gin.Context) {
    {{implementation}}
}"""
                }
            },
            patterns={
                "functions": r"func\s+\w+\s*\([^)]*\)\s*\w*\s*{|func\s*\(\s*\w+\s+\w+\s*\)\s+\w+\s*\([^)]*\)\s*\w*\s*{",
                "interfaces": r"type\s+\w+\s+interface\s*{",
                "structs": r"type\s+\w+\s+struct\s*{"
            },
            best_practices={
                "idioms": "Follow Go idioms",
                "error": "Handle errors properly",
                "testing": "Write table-driven tests",
                "concurrency": "Use goroutines and channels",
                "performance": "Use proper data structures"
            },
            linting_rules={
                "golint": {
                    "rules": {
                        "exported": "Exported names must be documented",
                        "unexported": "Unexported names should be lowercase"
                    }
                }
            },
            formatting_rules={
                "indent": 4,
                "max-line-length": 120,
                "quote-style": "double"
            }
        )

        # Node.js
        self._language_configs["nodejs"] = LanguageConfig(
            name="Node.js",
            extensions=[".js", ".ts"],
            frameworks=["Express", "NestJS", "Fastify"],
            templates={
                "express": {
                    "name": "Express Route",
                    "description": "Express.js route handler template",
                    "content": """const express = require('express');
const router = express.Router();
const {{service}} = require('../services/{{service}}');

router.get('/', async (req, res) => {
    try {
        {{implementation}}
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

module.exports = router;"""
                },
                "nest": {
                    "name": "NestJS Controller",
                    "description": "NestJS controller template",
                    "content": """import { Controller, Get, Post, Body } from '@nestjs/common';
import { {{service_name}}Service } from './{{service_name}}.service';

@Controller('{{route}}')
export class {{controller_name}}Controller {
    constructor(private readonly {{service_name}}Service: {{service_name}}Service) {}
    
    @Get()
    async findAll() {
        {{implementation}}
    }
    
    {{actions}}
}"""
                }
            },
            patterns={
                "routes": r"router\.(get|post|put|delete)\s*\(\s*['\"][^'\"]+['\"]",
                "middleware": r"app\.use\s*\(\s*[^)]+\)",
                "controllers": r"@Controller\s*\(\s*['\"][^'\"]+['\"]\s*\)"
            },
            best_practices={
                "async": "Use async/await properly",
                "error": "Implement proper error handling",
                "security": "Use security middleware",
                "testing": "Write unit tests",
                "logging": "Implement proper logging"
            },
            linting_rules={
                "eslint": {
                    "rules": {
                        "no-console": "warn",
                        "no-unused-vars": "error",
                        "prefer-const": "error"
                    }
                }
            },
            formatting_rules={
                "indent": 2,
                "max-line-length": 100,
                "quote-style": "single"
            }
        )

        # PHP
        self._language_configs["php"] = LanguageConfig(
            name="PHP",
            extensions=[".php"],
            frameworks=["Laravel", "Symfony", "CodeIgniter"],
            templates={
                "class": {
                    "name": "PHP Class",
                    "description": "PHP class template",
                    "content": """<?php

namespace {{namespace}};

class {{class_name}}
{
    {{properties}}
    
    public function __construct({{parameters}})
    {
        {{initialization}}
    }
    
    {{methods}}
}"""
                },
                "controller": {
                    "name": "Laravel Controller",
                    "description": "Laravel controller template",
                    "content": """<?php

namespace {{namespace}}\\Controllers;

use App\\Http\\Controllers\\Controller;
use Illuminate\\Http\\Request;

class {{controller_name}}Controller extends Controller
{
    public function index()
    {
        {{implementation}}
    }
    
    {{actions}}
}"""
                }
            },
            patterns={
                "classes": r"class\s+\w+\s*{|interface\s+\w+\s*{",
                "methods": r"public\s+function\s+\w+\s*\([^)]*\)",
                "properties": r"private\s+\$[\w_]+;|protected\s+\$[\w_]+;|public\s+\$[\w_]+;"
            },
            best_practices={
                "psr": "Follow PSR standards",
                "security": "Use prepared statements",
                "testing": "Write unit tests",
                "performance": "Use proper caching",
                "maintenance": "Follow SOLID principles"
            },
            linting_rules={
                "phpcs": {
                    "rules": {
                        "PSR2": True,
                        "Generic.WhiteSpace.ScopeIndent": True
                    }
                }
            },
            formatting_rules={
                "indent": 4,
                "max-line-length": 120,
                "quote-style": "single"
            }
        )

    def _setup_mobile_languages(self) -> None:
        """Setup mobile language configurations"""
        mobile_languages = {
            "swift": {
                "extensions": [".swift"],
                "frameworks": ["uikit", "swiftui"],
                "templates": ["view", "viewmodel", "service"],
                "patterns": ["mvvm_pattern", "coordinator_pattern"],
                "best_practices": {
                    "protocol_oriented": "Use protocols for abstraction",
                    "value_types": "Prefer structs over classes",
                    "error_handling": "Use Result type"
                },
                "linting_rules": {
                    "line_length": 120,
                    "naming_convention": "camelCase",
                    "force_unwrapping": "error"
                },
                "formatting_rules": {
                    "indent_size": 4,
                    "brace_style": "end_of_line"
                }
            },
            "kotlin": {
                "extensions": [".kt"],
                "frameworks": ["android"],
                "templates": ["activity", "fragment", "viewmodel"],
                "patterns": ["mvvm_pattern", "repository_pattern"],
                "best_practices": {
                    "null_safety": "Use nullable types properly",
                    "coroutines": "Use coroutines for async operations",
                    "data_classes": "Use data classes for models"
                },
                "linting_rules": {
                    "max_line_length": 120,
                    "naming_convention": "camelCase",
                    "no_wildcard_imports": "error"
                },
                "formatting_rules": {
                    "indent_size": 4,
                    "brace_style": "end_of_line"
                }
            }
        }
        
        for lang, config in mobile_languages.items():
            self._language_configs[lang] = LanguageConfig(name=lang, **config)
            
        # React Native
        self._language_configs["react-native"] = LanguageConfig(
            name="React Native",
            extensions=[".js", ".tsx"],
            frameworks=["React Native", "Expo"],
            templates={
                "component": {
                    "name": "React Native Component",
                    "description": "React Native component template",
                    "content": """import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import PropTypes from 'prop-types';

const {{component_name}} = ({ {{props}} }) => {
    return (
        <View style={styles.container}>
            {{component_content}}
        </View>
    );
};

const styles = StyleSheet.create({
    container: {
        {{styles}}
    }
});

{{component_name}}.propTypes = {
    {{prop_types}}
};

export default {{component_name}};"""
                },
                "screen": {
                    "name": "React Native Screen",
                    "description": "React Native screen template",
                    "content": """import React from 'react';
import { View, StyleSheet } from 'react-native';
import { useNavigation } from '@react-navigation/native';

const {{screen_name}} = () => {
    const navigation = useNavigation();
    
    return (
        <View style={styles.container}>
            {{screen_content}}
        </View>
    );
};

const styles = StyleSheet.create({
    container: {
        flex: 1,
        {{styles}}
    }
});

export default {{screen_name}};"""
                }
            },
            patterns={
                "components": r"const\s+\w+\s*=\s*\([^)]*\)\s*=>",
                "styles": r"StyleSheet\.create\s*\(\s*{[^}]*}\s*\)",
                "navigation": r"useNavigation\s*\(\s*\)"
            },
            best_practices={
                "performance": "Use proper list rendering",
                "navigation": "Implement proper navigation",
                "state": "Use appropriate state management",
                "styling": "Use StyleSheet for styles",
                "testing": "Write component tests"
            },
            linting_rules={
                "eslint": {
                    "rules": {
                        "react-native/no-unused-styles": "error",
                        "react-native/no-inline-styles": "warn",
                        "react-native/no-color-literals": "warn"
                    }
                }
            },
            formatting_rules={
                "indent": 4,
                "max-line-length": 100,
                "quote-style": "single"
            }
        )

        # Flutter
        self._language_configs["flutter"] = LanguageConfig(
            name="Flutter",
            extensions=[".dart"],
            frameworks=["Flutter"],
            templates={
                "widget": {
                    "name": "Flutter Widget",
                    "description": "Flutter widget template",
                    "content": """import 'package:flutter/material.dart';

class {{widget_name}} extends StatelessWidget {
    const {{widget_name}}({Key? key}) : super(key: key);
    
    @override
    Widget build(BuildContext context) {
        return {{widget_tree}};
    }
}"""
                },
                "stateful": {
                    "name": "Stateful Widget",
                    "description": "Flutter stateful widget template",
                    "content": """import 'package:flutter/material.dart';

class {{widget_name}} extends StatefulWidget {
    const {{widget_name}}({Key? key}) : super(key: key);
    
    @override
    State<{{widget_name}}> createState() => _{{widget_name}}State();
}

class _{{widget_name}}State extends State<{{widget_name}}> {
    {{state_variables}}
    
    @override
    void initState() {
        super.initState();
        {{initialization}}
    }
    
    @override
    Widget build(BuildContext context) {
        return {{widget_tree}};
    }
}"""
                }
            },
            patterns={
                "widgets": r"class\s+\w+\s+extends\s+(StatelessWidget|StatefulWidget)",
                "state": r"class\s+_\w+State\s+extends\s+State<",
                "build": r"@override\s+Widget\s+build\s*\(\s*BuildContext\s+context\s*\)"
            },
            best_practices={
                "widgets": "Keep widgets small",
                "state": "Use proper state management",
                "performance": "Use const constructors",
                "testing": "Write widget tests",
                "navigation": "Use proper navigation"
            },
            linting_rules={
                "dart": {
                    "rules": {
                        "prefer_const_constructors": True,
                        "prefer_const_declarations": True,
                        "avoid_print": True
                    }
                }
            },
            formatting_rules={
                "indent": 4,
                "max-line-length": 80,
                "quote-style": "single"
            }
        )

    def _setup_data_languages(self) -> None:
        """Setup data language configurations"""
        data_languages = {
            "sql": {
                "extensions": [".sql"],
                "frameworks": ["postgresql", "mysql", "sqlite"],
                "templates": ["table", "view", "procedure"],
                "patterns": ["normalization_pattern", "indexing_pattern"],
                "best_practices": {
                    "naming": "Use descriptive table and column names",
                    "indexing": "Create indexes on frequently queried columns",
                    "constraints": "Use appropriate constraints"
                },
                "linting_rules": {
                    "keyword_case": "upper",
                    "identifier_case": "lower",
                    "max_line_length": 120
                },
                "formatting_rules": {
                    "indent_size": 4,
                    "keyword_alignment": true
                }
            },
            "graphql": {
                "extensions": [".graphql"],
                "frameworks": ["apollo", "relay"],
                "templates": ["type", "query", "mutation"],
                "patterns": ["schema_pattern", "resolver_pattern"],
                "best_practices": {
                    "naming": "Use descriptive type and field names",
                    "deprecation": "Use @deprecated directive",
                    "documentation": "Include descriptions for types and fields"
                },
                "linting_rules": {
                    "naming_convention": "camelCase",
                    "max_depth": 10,
                    "no_deprecated": "warn"
                },
                "formatting_rules": {
                    "indent_size": 2,
                    "max_line_length": 100
                }
            }
        }
        
        for lang, config in data_languages.items():
            self._language_configs[lang] = LanguageConfig(name=lang, **config)
            
        # NoSQL
        self._language_configs["nosql"] = LanguageConfig(
            name="NoSQL",
            extensions=[".js", ".json"],
            frameworks=["MongoDB", "CouchDB", "Redis"],
            templates={
                "schema": {
                    "name": "MongoDB Schema",
                    "description": "MongoDB schema template",
                    "content": """const mongoose = require('mongoose');

const {{schema_name}}Schema = new mongoose.Schema({
    {{fields}}
}, {
    timestamps: true
});

module.exports = mongoose.model('{{model_name}}', {{schema_name}}Schema);"""
                },
                "query": {
                    "name": "MongoDB Query",
                    "description": "MongoDB query template",
                    "content": """const {{model_name}} = require('../models/{{model_name}}');

async function {{query_name}}({{parameters}}) {
    try {
        const result = await {{model_name}}.find({{query}})
            .select({{fields}})
            .sort({{sort}})
            .limit({{limit}});
            
        return result;
    } catch (error) {
        throw new Error(`{{error_message}}: ${error.message}`);
    }
}"""
                }
            },
            patterns={
                "schemas": r"new\s+mongoose\.Schema\s*\(\s*{[^}]*}\s*\)",
                "queries": r"\.find\s*\(\s*{[^}]*}\s*\)",
                "aggregations": r"\.aggregate\s*\(\s*\[[^\]]*\]\s*\)"
            },
            best_practices={
                "schema": "Design proper schemas",
                "indexing": "Use appropriate indexes",
                "queries": "Optimize queries",
                "security": "Implement proper access control",
                "performance": "Use proper data types"
            },
            linting_rules={
                "eslint": {
                    "rules": {
                        "no-unused-vars": "error",
                        "no-console": "warn"
                    }
                }
            },
            formatting_rules={
                "indent": 2,
                "max-line-length": 100,
                "quote-style": "single"
            }
        )

        # REST API
        self._language_configs["rest"] = LanguageConfig(
            name="REST API",
            extensions=[".yaml", ".json"],
            frameworks=["OpenAPI", "Swagger"],
            templates={
                "spec": {
                    "name": "OpenAPI Specification",
                    "description": "OpenAPI specification template",
                    "content": """openapi: 3.0.0
info:
    title: {{api_title}}
    version: {{api_version}}
    description: {{api_description}}

servers:
    - url: {{base_url}}
      description: {{server_description}}

paths:
    {{paths}}

components:
    schemas:
        {{schemas}}
    securitySchemes:
        {{security_schemes}}"""
                },
                "endpoint": {
                    "name": "REST Endpoint",
                    "description": "REST endpoint template",
                    "content": """    /{{path}}:
        {{methods}}:
            summary: {{summary}}
            description: {{description}}
            parameters:
                {{parameters}}
            requestBody:
                required: {{required}}
                content:
                    application/json:
                        schema:
                            {{schema}}
            responses:
                {{responses}}"""
                }
            },
            patterns={
                "paths": r"/[a-zA-Z0-9/{}]+:",
                "methods": r"(get|post|put|delete):",
                "schemas": r"type:\s*(object|array|string|number|boolean)"
            },
            best_practices={
                "design": "Follow REST principles",
                "versioning": "Implement proper versioning",
                "security": "Use proper authentication",
                "documentation": "Document all endpoints",
                "validation": "Validate requests/responses"
            },
            linting_rules={
                "swagger": {
                    "rules": {
                        "no-unused-schemas": True,
                        "no-unused-parameters": True,
                        "valid-schema": True
                    }
                }
            },
            formatting_rules={
                "indent": 2,
                "max-line-length": 100,
                "quote-style": "double"
            }
        )

    def get_language_config(self, language: str) -> Optional[LanguageConfig]:
        """Get configuration for a specific language"""
        return self._language_configs.get(language)
        
    def get_available_languages(self, category: Optional[str] = None) -> List[str]:
        """Get available languages filtered by category"""
        try:
            languages = list(self._language_configs.keys())
            
            if category:
                # Filter by category
                if category == "frontend":
                    languages = [lang for lang in languages 
                               if lang in ["javascript", "typescript"]]
                elif category == "backend":
                    languages = [lang for lang in languages 
                               if lang in ["python", "java", "c#", "go", "nodejs", "php"]]
                elif category == "mobile":
                    languages = [lang for lang in languages 
                               if lang in ["swift", "kotlin", "react_native", "flutter"]]
                elif category == "data":
                    languages = [lang for lang in languages 
                               if lang in ["sql", "nosql", "graphql", "rest"]]
                    
            return languages
            
        except Exception as e:
            logger.error(f"Error getting available languages: {str(e)}")
            return []
            
    def generate_code(self, language: str, template_name: str, context: Dict) -> str:
        """Generate code for a specific language using a template"""
        try:
            # Get language config
            config = self.get_language_config(language)
            if not config:
                raise ValueError(f"Language {language} not supported")
                
            # Validate template
            if template_name not in config.templates:
                raise ValueError(f"Template {template_name} not available for {language}")
                
            # Generate code using template manager
            return self.template_manager.generate_code(template_name, context)
            
        except Exception as e:
            logger.error(f"Error generating code for {language}: {str(e)}")
            raise
            
    def get_code_suggestions(self, language: str, code_context: str) -> List[Dict]:
        """Get language-specific code suggestions"""
        try:
            # Get language config
            config = self.get_language_config(language)
            if not config:
                return []
                
            # Get suggestions from template manager
            suggestions = self.template_manager.get_context_suggestions(code_context, language)
            
            # Add language-specific suggestions
            for pattern in config.patterns:
                pattern_suggestions = self._get_pattern_suggestions(pattern, code_context)
                suggestions.extend(pattern_suggestions)
                
            return suggestions
            
        except Exception as e:
            logger.error(f"Error getting code suggestions for {language}: {str(e)}")
            return []
            
    def _get_pattern_suggestions(self, pattern: str, code_context: str) -> List[Dict]:
        """Get suggestions based on a specific pattern"""
        try:
            suggestions = []
            
            # Load pattern configuration
            pattern_path = Path(f"src/core/codegen/patterns/{pattern}.json")
            if pattern_path.exists():
                with open(pattern_path, "r") as f:
                    pattern_config = json.load(f)
                    
                # Apply pattern matching
                for rule in pattern_config["rules"]:
                    matches = re.finditer(rule["regex"], code_context)
                    for match in matches:
                        suggestion = {
                            "pattern": pattern,
                            "description": rule["description"],
                            "code": rule["suggestion"],
                            "context": match.group(0),
                            "position": match.start()
                        }
                        suggestions.append(suggestion)
                        
            return suggestions
            
        except Exception as e:
            logger.error(f"Error getting pattern suggestions: {str(e)}")
            return []
            
    def validate_code(self, language: str, code: str) -> List[Dict]:
        """Validate code against language-specific rules"""
        try:
            # Get language config
            config = self.get_language_config(language)
            if not config:
                return []
                
            issues = []
            
            # Check linting rules
            for rule, level in config.linting_rules.items():
                if not self._check_linting_rule(code, rule, level):
                    issues.append({
                        "type": "linting",
                        "rule": rule,
                        "level": level,
                        "message": f"Violation of {rule} rule"
                    })
                    
            # Check formatting rules
            for rule, value in config.formatting_rules.items():
                if not self._check_formatting_rule(code, rule, value):
                    issues.append({
                        "type": "formatting",
                        "rule": rule,
                        "value": value,
                        "message": f"Violation of {rule} formatting rule"
                    })
                    
            return issues
            
        except Exception as e:
            logger.error(f"Error validating code for {language}: {str(e)}")
            return []
            
    def _check_linting_rule(self, code: str, rule: str, level: str) -> bool:
        """Check a specific linting rule"""
        try:
            # Implement rule checking logic
            if rule == "max_line_length":
                max_length = int(level)
                return all(len(line) <= max_length for line in code.splitlines())
            elif rule == "naming_convention":
                if level == "camelCase":
                    return self._check_camel_case(code)
                elif level == "snake_case":
                    return self._check_snake_case(code)
            # Add more rule checks as needed
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking linting rule {rule}: {str(e)}")
            return True
            
    def _check_formatting_rule(self, code: str, rule: str, value: bool) -> bool:
        """Check a specific formatting rule"""
        try:
            # Implement formatting rule checks
            if rule == "indent_size":
                return self._check_indent_size(code, value)
            elif rule == "brace_style":
                return self._check_brace_style(code, value)
            # Add more formatting checks as needed
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking formatting rule {rule}: {str(e)}")
            return True
            
    def _check_camel_case(self, code: str) -> bool:
        """Check if code follows camelCase naming convention"""
        pattern = r'[a-z][a-zA-Z0-9]*'
        return bool(re.match(pattern, code))
        
    def _check_snake_case(self, code: str) -> bool:
        """Check if code follows snake_case naming convention"""
        pattern = r'[a-z][a-z0-9_]*'
        return bool(re.match(pattern, code))
        
    def _check_indent_size(self, code: str, size: int) -> bool:
        """Check if code uses correct indentation size"""
        lines = code.splitlines()
        for line in lines:
            if line.strip():
                indent = len(line) - len(line.lstrip())
                if indent % size != 0:
                    return False
        return True
        
    def _check_brace_style(self, code: str, style: str) -> bool:
        """Check if code follows specified brace style"""
        if style == "end_of_line":
            pattern = r'[^{]\s*{\s*$'
        else:  # next_line
            pattern = r'[^{]\s*$\s*{'
        return bool(re.match(pattern, code)) 