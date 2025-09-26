"""
Knowledge Graph Validation Package

This package ensures Claude and all AI systems respect the universal JSON schema
for the Chilean electrical system data processing project.

Components:
- SchemaValidator: Core validation engine
- ClaudeSchemaEnforcer: Claude-specific integration layer
- WorkflowIntegrator: Integration with existing workflows
- Usage examples and documentation

Usage:
    from ai_platform.knowledge_graph.validation import ClaudeSchemaEnforcer

    enforcer = ClaudeSchemaEnforcer()
    prompt = enforcer.create_extraction_prompt("operaciones", "anexo_01", text)
"""

from .schema_validator import SchemaValidator
from .claude_schema_enforcer import ClaudeSchemaEnforcer
from .workflow_integrator import WorkflowIntegrator

__all__ = ['SchemaValidator', 'ClaudeSchemaEnforcer', 'WorkflowIntegrator']
__version__ = '1.0.0'