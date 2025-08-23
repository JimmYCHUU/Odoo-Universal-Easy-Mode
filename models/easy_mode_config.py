# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)


class EasyModeConfig(models.Model):
    _name = 'easy.mode.config'
    _description = 'Easy Mode Configuration'
    _order = 'name'

    name = fields.Char('Configuration Name', required=True, default='Easy Mode Settings')
    active = fields.Boolean('Active', default=True)
    enabled_module_ids = fields.Many2many(
        'ir.module.module',
        'easy_mode_enabled_modules_rel',
        'config_id',
        'module_id',
        string='Enabled Modules',
        domain=[('state', '=', 'installed')],
        help='Select modules to enable Easy Mode for'
    )
    enabled_model_ids = fields.One2many(
        'easy.mode.model.config',
        'config_id',
        string='Configured Models',
        readonly=True
    )
    last_refresh = fields.Datetime('Last Refresh', readonly=True)
    view_count = fields.Integer('Generated Views Count', compute='_compute_view_count')
    
    @api.depends('enabled_model_ids')
    def _compute_view_count(self):
        for record in self:
            views = self.env['ir.ui.view'].search([
                ('name', 'like', '[Easy Mode]'),
                ('model', 'in', record.enabled_model_ids.mapped('model'))
            ])
            record.view_count = len(views)

    def action_refresh_models(self):
        """Detect and configure models from selected modules."""
        self.ensure_one()
        
        if not self.enabled_module_ids:
            raise UserError(_('Please select at least one module first.'))
        
        # Get all models
        all_models = self.env['ir.model'].search([])
        module_models = []
        
        for module in self.enabled_module_ids:
            # Method 1: Check if module name is in the modules field
            models_in_module = all_models.filtered(
                lambda m: m.modules and module.name in m.modules.split(',')
            )
            
            # Method 2: For CRM and other modules, also check model name patterns
            if module.name == 'crm':
                crm_models = all_models.filtered(
                    lambda m: m.model.startswith('crm.') or 
                    m.model in ['res.partner', 'calendar.event', 'mail.activity']
                )
                models_in_module |= crm_models
            elif module.name == 'sale':
                sale_models = all_models.filtered(
                    lambda m: m.model.startswith('sale.') or
                    m.model in ['product.product', 'product.template', 'res.partner']
                )
                models_in_module |= sale_models
            elif module.name == 'purchase':
                purchase_models = all_models.filtered(
                    lambda m: m.model.startswith('purchase.') or
                    m.model in ['product.product', 'product.template', 'res.partner']
                )
                models_in_module |= purchase_models
            elif module.name == 'stock':
                stock_models = all_models.filtered(
                    lambda m: m.model.startswith('stock.') or
                    m.model.startswith('procurement.') or
                    m.model in ['product.product', 'product.template']
                )
                models_in_module |= stock_models
            elif module.name == 'account':
                account_models = all_models.filtered(
                    lambda m: m.model.startswith('account.') or
                    m.model in ['res.partner', 'res.currency', 'product.product']
                )
                models_in_module |= account_models
            elif module.name == 'hr':
                hr_models = all_models.filtered(
                    lambda m: m.model.startswith('hr.')
                )
                models_in_module |= hr_models
            elif module.name == 'project':
                project_models = all_models.filtered(
                    lambda m: m.model.startswith('project.') or
                    m.model in ['res.partner']
                )
                models_in_module |= project_models
            elif module.name == 'base':
                # For base module, include core models
                base_models = all_models.filtered(
                    lambda m: m.model in ['res.partner', 'res.users', 'res.company', 'res.country']
                )
                models_in_module |= base_models
            
            module_models.extend(models_in_module.ids)
        
        # Remove duplicates
        module_models = list(set(module_models))
        
        # Filter out system/technical models but be more permissive
        excluded_prefixes = ['ir.', 'base.', 'mail.thread', 'mail.followers', 'bus.', 'web.', 'portal.']
        excluded_models = ['mail.message', 'mail.mail', 'mail.notification']
        
        valid_models = self.env['ir.model'].browse(module_models).filtered(
            lambda m: not any(m.model.startswith(prefix) for prefix in excluded_prefixes) and
            m.model not in excluded_models and
            m.field_id  # Must have fields defined
        )
        
        # Create or update model configurations
        existing_models = self.enabled_model_ids.mapped('model')
        created_count = 0
        
        _logger.info(f'Easy Mode: Processing {len(valid_models)} valid models')
        
        for model in valid_models:
            if model.model not in existing_models:
                _logger.info(f'Easy Mode: Creating config for {model.model} ({model.name})')
                self.env['easy.mode.model.config'].create({
                    'config_id': self.id,
                    'model': model.model,
                    'model_name': model.name,
                    'enabled': True
                })
                created_count += 1
            else:
                _logger.info(f'Easy Mode: Config already exists for {model.model}')
        
        # Remove models that are no longer in selected modules
        current_model_names = valid_models.mapped('model')
        outdated_configs = self.enabled_model_ids.filtered(
            lambda m: m.model not in current_model_names
        )
        if outdated_configs:
            _logger.info(f'Easy Mode: Removing {len(outdated_configs)} outdated configs')
            outdated_configs.unlink()
        
        self.last_refresh = fields.Datetime.now()
        
        # Log detailed information for debugging
        _logger.info(f'Easy Mode: Found {len(valid_models)} models for modules: {self.enabled_module_ids.mapped("name")}')
        for model in valid_models:
            _logger.info(f'Easy Mode: Added model {model.model} ({model.name})')
        
        # Return success message with model details
        model_names = ', '.join([f'{m.model} ({m.name})' for m in valid_models[:5]])  # Show first 5
        if len(valid_models) > 5:
            model_names += f', and {len(valid_models) - 5} more...'
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Models Refreshed'),
                'message': _('Found %s models: %s') % (len(valid_models), model_names) if valid_models else _('No models found! Check if the selected modules are installed and have data models.'),
                'sticky': True,
                'type': 'success' if valid_models else 'warning'
            }
        }

    def action_generate_easy_views(self):
        """Generate Easy Mode views for all enabled models."""
        self.ensure_one()
        
        enabled_models = self.enabled_model_ids.filtered('enabled')
        if not enabled_models:
            raise UserError(_('No models are enabled for Easy Mode.'))
        
        generated_count = 0
        for model_config in enabled_models:
            try:
                model_config.generate_easy_views()
                generated_count += 1
            except Exception as e:
                _logger.error(f'Failed to generate views for {model_config.model}: {str(e)}')
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Success'),
                'message': _('Generated Easy Mode views for %s models.') % generated_count,
                'sticky': False,
                'type': 'success'
            }
        }

    def action_view_generated_views(self):
        """Open list of generated Easy Mode views."""
        self.ensure_one()
        
        views = self.env['ir.ui.view'].search([
            ('name', 'like', '[Easy Mode]'),
            ('model', 'in', self.enabled_model_ids.mapped('model'))
        ])
        
        return {
            'name': _('Generated Easy Mode Views'),
            'type': 'ir.actions.act_window',
            'res_model': 'ir.ui.view',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', views.ids)],
            'context': {'create': False}
        }
    
    def action_debug_models(self):
        """Debug action to show what models are available and clean up invalid records"""
        self.ensure_one()
        
        try:
            # First, clean up any invalid field overrides
            cleanup_count = 0
            if self.enabled_model_ids:
                all_overrides = self.env['easy.mode.field.override'].search([
                    ('model_config_id', 'in', self.enabled_model_ids.ids)
                ])
                
                valid_field_types = ['char', 'text', 'html', 'integer', 'float', 'monetary', 
                                    'boolean', 'date', 'datetime', 'selection', 'many2one', 
                                    'one2many', 'many2many', 'binary', 'reference', 'computed', 'other']
                
                invalid_overrides = all_overrides.filtered(
                    lambda r: r.field_type not in valid_field_types
                )
                
                cleanup_count = len(invalid_overrides)
                if invalid_overrides:
                    invalid_overrides.unlink()
            
            # Check if CRM is installed
            crm_module = self.env['ir.module.module'].search([('name', '=', 'crm')])
            crm_status = f"CRM module: {crm_module.state if crm_module else 'Not found'}"
            
            # Get all models and show debugging info
            all_models = self.env['ir.model'].search([])
            total_models = len(all_models)
            
            # Check CRM models specifically
            crm_models = all_models.filtered(lambda m: 'crm' in m.model.lower() or m.model.startswith('crm.'))
            
            # Try to create test model configs for CRM
            test_models = ['crm.lead', 'crm.team', 'crm.stage']
            created_models = []
            
            for model_name in test_models:
                model_record = self.env['ir.model'].search([('model', '=', model_name)], limit=1)
                if model_record:
                    existing = self.env['easy.mode.model.config'].search([
                        ('config_id', '=', self.id),
                        ('model', '=', model_name)
                    ])
                    
                    if not existing:
                        new_config = self.env['easy.mode.model.config'].create({
                            'config_id': self.id,
                            'model': model_name,
                            'model_name': model_record.name,
                            'enabled': True
                        })
                        created_models.append(f"{model_name} (ID: {new_config.id})")
                    else:
                        created_models.append(f"{model_name} (already exists)")
                else:
                    created_models.append(f"{model_name} (model not found)")
            
            # Check current model configs
            current_count = len(self.enabled_model_ids)
            model_list = ', '.join([f'{m.model} ({m.id})' for m in self.enabled_model_ids])
            
            crm_info = '\n'.join([f'- {m.model} ({m.name})' for m in crm_models[:10]])
            
            message = f"""Debug & Cleanup Results:

{crm_status}
Total models in system: {total_models}
CRM models found: {len(crm_models)}

Cleaned up: {cleanup_count} invalid field overrides
Created/checked test models: {len(created_models)}
{chr(10).join([f'  - {m}' for m in created_models])}

Current model configs: {current_count}
Models: {model_list or 'None'}

Sample CRM models available:
{crm_info or 'No CRM models found'}

Selected modules: {', '.join(self.enabled_module_ids.mapped('name'))}
            """
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Debug & Cleanup Results'),
                    'message': message,
                    'sticky': True,
                    'type': 'info'
                }
            }
            
        except Exception as e:
            _logger.error(f'Error in action_debug_models: {str(e)}')
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Debug Error'),
                    'message': f'Error occurred: {str(e)}',
                    'sticky': True,
                    'type': 'danger'
                }
            }
    
    def action_test_refresh(self):
        """Simple test to create a few CRM model configs manually"""
        self.ensure_one()
        
        # Get CRM models that should definitely exist
        test_models = ['crm.lead', 'crm.team', 'crm.stage']
        created_models = []
        
        for model_name in test_models:
            model_record = self.env['ir.model'].search([('model', '=', model_name)], limit=1)
            if model_record:
                existing = self.env['easy.mode.model.config'].search([
                    ('config_id', '=', self.id),
                    ('model', '=', model_name)
                ])
                
                if not existing:
                    self.env['easy.mode.model.config'].create({
                        'config_id': self.id,
                        'model': model_name,
                        'model_name': model_record.name,
                        'enabled': True
                    })
                    created_models.append(model_name)
        
        # Check what we have now
        current_count = len(self.enabled_model_ids)
        model_list = ', '.join([f'{m.model}' for m in self.enabled_model_ids])
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Test Refresh Complete'),
                'message': _('Created: %s\nTotal count: %s\nModels: %s') % (', '.join(created_models) or 'None', current_count, model_list or 'None'),
                'sticky': True,
                'type': 'success'
            }
        }
    
    def action_cleanup_field_overrides(self):
        """Clean up any invalid field override records"""
        self.ensure_one()
        
        # Find all field overrides with invalid field_type values
        all_overrides = self.env['easy.mode.field.override'].search([
            ('model_config_id', 'in', self.enabled_model_ids.ids)
        ])
        
        valid_field_types = ['char', 'text', 'html', 'integer', 'float', 'monetary', 
                            'boolean', 'date', 'datetime', 'selection', 'many2one', 
                            'one2many', 'many2many', 'binary', 'reference', 'computed', 'other']
        
        invalid_overrides = all_overrides.filtered(
            lambda r: r.field_type not in valid_field_types
        )
        
        cleaned_count = len(invalid_overrides)
        if invalid_overrides:
            invalid_overrides.unlink()
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Cleanup Complete'),
                'message': _('Removed %s invalid field override records') % cleaned_count,
                'sticky': True,
                'type': 'success'
            }
        }


class EasyModeModelConfig(models.Model):
    _name = 'easy.mode.model.config'
    _description = 'Easy Mode Model Configuration'
    _order = 'model_name'

    config_id = fields.Many2one('easy.mode.config', 'Configuration', required=True, ondelete='cascade')
    model = fields.Char('Model Name', required=True)
    model_name = fields.Char('Display Name', required=True)
    enabled = fields.Boolean('Enable Easy Mode', default=True)
    field_override_ids = fields.One2many(
        'easy.mode.field.override',
        'model_config_id',
        string='Field Overrides'
    )
    easy_view_ids = fields.One2many(
        'ir.ui.view',
        compute='_compute_easy_views',
        string='Generated Easy Views'
    )
    
    @api.depends('model')
    def _compute_easy_views(self):
        for record in self:
            views = self.env['ir.ui.view'].search([
                ('name', 'like', '[Easy Mode]'),
                ('model', '=', record.model)
            ])
            record.easy_view_ids = views

    def action_configure_fields(self):
        """Open field override configuration for this model."""
        self.ensure_one()
        
        # Ensure field overrides exist for all fields
        self._ensure_field_overrides()
        
        return {
            'name': _('Configure Fields - %s') % self.model_name,
            'type': 'ir.actions.act_window',
            'res_model': 'easy.mode.field.override',
            'view_mode': 'tree',
            'domain': [('model_config_id', '=', self.id)],
            'context': {
                'default_model_config_id': self.id,
                'create': False,
                'delete': False
            }
        }

    def action_visual_editor(self):
        """Open the visual editor for this model."""
        self.ensure_one()
        
        # Open the main visual editor with the model pre-selected
        return {
            'name': _('Visual Editor - %s') % self.model_name,
            'type': 'ir.actions.act_window',
            'res_model': 'easy.mode.view.override',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_model_name': self.model,
                'default_name': f'Custom {self.model_name} View',
                'default_view_type': 'form'
            }
        }

    def _ensure_field_overrides(self):
        """Ensure all model fields have override configurations."""
        try:
            model_obj = self.env[self.model]
            existing_fields = self.field_override_ids.mapped('field_name')
            
            # Clean up any existing records with invalid field_type values
            invalid_overrides = self.field_override_ids.filtered(
                lambda r: r.field_type not in ['char', 'text', 'html', 'integer', 'float', 'monetary', 
                                               'boolean', 'date', 'datetime', 'selection', 'many2one', 
                                               'one2many', 'many2many', 'binary', 'reference', 'computed', 'other']
            )
            if invalid_overrides:
                _logger.info(f'Easy Mode: Removing {len(invalid_overrides)} invalid field overrides')
                invalid_overrides.unlink()
                # Refresh existing_fields after cleanup
                existing_fields = self.field_override_ids.mapped('field_name')
            
            for field_name, field_def in model_obj._fields.items():
                if field_name not in existing_fields and not field_name.startswith('_'):
                    field_type = self._get_odoo_field_type(field_def)
                    is_basic = self._is_basic_field(field_name, field_def)
                    
                    # Create field override with all information populated
                    field_override = self.env['easy.mode.field.override'].create({
                        'model_config_id': self.id,
                        'field_name': field_name,
                        'field_type': field_type,
                        'is_basic': is_basic,
                        'field_string': field_def.string or field_name.title(),
                        'is_required': getattr(field_def, 'required', False),
                        'is_readonly': getattr(field_def, 'readonly', False),
                        'has_groups': bool(getattr(field_def, 'groups', None))
                    })
        except Exception as e:
            _logger.error(f'Error in _ensure_field_overrides for model {self.model}: {str(e)}')
            raise

    def _get_odoo_field_type(self, field_def):
        """Get the Odoo field type for the selection field."""
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
        
        if hasattr(field_def, 'compute') and field_def.compute and not field_def.store:
            return 'computed'
        
        return type_mapping.get(field_type, 'other')

    def _classify_field(self, field_name, field_def):
        """Classify field as basic or advanced based on type and properties."""
        # This method is deprecated, use _is_basic_field instead
        return self._is_basic_field(field_name, field_def)

    def _is_basic_field(self, field_name, field_def):
        """Determine if a field should be considered basic (shown in Easy Mode).
        
        STRICT CRITERIA: Only truly essential business fields
        """
        field_type = field_def.type
        
        # Check if field requires technical groups - automatically advanced
        if hasattr(field_def, 'groups') and field_def.groups:
            groups = field_def.groups.split(',')
            technical_groups = ['base.group_system', 'base.group_no_one']
            if any(group.strip() in technical_groups for group in groups):
                return False
        
        # Check if field is computed without store - automatically advanced
        if field_def.compute and not field_def.store:
            return False
        
        # ESSENTIAL BUSINESS FIELDS ONLY - very restrictive list
        essential_fields = {
            # Core identification
            'name', 'display_name',
            # Contact information  
            'partner_name', 'email_from', 'phone', 'email', 'mobile',
            # Business workflow
            'stage_id', 'state', 'user_id', 'team_id',
            # Financial
            'expected_revenue', 'amount', 'price', 'total',
            # Dates (only current/future)
            'date_deadline', 'date_open', 'date_closed'
        }
        
        # Field must be in essential list AND have appropriate type
        if field_name not in essential_fields:
            return False
        
        # Essential field types for business users
        business_types = ['char', 'text', 'integer', 'float', 'monetary', 
                         'date', 'datetime', 'boolean', 'selection', 'many2one']
        
        return field_type in business_types

    def generate_easy_views(self):
        """Generate Easy Mode tree and form views for this model."""
        self.ensure_one()
        
        if not self.enabled:
            return
        
        # Ensure field overrides exist
        self._ensure_field_overrides()
        
        # Get basic fields
        basic_fields = self.field_override_ids.filtered('is_basic').mapped('field_name')
        
        if not basic_fields:
            _logger.warning(f'No basic fields found for model {self.model}')
            return
        
        # Generate tree view
        self._generate_tree_view(basic_fields)
        
        # Generate form view
        self._generate_form_view(basic_fields)

    def _generate_tree_view(self, basic_fields):
        """Generate Easy Mode tree view."""
        model_obj = self.env[self.model]
        
        # Build tree view XML - prioritize important fields first
        priority_fields = ['name', 'display_name', 'sequence', 'active', 'state']
        tree_fields = []
        
        # Add priority fields first if they exist and are basic
        for field_name in priority_fields:
            if field_name in basic_fields and field_name in model_obj._fields:
                field_def = model_obj._fields[field_name]
                attrs = self._get_field_attributes(field_def)
                tree_fields.append(f'                <field name="{field_name}"{attrs}/>')
                basic_fields = [f for f in basic_fields if f != field_name]
        
        # Add remaining basic fields (limit to 8 total for tree view)
        max_remaining = 8 - len(tree_fields)
        for field_name in basic_fields[:max_remaining]:
            if field_name in model_obj._fields:
                field_def = model_obj._fields[field_name]
                attrs = self._get_field_attributes(field_def)
                tree_fields.append(f'                <field name="{field_name}"{attrs}/>')
        
        if not tree_fields:
            tree_fields.append('                <field name="id"/>')
        
        arch_content = f'''<tree>
{chr(10).join(tree_fields)}
            </tree>'''
        
        # Create or update view
        view_name = f'[Easy Mode] {self.model_name} Tree'
        self._create_or_update_view(view_name, 'tree', arch_content)

    def _generate_form_view(self, basic_fields):
        """Generate Easy Mode form view with MAXIMUM simplicity."""
        model_obj = self.env[self.model]
        
        # STRICT LIMIT: Only 5-7 most essential fields
        essential_fields = ['name', 'partner_name', 'email_from', 'phone', 'stage_id', 'user_id', 'expected_revenue']
        
        # Filter basic fields to only include truly essential ones
        limited_basic_fields = []
        for field_name in essential_fields:
            if field_name in basic_fields and field_name in model_obj._fields:
                limited_basic_fields.append(field_name)
        
        # If no essential fields found, take first 5 basic fields
        if not limited_basic_fields:
            limited_basic_fields = [f for f in basic_fields[:5] if f in model_obj._fields]
        
        _logger.info(f'Easy Mode: Creating simplified form with {len(limited_basic_fields)} fields: {limited_basic_fields}')
        
        # Determine invisible fields needed for domain evaluations
        invisible_fields = []
        
        # For CRM Lead model - add team_id for stage_id domain and company_id for user_id domain
        if self.model == 'crm.lead':
            if 'stage_id' in limited_basic_fields and 'team_id' not in limited_basic_fields:
                invisible_fields.append('team_id')
            if 'user_id' in limited_basic_fields and 'company_id' not in limited_basic_fields:
                invisible_fields.append('company_id')
        
        # For CRM Team model - add company_id for user_id domain  
        elif self.model == 'crm.team':
            if 'user_id' in limited_basic_fields and 'company_id' not in limited_basic_fields:
                invisible_fields.append('company_id')
                
        # For CRM Team Member model - add user_company_ids for user_id domain
        elif self.model == 'crm.team.member':
            if 'user_id' in limited_basic_fields:
                if 'user_company_ids' not in limited_basic_fields:
                    invisible_fields.append('user_company_ids')
                if 'company_id' not in limited_basic_fields:
                    invisible_fields.append('company_id')
                if 'user_in_teams_ids' not in limited_basic_fields:
                    invisible_fields.append('user_in_teams_ids')
        
        # Build minimal form XML - start with form structure
        form_content = []
        
        # Add header if stage_id is present (needs to be first in form, OUTSIDE sheet)
        has_header = 'stage_id' in limited_basic_fields
        if has_header:
            form_content.append('                <header>')
            form_content.append('                    <field name="stage_id" widget="statusbar" options="{\'clickable\': \'1\'}"/>')
            form_content.append('                </header>')
            # Remove stage_id from remaining fields  
            limited_basic_fields = [f for f in limited_basic_fields if f != 'stage_id']
        
        # Start sheet
        form_content.append('                <sheet>')
        
        # Add invisible fields FIRST in sheet for domain validation
        _logger.info(f'Easy Mode: Adding invisible fields for {self.model}: {invisible_fields}')
        for field_name in invisible_fields:
            if field_name in model_obj._fields:
                form_content.append(f'                    <field name="{field_name}" invisible="1"/>')
                _logger.info(f'Easy Mode: Added invisible field {field_name}')
        
        # Add title field if name exists
        if 'name' in limited_basic_fields:
            form_content.append('                    <div class="oe_title">')
            form_content.append('                        <h1>')
            form_content.append('                            <field name="name" placeholder="Opportunity Name..."/>')
            form_content.append('                        </h1>')
            form_content.append('                    </div>')
            # Remove name from remaining fields
            limited_basic_fields = [f for f in limited_basic_fields if f != 'name']
        
        # Add remaining fields in a single simple group
        if limited_basic_fields:
            form_content.append('                    <group>')
            for field_name in limited_basic_fields:
                field_def = model_obj._fields[field_name]
                attrs = self._get_field_attributes(field_def)
                form_content.append(f'                        <field name="{field_name}"{attrs}/>')
            form_content.append('                    </group>')
        
        form_content.append('                </sheet>')
        
        arch_content = f'''<form>
{chr(10).join(form_content)}
            </form>'''
        
        # Create or update view
        view_name = f'[Easy Mode] {self.model_name} Form'
        self._create_or_update_view(view_name, 'form', arch_content)

    def _get_field_attributes(self, field_def, is_title=False):
        """Get appropriate attributes for a field based on its type."""
        attrs = []
        
        if field_def.type == 'boolean':
            attrs.append(' widget="boolean_toggle"')
        elif field_def.type == 'text' and not is_title:
            attrs.append(' widget="text"')
        elif field_def.type == 'html':
            attrs.append(' widget="html"')
        elif field_def.type in ['date', 'datetime']:
            widget = 'date' if field_def.type == 'date' else 'datetime'
            attrs.append(f' widget="{widget}"')
        elif field_def.type == 'monetary':
            attrs.append(' widget="monetary"')
        elif field_def.type == 'many2one':
            # For Easy Mode, simplify many2one fields and remove complex domains
            attrs.append(' options="{\'no_create\': True, \'no_create_edit\': True}"')
            # Remove any complex domain that might reference unavailable fields
            # This prevents errors like "team_id not defined" in Easy Mode
        elif field_def.type == 'selection' and hasattr(field_def, 'selection'):
            # Keep default selection widget
            pass
        elif field_def.type == 'float':
            attrs.append(' digits="[16,2]"')
        
        # Add required attribute if field is required
        if getattr(field_def, 'required', False):
            attrs.append(' required="1"')
        
        # Add readonly if field is readonly
        if getattr(field_def, 'readonly', False):
            attrs.append(' readonly="1"')
        
        return ''.join(attrs)

    def _create_or_update_view(self, view_name, view_type, arch_content):
        """Create or update a view with the given parameters."""
        existing_view = self.env['ir.ui.view'].search([
            ('name', '=', view_name),
            ('model', '=', self.model)
        ], limit=1)
        
        if existing_view:
            existing_view.write({
                'arch': arch_content,
                'priority': 99  # Start with low priority (disabled)
            })
        else:
            self.env['ir.ui.view'].create({
                'name': view_name,
                'model': self.model,
                'type': view_type,
                'priority': 99,  # Start with low priority (disabled)
                'arch': arch_content
            })
