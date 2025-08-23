# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)


class EasyModeValidator(models.TransientModel):
    _name = 'easy.mode.validator'
    _description = 'Easy Mode Validation and Testing Helper'

    @api.model
    def validate_installation(self):
        """Validate that Easy Mode is properly installed and configured."""
        results = {
            'status': 'success',
            'errors': [],
            'warnings': [],
            'info': []
        }
        
        # Check if main models exist
        try:
            config_model = self.env['easy.mode.config']
            results['info'].append('✓ easy.mode.config model available')
        except Exception as e:
            results['errors'].append(f'✗ easy.mode.config model missing: {str(e)}')
            results['status'] = 'error'
        
        try:
            toggler_model = self.env['easy.mode.toggler']
            results['info'].append('✓ easy.mode.toggler model available')
        except Exception as e:
            results['errors'].append(f'✗ easy.mode.toggler model missing: {str(e)}')
            results['status'] = 'error'
        
        # Check if there are any configurations
        config_count = self.env['easy.mode.config'].search_count([])
        if config_count == 0:
            results['warnings'].append('⚠ No Easy Mode configurations found. Create one in Settings.')
        else:
            results['info'].append(f'✓ Found {config_count} Easy Mode configuration(s)')
        
        # Check if any Easy Mode views exist
        easy_views_count = self.env['ir.ui.view'].search_count([
            ('name', 'like', '[Easy Mode]')
        ])
        if easy_views_count == 0:
            results['warnings'].append('⚠ No Easy Mode views generated yet. Run "Generate Easy Views".')
        else:
            results['info'].append(f'✓ Found {easy_views_count} Easy Mode view(s)')
        
        return results

    @api.model
    def test_contacts_integration(self):
        """Test Easy Mode integration with the Contacts module."""
        results = {
            'status': 'success',
            'errors': [],
            'warnings': [],
            'info': []
        }
        
        # Check if contacts module is available
        partner_model = self.env.get('res.partner')
        if not partner_model:
            results['errors'].append('✗ res.partner model not available')
            results['status'] = 'error'
            return results
        
        results['info'].append('✓ res.partner model available')
        
        # Check if we can create a test configuration
        try:
            # Create test configuration
            test_config = self.env['easy.mode.config'].create({
                'name': 'Test Configuration - Contacts'
            })
            
            # Create model configuration for contacts
            model_config = self.env['easy.mode.model.config'].create({
                'config_id': test_config.id,
                'model': 'res.partner',
                'model_name': 'Contact',
                'enabled': True
            })
            
            # Generate field overrides
            model_config._ensure_field_overrides()
            
            # Test view generation
            model_config.generate_easy_views()
            
            # Check if views were created
            easy_views = self.env['ir.ui.view'].search([
                ('name', 'like', '[Easy Mode]'),
                ('model', '=', 'res.partner')
            ])
            
            if easy_views:
                results['info'].append(f'✓ Generated {len(easy_views)} Easy Mode views for contacts')
                
                # Test toggle functionality
                toggler = self.env['easy.mode.toggler']
                if toggler.is_easy_mode_available('res.partner'):
                    results['info'].append('✓ Easy Mode toggle available for contacts')
                else:
                    results['warnings'].append('⚠ Easy Mode toggle not available for contacts')
            else:
                results['warnings'].append('⚠ No Easy Mode views generated for contacts')
            
            # Clean up test data
            test_config.unlink()
            
        except Exception as e:
            results['errors'].append(f'✗ Error testing contacts integration: {str(e)}')
            results['status'] = 'error'
        
        return results

    @api.model
    def run_full_validation(self):
        """Run complete validation of Easy Mode functionality."""
        _logger.info('Starting Easy Mode validation...')
        
        all_results = {
            'installation': self.validate_installation(),
            'contacts_test': self.test_contacts_integration(),
            'summary': {'status': 'success', 'total_errors': 0, 'total_warnings': 0}
        }
        
        # Count total errors and warnings
        for test_name, results in all_results.items():
            if test_name == 'summary':
                continue
            if results.get('status') == 'error':
                all_results['summary']['status'] = 'error'
            all_results['summary']['total_errors'] += len(results.get('errors', []))
            all_results['summary']['total_warnings'] += len(results.get('warnings', []))
        
        _logger.info(f'Easy Mode validation completed. Status: {all_results["summary"]["status"]}')
        
        return all_results

    @api.model
    def create_demo_configuration(self):
        """Create a demo configuration for testing purposes."""
        # Check if demo config already exists
        existing_config = self.env['easy.mode.config'].search([
            ('name', 'ilike', 'demo')
        ], limit=1)
        
        if existing_config:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Demo Configuration'),
                    'message': _('Demo configuration already exists.'),
                    'type': 'info'
                }
            }
        
        # Create demo configuration
        demo_config = self.env['easy.mode.config'].create({
            'name': 'Demo Easy Mode Configuration'
        })
        
        # Add contacts module if available
        contacts_module = self.env['ir.module.module'].search([
            ('name', '=', 'contacts'),
            ('state', '=', 'installed')
        ], limit=1)
        
        if not contacts_module:
            # Try base module which contains res.partner
            contacts_module = self.env['ir.module.module'].search([
                ('name', '=', 'base'),
                ('state', '=', 'installed')
            ], limit=1)
        
        if contacts_module:
            demo_config.enabled_module_ids = [(6, 0, [contacts_module.id])]
            
            # Refresh models
            demo_config.action_refresh_models()
            
            # Generate views
            demo_config.action_generate_easy_views()
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'easy.mode.config',
            'res_id': demo_config.id,
            'view_mode': 'form',
            'target': 'current',
        }
