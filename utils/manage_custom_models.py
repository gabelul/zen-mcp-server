#!/usr/bin/env python3
"""Interactive utility for managing custom OpenAI models.

This script provides an interactive CLI interface for managing custom OpenAI models
via the OPENAI_CUSTOM_MODELS environment variable.
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional

# Add the parent directory to the path to import from providers
sys.path.insert(0, str(Path(__file__).parent.parent))

def load_env_file(env_path: str = ".env") -> Dict[str, str]:
    """Load environment variables from .env file."""
    env_vars = {}
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()
    return env_vars

def save_env_file(env_vars: Dict[str, str], env_path: str = ".env"):
    """Save environment variables to .env file."""
    # Create backup
    if os.path.exists(env_path):
        backup_path = f"{env_path}.backup"
        with open(env_path, 'r') as src, open(backup_path, 'w') as dst:
            dst.write(src.read())
        print(f"✅ Created backup: {backup_path}")
    
    with open(env_path, 'w') as f:
        for key, value in env_vars.items():
            f.write(f"{key}={value}\n")
    print(f"✅ Updated {env_path}")

def get_current_custom_models() -> Dict[str, Any]:
    """Get current custom models from environment."""
    env_vars = load_env_file()
    custom_models_json = env_vars.get("OPENAI_CUSTOM_MODELS", "{}")
    
    try:
        return json.loads(custom_models_json)
    except json.JSONDecodeError:
        print("⚠️  Invalid JSON in OPENAI_CUSTOM_MODELS, starting fresh")
        return {}

def save_custom_models(models: Dict[str, Any]):
    """Save custom models to environment file."""
    env_vars = load_env_file()
    env_vars["OPENAI_CUSTOM_MODELS"] = json.dumps(models, indent=None)
    save_env_file(env_vars)

def validate_model_config(config: Dict[str, Any]) -> bool:
    """Validate model configuration."""
    required_fields = ["context_window"]
    
    for field in required_fields:
        if field not in config:
            print(f"❌ Missing required field: {field}")
            return False
    
    if not isinstance(config["context_window"], int) or config["context_window"] <= 0:
        print("❌ context_window must be a positive integer")
        return False
    
    return True

def add_model():
    """Interactive model addition."""
    print("\n=== Add New Custom Model ===")
    
    model_name = input("Enter model name: ").strip()
    if not model_name:
        print("❌ Model name cannot be empty")
        return
    
    # Check if model already exists
    current_models = get_current_custom_models()
    if model_name in current_models:
        overwrite = input(f"Model '{model_name}' already exists. Overwrite? [y/N]: ").strip().lower()
        if overwrite != 'y':
            print("❌ Cancelled")
            return
    
    try:
        context_window = int(input("Enter context window (tokens): ").strip())
        if context_window <= 0:
            raise ValueError()
    except ValueError:
        print("❌ Context window must be a positive integer")
        return
    
    max_output_tokens = input("Enter max output tokens [4096]: ").strip()
    if max_output_tokens:
        try:
            max_output_tokens = int(max_output_tokens)
        except ValueError:
            print("❌ Max output tokens must be an integer")
            return
    else:
        max_output_tokens = 4096
    
    aliases_input = input("Enter aliases (comma-separated) []: ").strip()
    aliases = [alias.strip() for alias in aliases_input.split(",") if alias.strip()] if aliases_input else []
    
    # Boolean options with defaults
    supports_function_calling = input("Supports function calling? [Y/n]: ").strip().lower() not in ['n', 'no']
    supports_streaming = input("Supports streaming? [Y/n]: ").strip().lower() not in ['n', 'no']
    supports_images = input("Supports images? [y/N]: ").strip().lower() in ['y', 'yes']
    supports_json_mode = input("Supports JSON mode? [Y/n]: ").strip().lower() not in ['n', 'no']
    
    description = input(f"Description [{model_name} custom model]: ").strip()
    if not description:
        description = f"{model_name} custom model"
    
    # Build configuration
    config = {
        "context_window": context_window,
        "max_output_tokens": max_output_tokens,
        "supports_function_calling": supports_function_calling,
        "supports_streaming": supports_streaming,
        "supports_images": supports_images,
        "supports_json_mode": supports_json_mode,
        "description": description
    }
    
    if aliases:
        config["aliases"] = aliases
    
    if supports_images:
        max_image_size = input("Max image size (MB) [20.0]: ").strip()
        if max_image_size:
            try:
                config["max_image_size_mb"] = float(max_image_size)
            except ValueError:
                print("❌ Max image size must be a number")
                return
        else:
            config["max_image_size_mb"] = 20.0
    
    # Validate and save
    if not validate_model_config(config):
        return
    
    current_models[model_name] = config
    save_custom_models(current_models)
    
    print(f"✅ Model '{model_name}' added successfully!")
    if aliases:
        print(f"   Aliases: {', '.join(aliases)}")

def list_models():
    """List current custom models."""
    print("\n=== Current Custom Models ===")
    
    current_models = get_current_custom_models()
    if not current_models:
        print("No custom models configured.")
        return
    
    for model_name, config in current_models.items():
        aliases = config.get("aliases", [])
        alias_str = f" (aliases: {', '.join(aliases)})" if aliases else ""
        context = config.get("context_window", "unknown")
        max_tokens = config.get("max_output_tokens", "unknown")
        
        print(f"• {model_name}{alias_str}")
        print(f"  Context: {context:,} tokens, Max output: {max_tokens:,} tokens")
        print(f"  Description: {config.get('description', 'N/A')}")
        print()

def remove_model():
    """Remove a custom model."""
    print("\n=== Remove Custom Model ===")
    
    current_models = get_current_custom_models()
    if not current_models:
        print("No custom models to remove.")
        return
    
    print("Available models:")
    model_names = list(current_models.keys())
    for i, name in enumerate(model_names, 1):
        aliases = current_models[name].get("aliases", [])
        alias_str = f" (aliases: {', '.join(aliases)})" if aliases else ""
        print(f"{i}. {name}{alias_str}")
    
    try:
        choice = input("\nEnter model number to remove (or model name): ").strip()
        
        if choice.isdigit():
            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(model_names):
                model_to_remove = model_names[choice_idx]
            else:
                print("❌ Invalid choice")
                return
        else:
            if choice in current_models:
                model_to_remove = choice
            else:
                print(f"❌ Model '{choice}' not found")
                return
        
        confirm = input(f"Remove model '{model_to_remove}'? [y/N]: ").strip().lower()
        if confirm == 'y':
            del current_models[model_to_remove]
            save_custom_models(current_models)
            print(f"✅ Model '{model_to_remove}' removed successfully!")
        else:
            print("❌ Cancelled")
            
    except ValueError:
        print("❌ Invalid input")

def export_models():
    """Export models to a JSON file."""
    print("\n=== Export Models ===")
    
    current_models = get_current_custom_models()
    if not current_models:
        print("No custom models to export.")
        return
    
    filename = input("Export filename [custom_models.json]: ").strip()
    if not filename:
        filename = "custom_models.json"
    
    try:
        with open(filename, 'w') as f:
            json.dump(current_models, f, indent=2)
        print(f"✅ Models exported to {filename}")
    except Exception as e:
        print(f"❌ Export failed: {e}")

def import_models():
    """Import models from a JSON file."""
    print("\n=== Import Models ===")
    
    filename = input("Import filename: ").strip()
    if not filename or not os.path.exists(filename):
        print("❌ File not found")
        return
    
    try:
        with open(filename, 'r') as f:
            imported_models = json.load(f)
        
        if not isinstance(imported_models, dict):
            print("❌ Invalid file format")
            return
        
        current_models = get_current_custom_models()
        conflicts = set(imported_models.keys()) & set(current_models.keys())
        
        if conflicts:
            print(f"⚠️  Conflicting models: {', '.join(conflicts)}")
            overwrite = input("Overwrite existing models? [y/N]: ").strip().lower()
            if overwrite != 'y':
                print("❌ Import cancelled")
                return
        
        current_models.update(imported_models)
        save_custom_models(current_models)
        print(f"✅ Imported {len(imported_models)} models successfully!")
        
    except Exception as e:
        print(f"❌ Import failed: {e}")

def test_model():
    """Test a model connection (basic validation)."""
    print("\n=== Test Model ===")
    
    current_models = get_current_custom_models()
    if not current_models:
        print("No custom models to test.")
        return
    
    print("Available models:")
    model_names = list(current_models.keys())
    for i, name in enumerate(model_names, 1):
        print(f"{i}. {name}")
    
    try:
        choice = input("\nEnter model number to test (or model name): ").strip()
        
        if choice.isdigit():
            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(model_names):
                model_to_test = model_names[choice_idx]
            else:
                print("❌ Invalid choice")
                return
        else:
            if choice in current_models:
                model_to_test = choice
            else:
                print(f"❌ Model '{choice}' not found")
                return
        
        config = current_models[model_to_test]
        print(f"\n✅ Model configuration is valid for '{model_to_test}':")
        print(f"   Context window: {config['context_window']:,} tokens")
        print(f"   Max output: {config.get('max_output_tokens', 4096):,} tokens")
        
        aliases = config.get("aliases", [])
        if aliases:
            print(f"   Aliases: {', '.join(aliases)}")
        
        print(f"\n💡 To test actual API connectivity, use this model name in your MCP tools.")
        print(f"   Make sure OPENAI_BASE_URL is set to your custom endpoint.")
        
    except ValueError:
        print("❌ Invalid input")

def main():
    """Main interactive menu."""
    print("=== Custom OpenAI Models Manager ===")
    print("Manages models via OPENAI_CUSTOM_MODELS environment variable")
    
    while True:
        print("\nOptions:")
        print("1. Add new model")
        print("2. List current models")
        print("3. Remove model")
        print("4. Test model configuration")
        print("5. Export models to file")
        print("6. Import models from file")
        print("7. Exit")
        
        choice = input("\nChoice [1-7]: ").strip()
        
        if choice == "1":
            add_model()
        elif choice == "2":
            list_models()
        elif choice == "3":
            remove_model()
        elif choice == "4":
            test_model()
        elif choice == "5":
            export_models()
        elif choice == "6":
            import_models()
        elif choice == "7":
            print("Goodbye!")
            break
        else:
            print("❌ Invalid choice")

if __name__ == "__main__":
    main()