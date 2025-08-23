/** @odoo-module **/

import { registry } from "@web/core/registry";
import { _t } from "@web/core/l10n/translation";
import { Component, xml } from "@odoo/owl";

// Simple console log to verify loading
console.log("Universal Easy Mode: Module loading started");

/**
 * Easy Mode Toggle Systray Component
 */
class EasyModeToggle extends Component {
    static template = xml`
        <div class="o_systray_easy_mode_toggle">
            <button class="btn btn-sm" 
                    t-att-class="getButtonClass()"
                    t-on-click="onToggleClick"
                    title="Toggle Easy Mode">
                <i class="fa fa-magic" role="img" aria-label="Easy Mode"/>
                <span class="d-none d-sm-inline ms-1" t-esc="getButtonText()"/>
            </button>
        </div>
    `;

    setup() {
        super.setup();
        // Initialize state and load from backend
        this.easyModeEnabled = localStorage.getItem('easy_mode_enabled') === 'true';
        console.log("Universal Easy Mode: Initial state from localStorage:", this.easyModeEnabled ? 'ON' : 'OFF');
        
        // Check backend status on load
        this.checkBackendStatus();
    }
    
    async checkBackendStatus() {
        try {
            const result = await this.env.services.rpc("/web/dataset/call_kw", {
                model: 'ir.ui.view',
                method: 'get_easy_mode_status',
                args: [],
                kwargs: {}
            });
            
            if (result && typeof result.enabled === 'boolean') {
                this.easyModeEnabled = result.enabled;
                localStorage.setItem('easy_mode_enabled', this.easyModeEnabled.toString());
                console.log("Universal Easy Mode: Status from backend:", this.easyModeEnabled ? 'ON' : 'OFF');
                this.render();
            }
        } catch (error) {
            console.warn("Universal Easy Mode: Could not check backend status:", error);
            // Keep localStorage state as fallback
        }
    }

    getButtonClass() {
        return this.easyModeEnabled 
            ? "btn-success" 
            : "btn-outline-primary";
    }

    getButtonText() {
        return this.easyModeEnabled ? "Easy Mode ON" : "Easy Mode OFF";
    }

    async onToggleClick() {
        console.log("Universal Easy Mode: Toggle clicked - current state:", this.easyModeEnabled ? 'ON' : 'OFF');
        
        const notification = this.env.services.notification;
        
        try {
            // Toggle the state
            this.easyModeEnabled = !this.easyModeEnabled;
            
            // Save state to localStorage
            localStorage.setItem('easy_mode_enabled', this.easyModeEnabled.toString());
            
            // Call the backend to switch view priorities
            const result = await this.env.services.rpc("/web/dataset/call_kw", {
                model: 'ir.ui.view',
                method: 'toggle_easy_mode_views',
                args: [this.easyModeEnabled],
                kwargs: {}
            });
            
            // Show appropriate notification
            const message = this.easyModeEnabled 
                ? _t("Easy Mode Activated - Interface simplified") 
                : _t("Easy Mode Deactivated - Full interface restored");
                
            notification.add(message, { 
                type: "success",
                title: this.easyModeEnabled ? "🟢 Easy Mode ON" : "🔴 Easy Mode OFF"
            });
            
            // Force re-render of button
            this.render();
            
            // Reload current view to show changes
            if (this.env.services.action && this.env.services.action.doAction) {
                // Refresh current view
                window.location.reload();
            }
            
        } catch (error) {
            console.error("Universal Easy Mode: Error in toggle:", error);
            
            // Revert state on error
            this.easyModeEnabled = !this.easyModeEnabled;
            localStorage.setItem('easy_mode_enabled', this.easyModeEnabled.toString());
            
            notification.add(_t("Error switching Easy Mode - please try again"), { 
                type: "danger",
                title: "Easy Mode Error"
            });
        }
    }
}

// Register the systray component with comprehensive error handling
try {
    console.log("Universal Easy Mode: Attempting to register systray component");
    
    registry.category("systray").add("universal_easy_mode.EasyModeToggle", {
        Component: EasyModeToggle,
    }, { sequence: 1 });
    
    console.log("Universal Easy Mode: Systray component registered successfully");
    
} catch (error) {
    console.error("Universal Easy Mode: Failed to register systray component:", error);
}

console.log("Universal Easy Mode: Module loading completed");
