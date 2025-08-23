#!/usr/bin/env python3
"""
Simple validation script to check module structure
"""

import os
import json

def check_file_exists(path):
    """Check if file exists and return status"""
    exists = os.path.exists(path)
    print(f"{'✓' if exists else '✗'} {path}")
    return exists

def check_manifest():
    """Check manifest file"""
    print("Checking manifest.py...")
    if check_file_exists('__manifest__.py'):
        with open('__manifest__.py', 'r') as f:
            content = f.read()
            if "'name': 'Universal Easy Mode'" in content:
                print("✓ Module name found")
            if "'depends': [" in content:
                print("✓ Dependencies defined")
            if "'data': [" in content:
                print("✓ Data files defined")
            if "'assets': {" in content:
                print("✓ Assets defined")
    print()

def check_models():
    """Check model files"""
    print("Checking models...")
    check_file_exists('models/__init__.py')
    check_file_exists('models/easy_mode_view_override.py')
    check_file_exists('models/easy_mode_config.py')
    print()

def check_controllers():
    """Check controller files"""
    print("Checking controllers...")
    check_file_exists('controllers/__init__.py')
    check_file_exists('controllers/visual_editor_controller.py')
    print()

def check_views():
    """Check view files"""
    print("Checking views...")
    check_file_exists('views/visual_editor_views.xml')
    check_file_exists('views/easy_mode_menus.xml')
    print()

def check_static():
    """Check static files"""
    print("Checking static files...")
    check_file_exists('static/src/js/visual_editor.js')
    check_file_exists('static/src/js/visual_editor_action.js')
    check_file_exists('static/src/css/visual_editor.css')
    check_file_exists('static/src/xml/visual_editor_templates.xml')
    print()

def check_security():
    """Check security files"""
    print("Checking security...")
    check_file_exists('security/ir.model.access.csv')
    print()

if __name__ == "__main__":
    print("=== Universal Easy Mode Module Validation ===")
    print()
    
    check_manifest()
    check_models()
    check_controllers()
    check_views()
    check_static()
    check_security()
    
    print("=== Validation Complete ===")
