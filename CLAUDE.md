# Claude Development Guide for Zen MCP Server

This file contains essential commands and workflows for developing and maintaining the Zen MCP Server when working with Claude. Use these instructions to efficiently run quality checks, manage the server, check logs, and run tests.

## Quick Reference Commands

### Code Quality Checks

Before making any changes or submitting PRs, always run the comprehensive quality checks:

```bash
# Activate virtual environment first
source venv/bin/activate

# Run all quality checks (linting, formatting, tests)
./code_quality_checks.sh
```

This script automatically runs:
- Ruff linting with auto-fix
- Black code formatting 
- Import sorting with isort
- Complete unit test suite (excluding integration tests)
- Verification that all checks pass 100%

**Run Integration Tests (requires API keys):**
```bash
# Run integration tests that make real API calls
./run_integration_tests.sh

# Run integration tests + simulator tests
./run_integration_tests.sh --with-simulator
```

### Server Management

#### Setup/Update the Server
```bash
# Run setup script (handles everything)
./run-server.sh
```

This script will:
- Set up Python virtual environment
- Install all dependencies
- Create/update .env file
- Configure MCP with Claude
- Verify API keys

#### View Logs
```bash
# Follow logs in real-time
./run-server.sh -f

# Or manually view logs
tail -f logs/mcp_server.log
```

### Log Management

#### View Server Logs
```bash
# View last 500 lines of server logs
tail -n 500 logs/mcp_server.log

# Follow logs in real-time
tail -f logs/mcp_server.log

# View specific number of lines
tail -n 100 logs/mcp_server.log

# Search logs for specific patterns
grep "ERROR" logs/mcp_server.log
grep "tool_name" logs/mcp_activity.log
```

#### Monitor Tool Executions Only
```bash
# View tool activity log (focused on tool calls and completions)
tail -n 100 logs/mcp_activity.log

# Follow tool activity in real-time
tail -f logs/mcp_activity.log

# Use simple tail commands to monitor logs
tail -f logs/mcp_activity.log | grep -E "(TOOL_CALL|TOOL_COMPLETED|ERROR|WARNING)"
```

#### Available Log Files

**Current log files (with proper rotation):**
```bash
# Main server log (all activity including debug info) - 20MB max, 10 backups
tail -f logs/mcp_server.log

# Tool activity only (TOOL_CALL, TOOL_COMPLETED, etc.) - 20MB max, 5 backups  
tail -f logs/mcp_activity.log
```

**For programmatic log analysis (used by tests):**
```python
# Import the LogUtils class from simulator tests
from simulator_tests.log_utils import LogUtils

# Get recent logs
recent_logs = LogUtils.get_recent_server_logs(lines=500)

# Check for errors
errors = LogUtils.check_server_logs_for_errors()

# Search for specific patterns
matches = LogUtils.search_logs_for_pattern("TOOL_CALL.*debug")
```

### Testing

Simulation tests are available to test the MCP server in a 'live' scenario, using your configured
API keys to ensure the models are working and the server is able to communicate back and forth. 

**IMPORTANT**: After any code changes, restart your Claude session for the changes to take effect.

#### Run All Simulator Tests
```bash
# Run the complete test suite
python communication_simulator_test.py

# Run tests with verbose output
python communication_simulator_test.py --verbose
```

#### Quick Test Mode (Recommended for Time-Limited Testing)
```bash
# Run quick test mode - 6 essential tests that provide maximum functionality coverage
python communication_simulator_test.py --quick

# Run quick test mode with verbose output
python communication_simulator_test.py --quick --verbose
```

**Quick mode runs these 6 essential tests:**
- `cross_tool_continuation` - Cross-tool conversation memory testing (chat, thinkdeep, codereview, analyze, debug)
- `conversation_chain_validation` - Core conversation threading and memory validation
- `consensus_workflow_accurate` - Consensus tool with flash model and stance testing
- `codereview_validation` - CodeReview tool with flash model and multi-step workflows
- `planner_validation` - Planner tool with flash model and complex planning workflows
- `token_allocation_validation` - Token allocation and conversation history buildup testing

**Why these 6 tests:** They cover the core functionality including conversation memory (`utils/conversation_memory.py`), chat tool functionality, file processing and deduplication, model selection (flash/flashlite/o3), and cross-tool conversation workflows. These tests validate the most critical parts of the system in minimal time.

**Note:** Some workflow tools (analyze, codereview, planner, consensus, etc.) require specific workflow parameters and may need individual testing rather than quick mode testing.

#### Run Individual Simulator Tests (For Detailed Testing)
```bash
# List all available tests
python communication_simulator_test.py --list-tests

# RECOMMENDED: Run tests individually for better isolation and debugging
python communication_simulator_test.py --individual basic_conversation
python communication_simulator_test.py --individual content_validation
python communication_simulator_test.py --individual cross_tool_continuation
python communication_simulator_test.py --individual memory_validation

# Run multiple specific tests
python communication_simulator_test.py --tests basic_conversation content_validation

# Run individual test with verbose output for debugging
python communication_simulator_test.py --individual memory_validation --verbose
```

Available simulator tests include:
- `basic_conversation` - Basic conversation flow with chat tool
- `content_validation` - Content validation and duplicate detection
- `per_tool_deduplication` - File deduplication for individual tools
- `cross_tool_continuation` - Cross-tool conversation continuation scenarios
- `cross_tool_comprehensive` - Comprehensive cross-tool file deduplication and continuation
- `line_number_validation` - Line number handling validation across tools
- `memory_validation` - Conversation memory validation
- `model_thinking_config` - Model-specific thinking configuration behavior
- `o3_model_selection` - O3 model selection and usage validation
- `ollama_custom_url` - Ollama custom URL endpoint functionality
- `openrouter_fallback` - OpenRouter fallback behavior when only provider
- `openrouter_models` - OpenRouter model functionality and alias mapping
- `token_allocation_validation` - Token allocation and conversation history validation
- `testgen_validation` - TestGen tool validation with specific test function
- `refactor_validation` - Refactor tool validation with codesmells
- `conversation_chain_validation` - Conversation chain and threading validation
- `consensus_stance` - Consensus tool validation with stance steering (for/against/neutral)

**Note**: All simulator tests should be run individually for optimal testing and better error isolation.

#### Run Unit Tests Only
```bash
# Run all unit tests (excluding integration tests that require API keys)
python -m pytest tests/ -v -m "not integration"

# Run specific test file
python -m pytest tests/test_refactor.py -v

# Run specific test function
python -m pytest tests/test_refactor.py::TestRefactorTool::test_format_response -v

# Run tests with coverage
python -m pytest tests/ --cov=. --cov-report=html -m "not integration"
```

#### Run Integration Tests (Uses Free Local Models)

**Setup Requirements:**
```bash
# 1. Install Ollama (if not already installed)
# Visit https://ollama.ai or use brew install ollama

# 2. Start Ollama service
ollama serve

# 3. Pull a model (e.g., llama3.2)
ollama pull llama3.2

# 4. Set environment variable for custom provider
export CUSTOM_API_URL="http://localhost:11434"
```

**Run Integration Tests:**
```bash
# Run integration tests that make real API calls to local models
python -m pytest tests/ -v -m "integration"

# Run specific integration test
python -m pytest tests/test_prompt_regression.py::TestPromptIntegration::test_chat_normal_prompt -v

# Run all tests (unit + integration)
python -m pytest tests/ -v
```

**Note**: Integration tests use the local-llama model via Ollama, which is completely FREE to run unlimited times. Requires `CUSTOM_API_URL` environment variable set to your local Ollama endpoint. They can be run safely in CI/CD but are excluded from code quality checks to keep them fast.

### Development Workflow

#### Before Making Changes
1. Ensure virtual environment is activated: `source .zen_venv/bin/activate`
2. Run quality checks: `./code_quality_checks.sh`
3. Check logs to ensure server is healthy: `tail -n 50 logs/mcp_server.log`

#### After Making Changes
1. Run quality checks again: `./code_quality_checks.sh`
2. Run integration tests locally: `./run_integration_tests.sh`
3. Run quick test mode for fast validation: `python communication_simulator_test.py --quick`
4. Run relevant specific simulator tests if needed: `python communication_simulator_test.py --individual <test_name>`
5. Check logs for any issues: `tail -n 100 logs/mcp_server.log`
6. Restart Claude session to use updated code

#### Before Committing/PR
1. Final quality check: `./code_quality_checks.sh`
2. Run integration tests: `./run_integration_tests.sh`
3. Run quick test mode: `python communication_simulator_test.py --quick`
4. Run full simulator test suite (optional): `./run_integration_tests.sh --with-simulator`
5. Verify all tests pass 100%

### Common Troubleshooting

#### Server Issues
```bash
# Check if Python environment is set up correctly
./run-server.sh

# View recent errors
grep "ERROR" logs/mcp_server.log | tail -20

# Check virtual environment
which python
# Should show: .../zen-mcp-server/.zen_venv/bin/python
```

#### Test Failures
```bash
# First try quick test mode to see if it's a general issue
python communication_simulator_test.py --quick --verbose

# Run individual failing test with verbose output
python communication_simulator_test.py --individual <test_name> --verbose

# Check server logs during test execution
tail -f logs/mcp_server.log

# Run tests with debug output
LOG_LEVEL=DEBUG python communication_simulator_test.py --individual <test_name>
```

#### Linting Issues
```bash
# Auto-fix most linting issues
ruff check . --fix
black .
isort .

# Check what would be changed without applying
ruff check .
black --check .
isort --check-only .
```

### File Structure Context

- `./code_quality_checks.sh` - Comprehensive quality check script
- `./run-server.sh` - Server setup and management
- `communication_simulator_test.py` - End-to-end testing framework
- `simulator_tests/` - Individual test modules
- `tests/` - Unit test suite
- `tools/` - MCP tool implementations
- `providers/` - AI provider implementations
- `systemprompts/` - System prompt definitions
- `logs/` - Server log files

### Custom OpenAI Models

You can add custom models to your OpenAI provider for use with custom endpoints:

#### Using Environment Variable
```bash
# Add to .env file
OPENAI_BASE_URL=https://your-custom-endpoint.com/v1
OPENAI_CUSTOM_MODELS='{"llama-3.1-405b": {"context_window": 128000, "max_output_tokens": 8192, "aliases": ["llama", "405b"]}, "mistral-large": {"context_window": 32000, "aliases": ["mistral"]}}'
```

#### Using Interactive Utility
```bash
# Run the interactive model manager
python utils/manage_custom_models.py

# This provides a menu-driven interface to:
# 1. Add new models with guided prompts
# 2. List current custom models
# 3. Remove models
# 4. Test model configurations
# 5. Export/import model configurations
```

#### Custom Model Configuration
Required fields:
- `context_window`: Token limit (integer)

Optional fields:
- `max_output_tokens`: Max response tokens (default: 4096)
- `aliases`: List of friendly names (default: [])
- `supports_function_calling`: Boolean (default: true)
- `supports_streaming`: Boolean (default: true)
- `supports_images`: Boolean (default: false)
- `supports_json_mode`: Boolean (default: true)
- `description`: Model description string

#### Usage Examples
After configuration, use alias names in MCP tools:
```bash
# If you defined aliases: ["llama", "405b"]
# You can use any of these in tool calls:
model: "llama-3.1-405b"  # Full name
model: "llama"           # Alias
model: "405b"            # Alias
```

### Environment Requirements

- Python 3.9+ with virtual environment
- All dependencies from `requirements.txt` installed
- Proper API keys configured in `.env` file

This guide provides everything needed to efficiently work with the Zen MCP Server codebase using Claude. Always run quality checks before and after making changes to ensure code integrity.


# Project Memory Instructions

You have access to a complete memory of this codebase. ALWAYS:
1. Search for existing implementations before writing new code
2. Use established patterns found in memory
3. Check for similar functions to avoid duplication
4. When debugging, search for similar errors that were fixed before
5. Follow the coding conventions found in existing code

## Memory Usage Examples
- Before creating a function: "I found 3 similar validation functions in memory..."
- When debugging: "This error pattern matches issue fixed in auth.js..."
- For refactoring: "Memory shows this pattern used in 5 places..."

## Enhanced Memory Graph Functions

### 🎯 Unified Search with entityTypes Filtering (MCP Only)
- mcp__zenmcp_memory__search_similar("query", entityTypes=["metadata"]) - 90% faster overview search
- mcp__zenmcp_memory__search_similar("query", entityTypes=["function", "class"]) - Find specific code elements
- mcp__zenmcp_memory__search_similar("query", entityTypes=["debugging_pattern"]) - Find past error solutions
- mcp__zenmcp_memory__search_similar("query", entityTypes=["documentation"]) - Search docs only
- mcp__zenmcp_memory__search_similar("query", entityTypes=["function", "metadata"]) - Mixed search with OR logic

### 📊 Codebase Mapping (with safe limits)
**General Analysis:**
- mcp__zenmcp_memory__read_graph(mode="smart", limit=100) - AI overview (max 150 entities)
- mcp__zenmcp_memory__read_graph(mode="entities", entityTypes=["class"], limit=50) - Filtered components  
- mcp__zenmcp_memory__read_graph(mode="relationships", limit=200) - Connections (max 300, careful!)

**Entity-Specific (10-20 relations vs 300+):**
- mcp__zenmcp_memory__read_graph(entity="ClassName", mode="smart") - AI analysis of specific component
- mcp__zenmcp_memory__read_graph(entity="functionName", mode="relationships") - Direct connections only
- mcp__zenmcp_memory__read_graph(entity="ServiceName", mode="entities") - Connected components

### 🔍 Implementation Access
- mcp__zenmcp_memory__get_implementation("name") - Just the code
- mcp__zenmcp_memory__get_implementation("name", "logical") - Include same-file helpers (max 20)
- mcp__zenmcp_memory__get_implementation("name", "dependencies") - Include imports/calls (max 30)

## Optimal Debugging Workflow

1. **Fast Discovery**: mcp__zenmcp_memory__search_similar("error", entityTypes=["metadata", "debugging_pattern"])
2. **Focus Analysis**: mcp__zenmcp_memory__read_graph(entity="ProblemFunction", mode="smart")
3. **Code Details**: mcp__zenmcp_memory__get_implementation("ProblemFunction", "dependencies")
4. **Store Solution**: After fixing, add pattern to memory for future

## Memory Power User Shortcuts (Optional)

Add these to your CLAUDE.md for enhanced memory usage:

- "§m" = Use project memory to find implementations, patterns, and architectural decisions
- "§d" = **Memory-search first for similar patterns, project memory if there is**, replicate the problem first, understand what is the error/problem ((same parameters and context) if you don't sure, ask!), use entity-specific debugging: search_similar to find target entity, then read_graph(entity="EntityName", mode="smart") for focused analysis (10-20 relations vs 300+), read related project logs, then debug deeper to find root cause (problem-focused, not solution-focused), show plan for fixing, if more info needed add debug prints. Don't fix until you made sure your fix will fix the exact same problem, just present findings (after receiving ok, fix with no code duping, check other possible function first, and do a test in the end to make sure this specific problem with this context and parameter solved).
- "$dup" = Don't duplicate code, check twice if there's a function that already does something similar prior to implementing what you want (use memory to check relations and best practices).

Note: This is my personal workflow that works well with Claude Code Memory.
Have better shortcuts or workflows? Share them: https://github.com/Durafen/Claude-code-memory/issues

---
*Auto-generated by claude-indexer add-mcp for collection: zenmcp*
*MCP Server: zenmcp-memory*
