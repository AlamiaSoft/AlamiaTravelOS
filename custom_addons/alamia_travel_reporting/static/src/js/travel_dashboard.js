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
        this.notification = useService("notification");
        this.role = (this.props.action && this.props.action.context && this.props.action.context.dashboard_role) || null;

        this.state = useState({
            loading: true,
            activeTab: "today",
            activeModal: null, // 'complete', 'reschedule', 'reassign'
            selectedActivity: null,
            completeForm: {
                outcome: "Successful",
                feedback: "",
                scheduleNext: false,
                nextTypeId: "",
                nextDeadline: "",
                nextSummary: "",
            },
            rescheduleForm: {
                newDate: new Date().toISOString().split("T")[0],
            },
            reassignForm: {
                newUserId: "",
                newDate: "",
            },
            data: {
                role: this.role || "ceo",
                currency_symbol: "Rs",
                user_name: "",
                my_activities: {
                    overdue: [],
                    today: [],
                    upcoming: [],
                    overdue_count: 0,
                    today_count: 0,
                    upcoming_count: 0,
                },
                unassigned_activities: [],
                activity_types: [],
                team_workload: [],
                attention_items: {},
                kpis: {},
                sales_by_service: [],
                sales_by_staff: [],
                outstanding_customers: [],
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

    openRecord(resModel, resId) {
        if (!resModel || !resId) return;
        this.action.doAction({
            type: "ir.actions.act_window",
            res_model: resModel,
            res_id: resId,
            views: [[false, "form"]],
        });
    }

    openScheduleTaskWizard() {
        this.action.doAction("alamia_travel_core.action_travel_schedule_activity_wizard", {
            onClose: () => this.loadDashboardData(),
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

    openExpenses(domain, name) {
        this.action.doAction({
            type: "ir.actions.act_window",
            name: name || "Office Expenses",
            res_model: "travel.expense",
            views: [[false, "list"], [false, "form"]],
            domain: domain || [],
        });
    }

    openActivities(domain, name) {
        this.action.doAction({
            type: "ir.actions.act_window",
            name: name || "Activities",
            res_model: "mail.activity",
            views: [[false, "list"], [false, "form"]],
            domain: domain || [],
        });
    }

    // Modal & Activity Actions
    openCompleteModal(activity) {
        this.state.selectedActivity = activity;
        this.state.completeForm = {
            outcome: "Successful",
            feedback: "",
            scheduleNext: false,
            nextTypeId: this.state.data.activity_types.length ? this.state.data.activity_types[0].id : "",
            nextDeadline: new Date(Date.now() + 86400000 * 2).toISOString().split("T")[0],
            nextSummary: "",
        };
        this.state.activeModal = "complete";
    }

    async submitCompleteActivity() {
        if (!this.state.selectedActivity) return;
        try {
            const nextAct = this.state.completeForm.scheduleNext ? {
                activity_type_id: this.state.completeForm.nextTypeId,
                date_deadline: this.state.completeForm.nextDeadline,
                summary: this.state.completeForm.nextSummary,
            } : null;

            await this.orm.call("travel.dashboard", "action_complete_activity", [], {
                activity_id: this.state.selectedActivity.id,
                outcome: this.state.completeForm.outcome,
                feedback: this.state.completeForm.feedback,
                next_activity: nextAct,
            });

            this.notification.add("Activity marked completed!", { type: "success" });
            this.closeModal();
            await this.loadDashboardData();
        } catch (error) {
            console.error("Error completing activity:", error);
        }
    }

    openRescheduleModal(activity) {
        this.state.selectedActivity = activity;
        this.state.rescheduleForm.newDate = new Date(Date.now() + 86400000).toISOString().split("T")[0];
        this.state.activeModal = "reschedule";
    }

    async submitRescheduleActivity() {
        if (!this.state.selectedActivity || !this.state.rescheduleForm.newDate) return;
        try {
            await this.orm.call("travel.dashboard", "action_reschedule_activity", [], {
                activity_id: this.state.selectedActivity.id,
                new_date: this.state.rescheduleForm.newDate,
            });

            this.notification.add("Activity rescheduled!", { type: "info" });
            this.closeModal();
            await this.loadDashboardData();
        } catch (error) {
            console.error("Error rescheduling activity:", error);
        }
    }

    openReassignModal(activity) {
        this.state.selectedActivity = activity;
        this.state.reassignForm = {
            newUserId: this.state.data.team_workload.length ? this.state.data.team_workload[0].user_id : "",
            newDate: activity.date_deadline,
        };
        this.state.activeModal = "reassign";
    }

    async submitReassignActivity() {
        if (!this.state.selectedActivity || !this.state.reassignForm.newUserId) return;
        try {
            await this.orm.call("travel.dashboard", "action_reassign_activity", [], {
                activity_id: this.state.selectedActivity.id,
                new_user_id: this.state.reassignForm.newUserId,
                new_date: this.state.reassignForm.newDate,
            });

            this.notification.add("Activity reassigned!", { type: "success" });
            this.closeModal();
            await this.loadDashboardData();
        } catch (error) {
            console.error("Error reassigning activity:", error);
        }
    }

    closeModal() {
        this.state.activeModal = null;
        this.state.selectedActivity = null;
    }

    get roleTitle() {
        switch (this.state.data.role) {
            case "ceo": return "CEO Executive Dashboard";
            case "operations": return "Operations Director Dashboard";
            case "sales": return "Sales & Customer Relations Dashboard";
            case "ops_marketing": return "Operations & Marketing Dashboard";
            default: return "Travel OS Productivity Cockpit";
        }
    }
}

registry.category("actions").add("travel_dashboard_client_action", TravelDashboard);
