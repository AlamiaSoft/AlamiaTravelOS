# -*- coding: utf-8 -*-
from odoo import fields, models, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # CEO Dashboard Widgets
    dashboard_show_attention_ceo = fields.Boolean(
        string="CEO: Show Attention & Exception Cards",
        default=True,
        config_parameter="alamia_travel.dashboard_show_attention_ceo"
    )
    dashboard_show_quick_actions_ceo = fields.Boolean(
        string="CEO: Show Quick Action Shortcuts",
        default=True,
        config_parameter="alamia_travel.dashboard_show_quick_actions_ceo"
    )
    dashboard_show_team_workload_ceo = fields.Boolean(
        string="CEO: Show Team Workload Matrix",
        default=True,
        config_parameter="alamia_travel.dashboard_show_team_workload_ceo"
    )
    dashboard_show_sales_by_service_ceo = fields.Boolean(
        string="CEO: Show Sales by Service",
        default=True,
        config_parameter="alamia_travel.dashboard_show_sales_by_service_ceo"
    )
    dashboard_show_sales_by_staff_ceo = fields.Boolean(
        string="CEO: Show Salesperson Performance",
        default=True,
        config_parameter="alamia_travel.dashboard_show_sales_by_staff_ceo"
    )

    # Operations Director Widgets
    dashboard_show_attention_operations = fields.Boolean(
        string="Operations: Show Attention & Exception Cards",
        default=True,
        config_parameter="alamia_travel.dashboard_show_attention_operations"
    )
    dashboard_show_quick_actions_operations = fields.Boolean(
        string="Operations: Show Quick Action Shortcuts",
        default=True,
        config_parameter="alamia_travel.dashboard_show_quick_actions_operations"
    )
    dashboard_show_team_workload_operations = fields.Boolean(
        string="Operations: Show Team Workload Matrix",
        default=True,
        config_parameter="alamia_travel.dashboard_show_team_workload_operations"
    )
    dashboard_show_sales_by_service_operations = fields.Boolean(
        string="Operations: Show Sales by Service",
        default=True,
        config_parameter="alamia_travel.dashboard_show_sales_by_service_operations"
    )
    dashboard_show_sales_by_staff_operations = fields.Boolean(
        string="Operations: Show Salesperson Performance",
        default=True,
        config_parameter="alamia_travel.dashboard_show_sales_by_staff_operations"
    )

    # Sales Director Widgets
    dashboard_show_attention_sales = fields.Boolean(
        string="Sales: Show Attention & Exception Cards",
        default=True,
        config_parameter="alamia_travel.dashboard_show_attention_sales"
    )
    dashboard_show_quick_actions_sales = fields.Boolean(
        string="Sales: Show Quick Action Shortcuts",
        default=True,
        config_parameter="alamia_travel.dashboard_show_quick_actions_sales"
    )
    dashboard_show_team_workload_sales = fields.Boolean(
        string="Sales: Show Team Workload Matrix",
        default=False,
        config_parameter="alamia_travel.dashboard_show_team_workload_sales"
    )
    dashboard_show_sales_by_service_sales = fields.Boolean(
        string="Sales: Show Sales by Service",
        default=True,
        config_parameter="alamia_travel.dashboard_show_sales_by_service_sales"
    )
    dashboard_show_sales_by_staff_sales = fields.Boolean(
        string="Sales: Show Salesperson Performance",
        default=True,
        config_parameter="alamia_travel.dashboard_show_sales_by_staff_sales"
    )

    # Ops & Marketing Widgets
    dashboard_show_attention_ops_marketing = fields.Boolean(
        string="Ops & Marketing: Show Attention & Exception Cards",
        default=True,
        config_parameter="alamia_travel.dashboard_show_attention_ops_marketing"
    )
    dashboard_show_quick_actions_ops_marketing = fields.Boolean(
        string="Ops & Marketing: Show Quick Action Shortcuts",
        default=True,
        config_parameter="alamia_travel.dashboard_show_quick_actions_ops_marketing"
    )
    dashboard_show_team_workload_ops_marketing = fields.Boolean(
        string="Ops & Marketing: Show Team Workload Matrix",
        default=False,
        config_parameter="alamia_travel.dashboard_show_team_workload_ops_marketing"
    )
    dashboard_show_sales_by_service_ops_marketing = fields.Boolean(
        string="Ops & Marketing: Show Sales by Service",
        default=True,
        config_parameter="alamia_travel.dashboard_show_sales_by_service_ops_marketing"
    )
    dashboard_show_sales_by_staff_ops_marketing = fields.Boolean(
        string="Ops & Marketing: Show Salesperson Performance",
        default=True,
        config_parameter="alamia_travel.dashboard_show_sales_by_staff_ops_marketing"
    )
