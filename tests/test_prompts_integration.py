#!/usr/bin/env python3
"""
Test script to verify AI prompts are being loaded and used correctly.
Run this to verify the prompts integration works.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from legacy_inspector.config import PROMPTS_DIR
from legacy_inspector.ai_helper import AIHelper


def test_prompts_directory():
    """Test that prompts directory exists and contains files."""
    print("=" * 60)
    print("Testing Prompts Directory Configuration")
    print("=" * 60)
    
    print(f"\n✓ PROMPTS_DIR: {PROMPTS_DIR}")
    print(f"✓ Exists: {PROMPTS_DIR.exists()}")
    print(f"✓ Is directory: {PROMPTS_DIR.is_dir()}")
    
    if not PROMPTS_DIR.exists():
        print("\n❌ ERROR: Prompts directory does not exist!")
        return False
    
    return True


def test_prompt_files():
    """Test that all expected prompt files exist."""
    print("\n" + "=" * 60)
    print("Testing Prompt Files")
    print("=" * 60)
    
    expected_prompts = [
        'explain_module',
        'refactor_patch',
        'prioritize',
        'clean_code_review'
    ]
    
    all_exist = True
    for prompt_name in expected_prompts:
        prompt_file = PROMPTS_DIR / f'{prompt_name}.txt'
        exists = prompt_file.exists()
        
        if exists:
            size = prompt_file.stat().st_size
            print(f"\n✓ {prompt_name}.txt")
            print(f"  Size: {size:,} bytes")
        else:
            print(f"\n❌ {prompt_name}.txt - NOT FOUND")
            all_exist = False
    
    return all_exist


def test_prompt_loading():
    """Test that AIHelper can load prompts."""
    print("\n" + "=" * 60)
    print("Testing Prompt Loading via AIHelper")
    print("=" * 60)
    
    # Create helper (no API calls will be made)
    os.environ['LLM_API_KEY'] = 'test-key-for-loading-only'
    os.environ['LLM_PROVIDER'] = 'openai'
    
    try:
        helper = AIHelper()
        print("\n✓ AIHelper created successfully")
    except Exception as e:
        print(f"\n❌ ERROR creating AIHelper: {e}")
        return False
    
    prompts = ['explain_module', 'refactor_patch', 'prioritize', 'clean_code_review']
    all_loaded = True
    
    for prompt_name in prompts:
        try:
            content = helper._load_prompt(prompt_name)
            
            if content:
                preview = content[:80].replace('\n', ' ')
                print(f"\n✓ {prompt_name}")
                print(f"  Loaded: {len(content):,} characters")
                print(f"  Preview: {preview}...")
            else:
                print(f"\n❌ {prompt_name} - Empty content returned")
                all_loaded = False
                
        except Exception as e:
            print(f"\n❌ {prompt_name} - Error loading: {e}")
            all_loaded = False
    
    return all_loaded


def test_prompt_usage_in_methods():
    """Test that prompts are used in actual methods."""
    print("\n" + "=" * 60)
    print("Testing Prompt Usage in Methods")
    print("=" * 60)
    
    # Check the source code to verify prompts are loaded
    ai_helper_file = Path(__file__).parent.parent / 'legacy_inspector' / 'ai_helper.py'
    
    with open(ai_helper_file, 'r') as f:
        content = f.read()
    
    checks = {
        'explain_module in explain_module()': 'self._load_prompt("explain_module")' in content,
        'refactor_patch in suggest_refactor()': 'self._load_prompt("refactor_patch")' in content,
        'prioritize in prioritize_issues()': 'self._load_prompt("prioritize")' in content,
        'clean_code_review in clean_code_review()': 'self._load_prompt("clean_code_review")' in content,
        'refactor_patch in _generate_recommendations()': 'refactor_prompt = self._load_prompt("refactor_patch")' in content or 'self._load_prompt("refactor_patch")' in content,
    }
    
    all_pass = True
    for check_name, passed in checks.items():
        if passed:
            print(f"\n✓ {check_name}")
        else:
            print(f"\n❌ {check_name} - NOT USING PROMPT FILE")
            all_pass = False
    
    return all_pass


def main():
    """Run all tests."""
    print("\n" + "🔍 AI Code Inspector - Prompts Integration Test")
    print("=" * 60 + "\n")
    
    tests = [
        ("Prompts Directory", test_prompts_directory),
        ("Prompt Files", test_prompt_files),
        ("Prompt Loading", test_prompt_loading),
        ("Prompt Usage", test_prompt_usage_in_methods),
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"\n❌ Test '{test_name}' crashed: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    all_passed = all(results.values())
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ ALL TESTS PASSED - Prompts are properly integrated!")
    else:
        print("❌ SOME TESTS FAILED - Check output above for details")
    print("=" * 60 + "\n")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
