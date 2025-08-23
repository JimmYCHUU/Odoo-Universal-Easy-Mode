# Universal Easy Mode Module

A comprehensive Odoo 17 module that provides simplified interfaces ("Easy Mode") for complex models, making Odoo more accessible to end users by hiding advanced complexity while maintaining full functionality.

## 🎯 What This Module Does

The Universal Easy Mode module transforms complex Odoo forms into simplified, user-friendly interfaces by:

1. **Automatically detecting** all installed modules and their models
2. **Generating simplified views** that show only essential fields
3. **Providing a toggle mechanism** to switch between Easy Mode and Full Mode
4. **Maintaining full CRUD operations** while hiding complexity
5. **Respecting security permissions** and access rights
6. **Storing optimized views** in the database for performance

## 🔧 Core Functionality Overview

### 1. Module and Model Detection System
- **Automatic Discovery**: Scans all installed modules and detects their models
- **Smart Filtering**: Excludes system models and focuses on business-relevant models
- **Model Analysis**: Analyzes field types, relationships, and complexity
- **Dynamic Configuration**: Allows admins to enable/disable Easy Mode per model

### 2. Simplified View Generation
- **Field Categorization**: Automatically categorizes fields as "basic" or "advanced"
- **View Creation**: Generates simplified form and tree views dynamically
- **Inheritance System**: Uses Odoo's view inheritance for clean integration
- **Priority Management**: Controls which views are shown to users

### 3. Real-Time Mode Switching
- **Toggle Functionality**: Switch between Easy Mode and Full Mode instantly
- **State Persistence**: Remembers user preferences per model
- **Seamless Transition**: No data loss during mode switching
- **UI Integration**: Toggle buttons integrated into standard Odoo interface

## 🚀 Detailed Feature Breakdown

### 📋 Configuration Management (`easy.mode.config`)
**Primary Configuration Interface**
- **Module Selection**: Choose which installed modules to enable Easy Mode for
- **Automatic Model Detection**: Scans selected modules and identifies all models
- **Bulk Operations**: Enable/disable Easy Mode for multiple models at once
- **Refresh Functionality**: Re-scan modules when new models are added
- **Statistics Tracking**: Monitor how many views have been generated

**Key Methods:**
- `action_refresh_models()`: Detects new models from selected modules
- `action_generate_easy_views()`: Creates simplified views for all configured models
- `action_cleanup_views()`: Removes generated Easy Mode views

### 🎛️ Model-Specific Configuration (`easy.mode.model.config`)
**Per-Model Settings**
- **Individual Model Control**: Enable/disable Easy Mode per model
- **Field Analysis**: Automatic categorization of fields as basic/advanced
- **View Generation Status**: Track which views have been created
- **Usage Statistics**: Monitor Easy Mode adoption per model

**Automatic Field Categorization Logic:**
- **Basic Fields**: `name`, `description`, `active`, `date`, `email`, `phone`
- **Advanced Fields**: `create_date`, `write_date`, `__last_update`, computed fields
- **Relationship Fields**: Handled intelligently based on complexity

### 🔄 Field Override System (`easy.mode.field.override`)
**Granular Field Control**
- **Field-Level Customization**: Override automatic categorization
- **Widget Selection**: Choose specific widgets for fields in Easy Mode
- **Visibility Control**: Show/hide fields regardless of automatic categorization
- **Validation Rules**: Set specific validation for Easy Mode fields

### 🔀 Real-Time Toggle System (`easy.mode.toggler`)
**Seamless Mode Switching**
- **Instant Toggle**: Switch between modes without page reload
- **State Management**: Remember user preferences
- **Priority Control**: Dynamically adjust view priorities
- **Context Awareness**: Works with any model that has Easy Mode enabled

**Toggle Methods:**
- `toggle_easy_mode(model_name)`: Main toggle functionality
- `is_easy_mode_available(model_name)`: Check if Easy Mode exists for model
- `get_current_mode(model_name)`: Determine current active mode

### 🛡️ Validation System (`easy.mode.validator`)
**Data Integrity and Security**
- **Permission Validation**: Ensures users have proper access rights
- **Data Consistency**: Validates that Easy Mode operations don't break data
- **Security Checks**: Prevents unauthorized access to advanced features
- **Error Handling**: Graceful handling of validation failures

### 📊 View Management System (`easy.mode.view.manager`)
**Dynamic View Creation and Management**
- **XML Generation**: Creates clean, optimized view XML
- **Inheritance Handling**: Proper use of Odoo's view inheritance system
- **Priority Management**: Controls which views are active
- **Cleanup Operations**: Removes orphaned or outdated views

## 🎨 How the Complete System Works

### 1. **Initial Setup Workflow**
```
Admin Access → Settings → Easy Mode Configuration
     ↓
Select Modules → Automatic Model Detection
     ↓
Field Analysis → Easy Mode View Generation
     ↓
Deploy to Users → Toggle Functionality Available
```

### 2. **Runtime Operation Flow**
```
User Opens Model → System Checks Easy Mode Availability
     ↓
Load Appropriate View (Easy/Full) → Display Toggle Button
     ↓
User Clicks Toggle → Priority Switch → View Refresh
     ↓
New Mode Active → State Persisted → User Continues
```

### 3. **View Generation Process**
```
Model Analysis → Field Categorization → XML Template Creation
     ↓
Inheritance Setup → Priority Assignment → Database Storage
     ↓
View Registration → Activation → User Interface Update
```

## 🔧 Technical Implementation Details

### Database Models Architecture

#### 1. `easy.mode.config` - Main Configuration
```python
class EasyModeConfig(models.Model):
    _name = 'easy.mode.config'
    _description = 'Easy Mode Configuration'
    
    # Core fields
    name = fields.Char('Configuration Name', required=True)
    active = fields.Boolean('Active', default=True)
    enabled_module_ids = fields.Many2many('ir.module.module')
    enabled_model_ids = fields.One2many('easy.mode.model.config')
    last_refresh = fields.Datetime('Last Refresh', readonly=True)
    view_count = fields.Integer('Generated Views Count', compute='_compute_view_count')
```

#### 2. `easy.mode.model.config` - Per-Model Settings
```python
class EasyModeModelConfig(models.Model):
    _name = 'easy.mode.model.config'
    _description = 'Easy Mode Model Configuration'
    
    # Model identification
    model = fields.Char('Model Name', required=True)
    is_enabled = fields.Boolean('Enable Easy Mode', default=True)
    basic_fields = fields.Text('Basic Fields (JSON)')
    advanced_fields = fields.Text('Advanced Fields (JSON)')
    view_priority = fields.Integer('View Priority', default=1)
```

#### 3. `easy.mode.field.override` - Field-Level Control
```python
class EasyModeFieldOverride(models.Model):
    _name = 'easy.mode.field.override'
    _description = 'Easy Mode Field Override'
    
    # Field configuration
    model_name = fields.Char('Model Name', required=True)
    field_name = fields.Char('Field Name', required=True)
    is_basic = fields.Boolean('Is Basic Field', default=True)
    widget = fields.Char('Widget Type')
    is_visible = fields.Boolean('Visible in Easy Mode', default=True)
```

#### 4. `easy.mode.toggler` - Runtime Toggle System
```python
class EasyModeToggler(models.TransientModel):
    _name = 'easy.mode.toggler'
    _description = 'Easy Mode Toggle Helper'
    
    # Main toggle method
    def toggle_easy_mode(self, model_name=None):
        # Switches view priorities dynamically
        # Returns client action for UI refresh
```

### View Generation Algorithm

#### Field Categorization Logic
```python
def categorize_fields(self, model_obj):
    """Automatically categorize fields as basic or advanced."""
    basic_patterns = [
        'name', 'title', 'description', 'notes', 'email', 'phone',
        'mobile', 'website', 'street', 'city', 'country_id', 'state_id',
        'zip', 'active', 'date', 'deadline', 'priority', 'stage_id',
        'user_id', 'partner_id', 'company_id', 'currency_id'
    ]
    
    advanced_patterns = [
        'create_date', 'write_date', '__last_update', 'create_uid',
        'write_uid', 'sequence', 'message_ids', 'activity_ids',
        'message_follower_ids', 'access_token'
    ]
    
    # Field analysis and categorization
    for field_name, field_obj in model_obj._fields.items():
        if field_name in basic_patterns:
            category = 'basic'
        elif field_name in advanced_patterns:
            category = 'advanced'
        elif field_obj.compute:
            category = 'advanced'  # Computed fields are advanced
        elif field_obj.related:
            category = 'advanced'  # Related fields are advanced
        else:
            category = 'basic'     # Default to basic
```

#### XML View Generation
```python
def generate_easy_view_xml(self, model_name, fields_data):
    """Generate simplified view XML."""
    form_template = '''
    <form string="Easy Mode">
        <sheet>
            <group>
                %s
            </group>
        </sheet>
    </form>
    '''
    
    tree_template = '''
    <tree string="Easy Mode">
        %s
    </tree>
    '''
    
    # Generate field elements based on categorization
    form_fields = []
    tree_fields = []
    
    for field_name, field_data in fields_data.items():
        if field_data['category'] == 'basic':
            form_fields.append(f'<field name="{field_name}"/>')
            tree_fields.append(f'<field name="{field_name}"/>')
    
    return {
        'form': form_template % '\n'.join(form_fields),
        'tree': tree_template % '\n'.join(tree_fields)
    }
```

### Security and Access Control

#### Group-Based Permissions
```xml
<!-- Security Groups -->
<record id="group_easy_mode_user" model="res.groups">
    <field name="name">Easy Mode User</field>
    <field name="category_id" ref="base.module_category_tools"/>
</record>

<record id="group_easy_mode_admin" model="res.groups">
    <field name="name">Easy Mode Admin</field>
    <field name="category_id" ref="base.module_category_tools"/>
    <field name="implied_ids" eval="[(4, ref('group_easy_mode_user'))]"/>
</record>
```

#### Access Rights Matrix
```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_easy_mode_config_admin,easy.mode.config.admin,model_easy_mode_config,group_easy_mode_admin,1,1,1,1
access_easy_mode_config_user,easy.mode.config.user,model_easy_mode_config,group_easy_mode_user,1,0,0,0
access_easy_mode_field_override_admin,easy.mode.field.override.admin,model_easy_mode_field_override,group_easy_mode_admin,1,1,1,1
```

## 📱 User Interface Components

### Configuration Interface
**Location**: `Settings → Easy Mode → Configuration`

#### Main Configuration Screen
- **Module Selection Grid**: Visual grid of all installed modules with checkboxes
- **Quick Actions**: Bulk enable/disable, refresh models, generate views
- **Statistics Dashboard**: View counts, enabled models, last refresh dates
- **Model List View**: Detailed view of all configured models with status

#### Model Configuration Forms
- **Model Information**: Display model name, description, module source
- **Field Analysis**: Show categorized fields with basic/advanced labels
- **View Generation Status**: Track which views exist and their priorities
- **Override Controls**: Create field-level overrides for specific needs

### Runtime User Interface
**Integration**: Seamlessly integrated into standard Odoo interface

#### Toggle Button Placement
- **Systray Integration**: Easy Mode toggle in the top navigation bar
- **Form View Integration**: Toggle button in form view headers
- **List View Integration**: Toggle option in list view controls
- **Context-Aware**: Only shows when Easy Mode is available for current model

#### Visual Indicators
- **Mode Status**: Clear indication of current mode (Easy/Full)
- **Field Highlighting**: Visual distinction between basic and advanced fields
- **Simplified Labels**: More user-friendly field labels in Easy Mode
- **Guided Workflows**: Progressive disclosure of advanced features

### Administrative Tools
**Location**: `Settings → Easy Mode → Administration`

#### View Management Dashboard
- **Generated Views List**: All Easy Mode views with management options
- **Performance Metrics**: Usage statistics and performance data
- **Cleanup Tools**: Remove unused or outdated Easy Mode views
- **Bulk Operations**: Mass enable/disable across multiple models

## 🔄 Workflow Examples

### Example 1: Setting Up Easy Mode for Sales
```
1. Administrator Setup:
   Settings → Easy Mode → Configuration
   → Select "Sales" module
   → Click "Refresh Models"
   → Enable Easy Mode for "sale.order" model
   → Generate views

2. Field Categorization (Automatic):
   Basic Fields: customer_name, order_date, amount_total, state
   Advanced Fields: create_date, sequence, access_token, message_ids

3. User Experience:
   Sales → Orders → Toggle to Easy Mode
   → Simplified form with only essential fields
   → Toggle to Full Mode when advanced features needed
```

### Example 2: Custom Model Integration
```
1. Developer creates custom model "project.task.custom"
2. Administrator:
   → Adds custom module to Easy Mode
   → Refreshes model detection
   → Reviews auto-categorized fields
   → Creates field overrides if needed
   → Generates Easy Mode views

3. End Users:
   → Access simplified interface automatically
   → Toggle between modes as needed
   → Full functionality preserved in both modes
```

### Example 3: Troubleshooting Workflow
```
1. Issue: Easy Mode button not appearing
   → Check: User has group_easy_mode_user access
   → Check: Model has Easy Mode enabled
   → Check: Easy Mode views were generated successfully

2. Issue: Wrong fields in Easy Mode
   → Access: Easy Mode → Field Overrides
   → Create: Specific field override for the model
   → Configure: Field visibility and categorization
   → Test: Toggle to verify changes
```

## 🚀 Installation and Setup Guide

### Prerequisites
- Odoo 17.0 or higher
- PostgreSQL database
- Administrator access to Odoo instance

### Step-by-Step Installation
1. **Module Installation**
   ```bash
   # Copy module to addons directory
   cp -r universal_easy_mode /path/to/odoo/addons/
   
   # Update module list
   odoo-bin -d your_database -u base --stop-after-init
   
   # Install module
   Apps → Search "Universal Easy Mode" → Install
   ```

2. **Initial Configuration**
   ```
   Settings → Easy Mode → Configuration
   → Create new configuration
   → Name: "Production Easy Mode"
   → Select modules to enable
   → Click "Refresh Models"
   → Review detected models
   → Click "Generate Easy Views"
   ```

3. **User Access Setup**
   ```
   Settings → Users & Companies → Users
   → Select users who need Easy Mode
   → Add to "Easy Mode User" group
   → Save changes
   ```

4. **Testing and Validation**
   ```
   → Navigate to enabled model (e.g., Contacts)
   → Verify toggle button appears
   → Test switching between modes
   → Verify field visibility changes
   → Test all CRUD operations in both modes
   ```

### Advanced Configuration Options

#### Custom Field Categorization
```python
# Create field override
Settings → Easy Mode → Field Overrides → Create
Model: res.partner
Field: customer_rank
Category: Basic (instead of default Advanced)
Widget: priority
Visible: True
```

#### Performance Optimization
```python
# View priority settings
Easy Mode Views: Priority 1 (shown by default)
Standard Views: Priority 16 (hidden by default)
Full Mode Views: Priority 99 (shown when toggled)
```

#### Bulk Operations
```python
# Enable Easy Mode for multiple models
Configuration → Select Models → Bulk Actions
→ Enable Easy Mode
→ Generate Views
→ Activate for Users
```

## ⚠️ Known Limitations and Considerations

### Current Limitations
1. **Visual Editor Status**: The drag-and-drop visual editor has been temporarily disabled due to browser compatibility issues with the clipboard API in Docker environments
2. **Manual Configuration**: Currently requires manual field categorization through the configuration interface
3. **Static View Generation**: Views are generated once and require regeneration for model changes
4. **Limited Widget Support**: Some advanced widgets may not work properly in Easy Mode

### Browser Compatibility
- **Supported**: Chrome 90+, Firefox 88+, Safari 14+, Edge 90+
- **Clipboard Features**: Disabled in current version due to Docker compatibility
- **JavaScript**: Basic functionality only, advanced features temporarily disabled

### Performance Considerations
- **View Storage**: Easy Mode views are stored in database, minimal performance impact
- **Memory Usage**: Additional views increase memory usage slightly
- **Loading Time**: Negligible impact on page load times
- **Database Size**: Small increase due to additional view records

### Security Considerations
- **Access Control**: Respects existing Odoo security groups and permissions
- **Data Integrity**: No risk to existing data, only affects view layer
- **User Permissions**: Users can only access what they normally have access to
- **Admin Controls**: Full administrative control over Easy Mode features

## 🔧 Troubleshooting Guide

### Common Issues and Solutions

#### 1. Toggle Button Not Visible
**Problem**: Easy Mode toggle button doesn't appear
**Solutions**:
- Check user is in "Easy Mode User" group
- Verify model has Easy Mode enabled in configuration
- Ensure Easy Mode views were generated successfully
- Check browser console for JavaScript errors

#### 2. Fields Not Categorized Correctly
**Problem**: Wrong fields showing in Easy Mode
**Solutions**:
- Go to Easy Mode → Field Overrides
- Create manual override for specific fields
- Regenerate views after making changes
- Clear browser cache and refresh

#### 3. Views Not Generating
**Problem**: Easy Mode views don't get created
**Solutions**:
- Check user has admin permissions
- Verify selected modules are properly installed
- Check Odoo logs for error messages
- Try manual refresh of model detection

#### 4. Performance Issues
**Problem**: Slow loading or high memory usage
**Solutions**:
- Limit number of enabled models
- Use field overrides to reduce complexity
- Monitor database size and cleanup old views
- Check for orphaned view records

### Debug Mode
Enable debug mode for additional troubleshooting:
```python
# In Odoo
Settings → Activate Developer Mode
# Then access Easy Mode → Debug Information
```

### Log Analysis
Check Odoo logs for Easy Mode related messages:
```bash
# Docker environment
docker logs <odoo_container> | grep -i "easy.mode"

# Standard installation
tail -f /var/log/odoo/odoo.log | grep -i "easy.mode"
```

## 📊 Usage Statistics and Monitoring

### Built-in Analytics
- **View Generation Count**: Track how many Easy Mode views have been created
- **Model Usage**: Monitor which models are using Easy Mode most
- **User Adoption**: See how many users are utilizing Easy Mode features
- **Performance Metrics**: Basic performance tracking for view loading

### Custom Reporting
Access detailed usage through:
```
Settings → Easy Mode → Reports
→ View Usage Statistics
→ Model Adoption Rates
→ User Activity Summary
```

## 🚀 Future Roadmap

### Planned Enhancements
1. **Visual Editor Restoration**: Fix clipboard API compatibility and restore drag-and-drop functionality
2. **Smart Field Detection**: AI-powered field categorization based on usage patterns
3. **Template System**: Pre-built Easy Mode templates for common use cases
4. **Mobile Optimization**: Enhanced mobile interface for Easy Mode
5. **API Integration**: REST API for external Easy Mode management

### Community Contributions
We welcome contributions in the following areas:
- Bug fixes and compatibility improvements
- New field categorization algorithms
- Performance optimizations
- Documentation improvements
- Translation updates

## � Support and Community

### Getting Help
- **Documentation**: Complete documentation in module wiki
- **Community Forum**: Active discussion in Odoo community forums
- **Issue Tracking**: GitHub issues for bug reports and feature requests
- **Professional Support**: Available through certified Odoo partners

### Contributing
1. Fork the repository
2. Create a feature branch
3. Implement your changes
4. Add comprehensive tests
5. Update documentation
6. Submit a pull request

### License
This module is licensed under LGPL-3. See LICENSE file for complete terms.

---

## 📋 Quick Reference

### Key Commands
```bash
# Install module
Apps → Search "Universal Easy Mode" → Install

# Configure
Settings → Easy Mode → Configuration

# Enable for model
Configuration → Select Modules → Refresh Models → Generate Views

# User access
Settings → Users → Add to "Easy Mode User" group

# Toggle mode
Click toggle button in any enabled model view
```

### Important Files
```
universal_easy_mode/
├── models/
│   ├── easy_mode_config.py          # Main configuration
│   ├── easy_mode_field_override.py  # Field customization
│   └── easy_mode_toggler.py         # Toggle functionality
├── views/
│   ├── easy_mode_config_views.xml   # Configuration interface
│   └── easy_mode_menus.xml          # Menu structure
└── security/
    └── ir.model.access.csv          # Access rights
```

### Support Contact
- **Technical Issues**: Open GitHub issue with detailed description
- **Feature Requests**: Use GitHub discussions for new ideas
- **Security Issues**: Contact maintainers directly via email

**Made with ❤️ for the Odoo Community - Simplifying Complex Workflows Since 2024**