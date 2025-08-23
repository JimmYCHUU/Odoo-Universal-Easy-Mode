# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class EasyModeToggler(models.TransientModel):
    _name = 'easy.mode.toggler'
    _description = 'Easy Mode Toggle Helper'

    @api.model
    def toggle_easy_mode(self, model_name=None):
        """Toggle Easy Mode for the specified model."""
        if not model_name:
            # Try to get from context
            model_name = self._context.get('active_model')
        
        if not model_name:
            raise UserError(_('No model specified for Easy Mode toggle.'))

        # Check if Easy Mode views exist for this model
        easy_views = self.env['ir.ui.view'].search([
            ('name', 'like', '[Easy Mode]'),
            ('model', '=', model_name),
        ])

        if not easy_views:
            raise UserError(_('Easy Mode is not available for model %s.') % model_name)

        # Determine current state
        is_easy_mode = any(view.priority == 1 for view in easy_views)
        
        # Toggle priorities
        new_priority = 99 if is_easy_mode else 1
        easy_views.write({'priority': new_priority})

        # Return result message
        mode_name = _('Full Mode') if is_easy_mode else _('Easy Mode')
        
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
            'params': {
                'message': _('Switched to %s') % mode_name
            }
        }

    @api.model
    def is_easy_mode_available(self, model_name):
        """Check if Easy Mode is available for a model."""
        easy_views = self.env['ir.ui.view'].search_count([
            ('name', 'like', '[Easy Mode]'),
            ('model', '=', model_name),
        ])
        return easy_views > 0

    @api.model
    def get_easy_mode_state(self, model_name):
        """Get current Easy Mode state for a model."""
        easy_views = self.env['ir.ui.view'].search([
            ('name', 'like', '[Easy Mode]'),
            ('model', '=', model_name),
        ])
        
        if not easy_views:
            return {'available': False, 'enabled': False}
        
        is_enabled = any(view.priority == 1 for view in easy_views)
        return {'available': True, 'enabled': is_enabled}
