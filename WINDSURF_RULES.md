# Windsurf Rules for ADE Platform Development

Copy and paste these rules into your Windsurf settings to ensure consistent context and focused development across sessions.

## Context Maintenance Rules

```
Rule: Project Context Reading
Description: Before starting any development work, read the PROJECT_CONTEXT.md file to understand the overall vision and current state of the ADE platform as a comprehensive application development ecosystem with specialized AI agents.
Trigger: When starting a new chat or session related to ADE development
Action: Read the PROJECT_CONTEXT.md file and understand the project's vision, objectives, and current state

Rule: Implementation Plan Review
Description: Check the current implementation plan to understand priorities and ongoing tasks, with focus on the path to cloud deployment on cloudev.ai.
Trigger: When planning to implement new features or fix issues
Action: Review IMPLEMENTATION_PLAN.md to identify high-priority tasks and their dependencies

Rule: Active Tasks Review
Description: Review the current active tasks to understand what needs to be worked on and the status of ongoing tasks.
Trigger: When starting a new development session or planning work for the current session
Action: Review PROJECT_MANAGEMENT/ACTIVE_TASKS.md to identify tasks that need attention and their current status

Rule: Recent Implementation Reports
Description: Read recent implementation reports to understand what changes have been made to the platform's specialized agents and components.
Trigger: Before making changes to components or systems that may have been recently modified
Action: Check the IMPLEMENTATION_REPORTS directory for recent reports related to the area you're working on

Rule: Architecture Decision Awareness
Description: Be aware of architectural decisions that affect the multi-agent system and cloud deployment architecture.
Trigger: When making design decisions or implementing features that might have architectural implications
Action: Review relevant documents in the ARCHITECTURE_DECISIONS directory

Rule: Development Phase Awareness
Description: Understand which development phase the project is currently in (Local Testing, Cloud Preparation, or Initial Launch).
Trigger: When prioritizing tasks or making implementation decisions
Action: Check the current phase in PROJECT_MANAGEMENT.md and align work accordingly
```

## Development Process Rules

```
Rule: Task Status Updates
Description: Update task statuses in the implementation plan as work progresses toward cloud deployment.
Trigger: When starting or completing a task
Action: Update the status in IMPLEMENTATION_PLAN.md

Rule: Implementation Reporting
Description: Document significant implementation details for future reference, especially regarding specialized agent integration and cloud deployment preparation.
Trigger: After completing a significant feature or fix
Action: Create a new implementation report in the IMPLEMENTATION_REPORTS directory

Rule: Code Standards Adherence
Description: Follow established code standards for consistency across the platform.
Trigger: When writing or reviewing code
Action: Ensure code follows the standards outlined in PROJECT_MANAGEMENT.md

Rule: Continuous Integration
Description: Ensure all changes pass tests and don't break existing functionality of the specialized agents or their coordination.
Trigger: Before considering a task complete
Action: Run relevant tests and verify functionality
```

## Project Focus Rules

```
Rule: Multi-Agent System Focus
Description: Ensure all development work supports the multi-agent architecture of ADE.
Trigger: When designing or implementing features
Action: Verify that the work enhances or integrates with the specialized agent system

Rule: End-to-End Development Support
Description: Maintain focus on supporting the entire application development lifecycle.
Trigger: When implementing new features
Action: Consider how the feature contributes to the complete workflow from requirements to deployment

Rule: Cloud Deployment Path
Description: Prioritize work that moves the platform closer to cloud deployment on cloudev.ai.
Trigger: When prioritizing tasks
Action: Give higher priority to tasks that address cloud deployment requirements

Rule: User-Centric Development
Description: Consider the end-user experience of developers using ADE on cloudev.ai.
Trigger: When designing features or interfaces
Action: Evaluate how the feature will be used by developers creating applications on the platform
```

## How to Use These Rules

1. Copy the rule sections above
2. Go to Windsurf Settings
3. Find the Rules or Custom Instructions section
4. Paste the rules
5. Save your settings

These rules will help ensure that all development sessions maintain proper context and focus on advancing the ADE platform toward its goal of cloud deployment on cloudev.ai. They establish a consistent process for documenting decisions, tracking progress, and maintaining quality throughout the development lifecycle.
