/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { Component, onWillStart, useState } from "@odoo/owl";

export class AlamiaAiCopilot extends Component {
    static template = "alamia_travel_reporting.AlamiaAiCopilot";
    static props = ["*"];

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.notification = useService("notification");

        this.state = useState({
            loading: true,
            userProfile: null,
            searchQuery: "",
            activeTab: "chat",
            messages: [],
            activeDossier: null, // 'customer', 'booking', 'profitability', 'work_items'
            dossierData: null,
            pendingProposal: null,
            followupForm: {
                res_model: "res.partner",
                res_id: "",
                summary: "",
                note: "",
            },
        });

        onWillStart(async () => {
            await this.loadProfile();
        });
    }

    async loadProfile() {
        try {
            this.state.loading = true;
            const res = await this.orm.call("mcp.mixin", "get_employee_profile", []);
            const payload = res.structuredContent || {};
            this.state.userProfile = payload;
            this.state.loading = false;

            // Welcome message
            this.addSystemMessage(
                `👋 Hello ${payload.user?.name || "Team Member"}! I am your **${payload.role_profile?.name || "Alamia Travels AI Assistant"}**.` +
                ` How can I assist you with Travel OS operations today?`
            );

            // Automatically load daily briefing work items card on startup
            await this.onDailyBriefing();
        } catch (error) {
            console.error("Failed to load Alamia AI profile:", error);
            this.state.loading = false;
            this.notification.add("Could not load Alamia AI profile.", { type: "danger" });
        }
    }

    addSystemMessage(text, payload = null) {
        this.state.messages.push({
            id: Date.now(),
            sender: "ai",
            text: text,
            payload: payload,
            timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        });
    }

    addUserMessage(text) {
        this.state.messages.push({
            id: Date.now(),
            sender: "user",
            text: text,
            timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        });
    }

    async onSendMessage() {
        const query = this.state.searchQuery.trim();
        if (!query) return;

        this.addUserMessage(query);
        this.state.searchQuery = "";

        const lower = query.toLowerCase();

        if (lower.includes("briefing") || lower.includes("work") || lower.includes("attention") || lower.includes("tasks")) {
            await this.onDailyBriefing();
        } else if (lower.includes("ke-") || lower.includes("booking")) {
            await this.onSearchBooking360(query);
        } else if (lower.includes("profit") || lower.includes("margin") || lower.includes("revenue")) {
            await this.onBookingProfitability(query);
        } else {
            await this.onSearchCustomer360(query);
        }
    }

    async onDailyBriefing() {
        try {
            const res = await this.orm.call("mcp.mixin", "get_work_items", [], { urgency: "all" });
            const payload = res.structuredContent || {};
            this.state.activeDossier = "work_items";
            this.state.dossierData = payload;

            const count = payload.total_items || 0;
            this.addSystemMessage(
                `🌅 **Daily Briefing Summary**\nFound **${count} open work items** requiring attention. See the active work queue card below.`,
                payload
            );
        } catch (error) {
            this.notification.add("Failed to retrieve work items: " + error.message, { type: "danger" });
        }
    }

    async onSearchCustomer360(queryName) {
        try {
            const cleanName = queryName.replace(/\b(search|customer|360|show|find|for|dossier)\b/gi, "").trim() || queryName;
            const res = await this.orm.call("mcp.mixin", "get_customer_360", [], { name: cleanName });
            const payload = res.structuredContent || {};

            this.state.activeDossier = "customer";
            this.state.dossierData = payload;

            const cust = payload.customer || {};
            const metrics = payload.metrics || {};
            this.addSystemMessage(
                `👤 **Customer 360 Dossier: ${cust.name}**\n` +
                `• Total Spent: PKR ${(metrics.lifetime_spent || 0).toLocaleString()}\n` +
                `• Active Bookings: ${metrics.active_bookings_count || 0}\n` +
                `• Unpaid Shortfall: PKR ${(metrics.outstanding_unpaid_balance || 0).toLocaleString()}`,
                payload
            );
        } catch (error) {
            this.addSystemMessage(`⚠️ ${error.message || "Customer search yielded no matching records."}`);
        }
    }

    async onSearchBooking360(queryRef) {
        try {
            const match = queryRef.match(/KE-[A-Z0-9-]+/i);
            const ref = match ? match[0] : queryRef.trim();

            const res = await this.orm.call("mcp.mixin", "get_booking_360", [], { name: ref });
            const payload = res.structuredContent || {};

            this.state.activeDossier = "booking";
            this.state.dossierData = payload;

            const b = payload.booking || {};
            const f = payload.financials || {};
            this.addSystemMessage(
                `🕋 **Booking 360 Overview: ${b.name}**\n` +
                `• Customer: ${b.customer_name}\n` +
                `• Total Amount: PKR ${(f.amount_total || 0).toLocaleString()}\n` +
                `• Payment Shortfall: PKR ${(f.payment_shortfall || 0).toLocaleString()}`,
                payload
            );
        } catch (error) {
            this.addSystemMessage(`⚠️ Booking search for "${queryRef}" yielded no matching record. Ensure reference is in format KE-XXXXX.`);
        }
    }

    async onBookingProfitability(queryRef) {
        try {
            const match = queryRef.match(/KE-[A-Z0-9-]+/i);
            const ref = match ? match[0] : queryRef.trim();

            const res = await this.orm.call("mcp.mixin", "get_booking_profitability", [], { name: ref });
            const payload = res.structuredContent || {};

            this.state.activeDossier = "profitability";
            this.state.dossierData = payload;

            const p = payload.profitability || {};
            this.addSystemMessage(
                `📊 **Booking Profitability: ${payload.booking?.name || ref}**\n` +
                `• Revenue: PKR ${(p.revenue || 0).toLocaleString()}\n` +
                `• Total Cost: PKR ${(p.total_supplier_cost || 0).toLocaleString()}\n` +
                `• Gross Profit: PKR ${(p.gross_profit || 0).toLocaleString()} (**${p.margin_percentage}% margin**)`,
                payload
            );
        } catch (error) {
            this.addSystemMessage(`⚠️ Profitability calculation for "${queryRef}" failed. Specify a valid booking sequence e.g. KE-2026-00001.`);
        }
    }

    onSelectWorkItem(item) {
        this.state.followupForm.res_model = item.res_model || "res.partner";
        this.state.followupForm.res_id = item.res_id || "";
        this.state.followupForm.summary = `Follow-up on ${item.summary || "Task"}`;
        this.notification.add(`Selected item ${item.id}. Form populated below.`, { type: "info" });
    }

    async onProposeFollowup() {
        const f = this.state.followupForm;
        if (!f.res_id || !f.summary) {
            this.notification.add("Please provide Target ID and Summary for the follow-up.", { type: "warning" });
            return;
        }

        try {
            const res = await this.orm.call("mcp.mixin", "propose_action", [], {
                action_type: "create_followup",
                target: { model: f.res_model, id: parseInt(f.res_id) },
                reason: f.summary,
                proposed_changes: { note: f.note },
                idempotency_key: `IDEMP-UI-${Date.now()}`,
            });

            const proposal = res.structuredContent || {};
            this.state.pendingProposal = proposal;

            this.addSystemMessage(
                `⚡ **Action Proposal Generated: ${proposal.action_id}**\n` +
                `• Action Type: ${proposal.action_type}\n` +
                `• Target: ${proposal.target?.model}, ID ${proposal.target?.id}\n` +
                `• Reason: ${proposal.reason}\n` +
                `Please review and confirm execution below.`,
                proposal
            );
        } catch (error) {
            this.notification.add("Action proposal failed: " + error.message, { type: "danger" });
        }
    }

    async onConfirmProposal() {
        const prop = this.state.pendingProposal;
        if (!prop) return;

        try {
            const f = this.state.followupForm;
            const res = await this.orm.call("mcp.mixin", "create_followup", [], {
                res_model: prop.target?.model || f.res_model,
                res_id: prop.target?.id || parseInt(f.res_id),
                summary: prop.reason || f.summary,
                note: f.note,
                idempotency_key: prop.idempotency_key,
            });

            this.state.pendingProposal = null;
            this.notification.add("Action executed & chatter audit trail created!", { type: "success" });
            this.addSystemMessage(`✅ **Action Executed Successfully!** Activity created and logged to chatter audit trail.`);
        } catch (error) {
            this.notification.add("Execution failed: " + error.message, { type: "danger" });
        }
    }

    onRejectProposal() {
        this.state.pendingProposal = null;
        this.addSystemMessage("❌ Action proposal rejected by user.");
    }
}

registry.category("actions").add("alamia_ai_copilot_client_action", AlamiaAiCopilot);
