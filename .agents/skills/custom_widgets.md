# Agent Skill Profile: Odoo 19 Custom OWL Widget Architect

## 1. Skill Overview
* **Role/Domain:** Frontend Framework Engineer specializing in Odoo ERP development.
* **Core Mandate:** Design, develop, and integrate secure, interactive, and high-performance **OWL (Odoo Web Library)** widgets matching Odoo 19 syntax specifications.
* **Security Specialisation:** Implement Client-Side **Role-Based Access Control (RBAC)** aligned tightly with Odoo backend Security Groups (`res.groups`).

## 2. Technical Capabilities & Competencies

### A. Odoo 19 OWL Architecture
* **Component Construction:** Crafting modular UI structures extending Odoo’s native core `Component`.
* **State Management:** Utilizing reactive wrappers like `useState` to manage dynamic data-flows cleanly.
* **Asynchronous Integration:** Hooking into Lifecycle hooks (`onWillStart`, `onWillUpdateProps`) to handle non-blocking asynchronous behaviors seamlessly.
* **Registry Management:** Adding custom fields, views, and clients directly to the Odoo web registries (`registry.category("fields").add()`).

### B. Role-Based Access Control (RBAC) Architecture
* **User Service Consumption:** Consuming `@web/core/user` asynchronously to check user properties and roles.
* **Conditional Frontend Security:** Using `user.hasGroup("module.group_xml_id")` to evaluate permissions dynamically before components render.
* **Adaptive Templating:** Leveraging OWL's structural layout engine (`t-if`, `t-else`) to dynamically hide, present, or disable functional elements according to user permission profiles.
* **Defensive UI Execution:** Implementing logical client-side short-circuits in action handlers to reject illegal execution loops, ensuring a smooth, secure UX.

## 3. Standard Code Implementation Patterns

### Backend XML Security Foundation
Defines the user group constraints needed by the widget:
```xml
<odoo>
    <data noupdate="1">
        <record id="group_widget_advanced_manager" model="res.groups">
            <field name="name">Advanced Widget Manager</field>
            <field name="category_id" ref="base.module_category_hidden"/>
        </record>
    </data>
</odoo>
```

### OWL Component Blueprint (`.js`)
Handles reactive state orchestration, injection of the user service, and asynchronous role checks:
```javascript
/** @odoo-module **/
import { Component, useState, onWillStart } from "@odw/owl";
import { registry } from "@web/core/registry";
import { user } from "@web/core/user";

export class CustomSecureWidget extends Component {
    setup() {
        this.state = useState({
            isManager: false,
            isLoading: true,
        });

        onWillStart(async () => {
            // Asynchronous Odoo 19 group verification
            this.state.isManager = await user.hasGroup("my_custom_module.group_widget_advanced_manager");
            this.state.isLoading = false;
        });
    }

    async handleRestrictedAction() {
        if (!this.state.isManager) return; // Defensive guard clause
        // Execute premium mutations or dashboard processes
    }
}

CustomSecureWidget.template = "my_custom_module.CustomSecureWidgetTemplate";
registry.category("fields").add("secure_dashboard_widget", CustomSecureWidget);
```

### Template Layout Architecture (`.xml`)
Structures the visual experience to adapt perfectly based on the state evaluation:
```xml
<templates xml:space="preserve">
    <t t-name="my_custom_module.CustomSecureWidgetTemplate">
        <div class="secure-widget-container">
            <div class="public-view">
                <h3>General Statistics</h3>
                <p>Welcome back, <t t-esc="props.record.data.display_name"/></p>
            </div>
            
            <t t-if="state.isManager">
                <div class="manager-controls alert alert-info">
                    <h4>Admin Command Center</h4>
                    <button class="btn btn-danger" t-on-click="handleRestrictedAction">
                        Override Safe Margins
                    </button>
                </div>
            </t>
            <t t-else="">
                <div class="text-muted text-small">
                    💡 Contact a system administrator to request write-level execution rights.
                </div>
            </t>
        </div>
    </t>
</templates>
```

## 4. Architectural Rules & Best Practices
1. **Never Rely Solely on UI Hiding:** UI modification (`t-if`) serves as an ergonomic design pattern. You must always enforce strict backend validation (`@api.model` or endpoint group restrictions) to prevent unauthorized API requests.
2. **Mandatory Async Checks:** Never block thread processes with legacy synchronous global permission checks. Always bundle permission mapping into asynchronous triggers like `onWillStart`.
3. **Graceful State Handling:** Use clear fallbacks or loading states (`state.isLoading`) to ensure users do not experience jarring layout flashes while backend security checks finish resolving.
