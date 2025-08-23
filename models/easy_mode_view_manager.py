# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class EasyModeViewManager(models.Model):
    """Extends ir.ui.view to add Easy Mode toggle functionality"""
    _inherit = 'ir.ui.view'

    @api.model
    def toggle_easy_mode_views(self, enable_easy_mode):
        """
        Toggle Easy Mode views by changing their priorities
        
        Args:
            enable_easy_mode (bool): True to enable Easy Mode, False to disable
            
        Returns:
            dict: Success status and message
        """
        try:
            _logger.info(f'Easy Mode: Toggling to {"ON" if enable_easy_mode else "OFF"}')
            
            # Find all Easy Mode views
            easy_mode_views = self.search([
                ('name', 'like', '[Easy Mode]')
            ])
            
            if not easy_mode_views:
                _logger.warning('Easy Mode: No Easy Mode views found')
                return {
                    'success': False,
                    'message': 'No Easy Mode views found. Please generate views first.'
                }
            
            # Get all models that have Easy Mode views
            models_with_easy_views = easy_mode_views.mapped('model')
            _logger.info(f'Easy Mode: Found views for models: {models_with_easy_views}')
            
            if enable_easy_mode:
                # Enable Easy Mode: Set Easy Mode views to high priority (1-10)
                # and standard views to low priority (100+)
                
                for view in easy_mode_views:
                    view.write({'priority': 1})
                    _logger.info(f'Easy Mode: Enabled view {view.name} (priority: 1)')
                
                # Lower priority of standard views for these models
                standard_views = self.search([
                    ('model', 'in', models_with_easy_views),
                    ('name', 'not like', '[Easy Mode]'),
                    ('type', 'in', ['tree', 'form']),
                    ('priority', '<', 50)  # Only affect views that might interfere
                ])
                
                for view in standard_views:
                    # Set to lower priority so Easy Mode views take precedence
                    view.write({'priority': 99})
                    _logger.info(f'Easy Mode: Lowered priority of {view.name} (priority: 99)')
                    
            else:
                # Disable Easy Mode: Set Easy Mode views to low priority
                # and restore standard views to normal priority
                
                for view in easy_mode_views:
                    view.write({'priority': 99})
                    _logger.info(f'Easy Mode: Disabled view {view.name} (priority: 99)')
                
                # Restore standard views to normal priority
                standard_views = self.search([
                    ('model', 'in', models_with_easy_views),
                    ('name', 'not like', '[Easy Mode]'),
                    ('type', 'in', ['tree', 'form']),
                    ('priority', '>', 50)  # Views we previously lowered
                ])
                
                for view in standard_views:
                    view.write({'priority': 16})  # Odoo default priority
                    _logger.info(f'Easy Mode: Restored priority of {view.name} (priority: 16)')
            
            # Clear view cache to ensure changes take effect
            self.clear_caches()
            
            success_message = f'Easy Mode {"enabled" if enable_easy_mode else "disabled"} for {len(models_with_easy_views)} models'
            _logger.info(f'Easy Mode: {success_message}')
            
            return {
                'success': True,
                'message': success_message,
                'models_affected': models_with_easy_views,
                'views_count': len(easy_mode_views)
            }
            
        except Exception as e:
            _logger.error(f'Easy Mode: Error toggling views: {str(e)}')
            return {
                'success': False,
                'message': f'Error toggling Easy Mode: {str(e)}'
            }
    
    @api.model 
    def get_easy_mode_status(self):
        """Get current Easy Mode status"""
        try:
            easy_mode_views = self.search([
                ('name', 'like', '[Easy Mode]'),
                ('priority', '<=', 10)  # High priority means enabled
            ])
            
            total_easy_views = self.search_count([('name', 'like', '[Easy Mode]')])
            
            is_enabled = len(easy_mode_views) > 0 and len(easy_mode_views) == total_easy_views
            
            return {
                'enabled': is_enabled,
                'active_views': len(easy_mode_views),
                'total_views': total_easy_views
            }
            
        except Exception as e:
            _logger.error(f'Easy Mode: Error getting status: {str(e)}')
            return {'enabled': False, 'active_views': 0, 'total_views': 0}
