{
    'name': 'Universal Easy Mode',
    'version': '17.0.1.1.0',
    'category': 'Tools',
    'summary': 'Provides simplified interface (Easy Mode) for selected modules',
    'description': '''
        Universal Easy Mode Module
        ==========================
        
        This module provides a simplified interface ("Easy Mode") for selected modules:
        
        * Admin can select installed modules to enable Easy Mode
        * Works with custom models and core modules
        * Shows only basic fields, hides advanced fields
        * Supports full CRUD operations in Easy Mode
        * Toggle between Easy Mode and Full Mode using systray button
        * Dynamic view generation using ir.model and ir.model.fields
        * Respects Odoo's security and access rights
        * Performance optimized with database-stored views
        * Simple, bulletproof core functionality
    ''',
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'web',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/easy_mode_config_views.xml',
        'views/easy_mode_actions.xml',
        'views/easy_mode_menus.xml',
        'views/test_views.xml',
    ],
    'demo': [
        'demo/demo_data.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'universal_easy_mode/static/src/css/easy_mode.css',
            'universal_easy_mode/static/src/js/easy_mode_toggle.js',
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': False,
}
