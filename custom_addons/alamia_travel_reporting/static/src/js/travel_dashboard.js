/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { Component, onWillStart, useState } from "@odoo/owl";

export class TravelDashboard extends Component {
    static template = "alamia_travel_reporting.TravelDashboard";
    static props = ["*"];

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.role = (this.props.action && this.props.action.context && this.props.action.context.dashboard_role) || null;

        this.state = useState({
            loading: true,
            data: {
                role: this.role || "ceo",
                currency_symbol: "Rs",
                user_name: "",
                kpis: {
                    today_sales: 0,
                    today_sales_count: 0,
                    today_collections: 0,
                    monthly_sales: 0,
                    monthly_sales_count: 0,
                    monthly_gross_profit: 0,
                    total_receivables: 0,
                    total_payables: 0,
                    cash_position: 0,
                    bank_position: 0,
                    my_today_sales: 0,
                    my_month_sales: 0,
                    pending_transactions_count: 0,
                },
                sales_by_service: [],
                sales_by_staff: [],
                outstanding_customers: [],
                supplier_payables: [],
                top_customers: [],
                recent_sales: [],
                workload: {},
            },
        });

        onWillStart(async () => {
            await this.loadDashboardData();
        });
    }

    async loadDashboardData() {
        this.state.loading = true;
        try {
            const kwargs = {};
            if (this.role) {
                kwargs.role = this.role;
            }
            const data = await this.orm.call("travel.dashboard", "get_dashboard_data", [], kwargs);
            if (data) {
                this.state.data = data;
            }
        } catch (error) {
            console.error("Error loading Travel Dashboard data:", error);
        } finally {
            this.state.loading = false;
        }
    }

    formatCurrency(amount) {
        if (amount === undefined || amount === null) return "0";
        return Number(amount).toLocaleString(undefined, {
            minimumFractionDigits: 0,
            maximumFractionDigits: 0,
        });
    }

    openSales(domain, name) {
        this.action.doAction({
            type: "ir.actions.act_window",
            name: name || "Travel Sales",
            res_model: "travel.sale",
            views: [[false, "list"], [false, "form"]],
            domain: domain || [],
        });
    }

    openInvoices(domain, name) {
        this.action.doAction({
            type: "ir.actions.act_window",
            name: name || "Customer Invoices",
            res_model: "account.move",
            views: [[false, "list"], [false, "form"]],
            domain: domain || [],
            context: { default_move_type: "out_invoice" },
        });
    }

    openBills(domain, name) {
        this.action.doAction({
            type: "ir.actions.act_window",
            name: name || "Vendor Bills",
            res_model: "account.move",
            views: [[false, "list"], [false, "form"]],
            domain: domain || [],
            context: { default_move_type: "in_invoice" },
        });
    }

    openSale(saleId) {
        this.action.doAction({
            type: "ir.actions.act_window",
            name: "Travel Sale",
            res_model: "travel.sale",
            res_id: saleId,
            views: [[false, "form"]],
        });
    }

    get roleTitle() {
        switch (this.state.data.role) {
            case "ceo": return "CEO Executive Dashboard";
            case "operations": return "Operations Director Dashboard";
            case "sales": return "Sales & Customer Relations Dashboard";
            case "ops_marketing": return "Operations & Marketing Dashboard";
            default: return "Travel OS Dashboard";
        }
    }
}

registry.category("actions").add("travel_dashboard_client_action", TravelDashboard);
