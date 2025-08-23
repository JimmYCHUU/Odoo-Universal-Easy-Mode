# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)


class EasyModeFieldOverride(models.Model):
    _name = 'easy.mode.field.override'
    _description = 'Easy Mode Field Classification Override'
    _order = 'field_name'

    model_config_id = fields.Many2one(
        'easy.mode.model.config',
        'Model Configuration',
        required=True,
        ondelete='cascade'
    )
    field_name = fields.Char('Field Name', required=True)
    field_string = fields.Char('Field Label')
    field_type = fields.Selection([
        ('char', 'Char'),
        ('text', 'Text'),
        ('html', 'HTML'),
        ('integer', 'Integer'),
        ('float', 'Float'),
        ('monetary', 'Monetary'),
        ('boolean', 'Boolean'),
        ('date', 'Date'),
        ('datetime', 'DateTime'),
        ('selection', 'Selection'),
        ('many2one', 'Many2one'),
        ('one2many', 'One2many'),
        ('many2many', 'Many2many'),
        ('binary', 'Binary'),
        ('reference', 'Reference'),
        ('computed', 'Computed'),
        ('other', 'Other')
    ], 'Field Type', default='other')
    is_basic = fields.Boolean(
        'Show in Easy Mode',
        default=True,
        help='If checked, this field will be shown in Easy Mode'
    )
    is_required = fields.Boolean('Required')
    is_readonly = fields.Boolean('Readonly')
    has_groups = fields.Boolean('Has Groups Restriction')

    _sql_constraints = [
        ('unique_field_per_model', 'unique(model_config_id, field_name)',
         'Field name must be unique per model configuration!')
    ]

    @api.model
    def create(self, vals):
        """Override create to populate computed fields"""
        record = super().create(vals)
        if record.model_config_id and record.field_name:
            record._populate_field_info()
        return record
    
    def _populate_field_info(self):
        """Populate field information from the model definition."""
        for record in self:
            if not record.model_config_id or not record.field_name:
                continue
            
            try:
                model_obj = self.env[record.model_config_id.model]
                if record.field_name in model_obj._fields:
                    field_def = model_obj._fields[record.field_name]
                    
                    # Update field information
                    record.write({
                        'field_string': field_def.string or record.field_name.title(),
                        'field_type': record._map_field_type(field_def),
                        'is_required': getattr(field_def, 'required', False),
                        'is_readonly': getattr(field_def, 'readonly', False),
                        'has_groups': bool(getattr(field_def, 'groups', None))
                    })
                else:
                    # Field not found, set defaults
                    record.write({
                        'field_string': record.field_name.title(),
                        'field_type': 'other',
                        'is_required': False,
                        'is_readonly': False,
                        'has_groups': False
                    })
            except Exception as e:
                _logger.error(f'Error populating field info for {record.field_name}: {str(e)}')
                # Set safe defaults
                record.write({
                    'field_string': record.field_name.title(),
                    'field_type': 'other',
                    'is_required': False,
                    'is_readonly': False,
                    'has_groups': False
                })

    def _map_field_type(self, field_def):
        """Map Odoo field type to our selection values."""
        field_type = field_def.type
        
        # Map Odoo field types to our selection values
        type_mapping = {
            'char': 'char',
            'text': 'text', 
            'html': 'html',
            'integer': 'integer',
            'float': 'float',
            'monetary': 'monetary',
            'boolean': 'boolean',
            'date': 'date',
            'datetime': 'datetime',
            'selection': 'selection',
            'many2one': 'many2one',
            'one2many': 'one2many',
            'many2many': 'many2many',
            'binary': 'binary',
            'reference': 'reference'
        }
        
        # Check if field is computed without store
        if hasattr(field_def, 'compute') and field_def.compute and not field_def.store:
            return 'computed'
        
        return type_mapping.get(field_type, 'other')

    def action_set_all_basic(self):
        """Set all fields as basic (show in Easy Mode)."""
        self.search([('model_config_id', '=', self._context.get('active_id'))]).write({'is_basic': True})
        
    def action_set_all_advanced(self):
        """Set all fields as advanced (hide in Easy Mode)."""
        self.search([('model_config_id', '=', self._context.get('active_id'))]).write({'is_basic': False})
        
    def action_auto_classify(self):
        """Auto-classify fields based on default rules."""
        records = self.search([('model_config_id', '=', self._context.get('active_id'))])
        
        for record in records:
            # Basic field types
            basic_types = ['char', 'text', 'integer', 'float', 'monetary', 'date', 'datetime', 'boolean', 'selection', 'many2one']
            
            is_basic = (
                record.field_type in basic_types and
                not record.has_groups and
                not record.field_name.startswith('_')
            )
            
            # Special cases for advanced
            if record.field_type in ['one2many', 'many2many', 'binary'] or record.has_groups:
                is_basic = False
            
            record.is_basic = is_basic
