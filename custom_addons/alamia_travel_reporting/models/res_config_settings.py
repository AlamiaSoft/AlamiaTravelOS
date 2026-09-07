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

    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        icp = self.env['ir.config_parameter'].sudo()

        def parse_bool(key, default):
            val = icp.get_param(key, None)
            if val is None:
                return default
            return val in ('True', '1', True)

        res.update(
            dashboard_show_attention_ceo=parse_bool('alamia_travel.dashboard_show_attention_ceo', True),
            dashboard_show_quick_actions_ceo=parse_bool('alamia_travel.dashboard_show_quick_actions_ceo', True),
            dashboard_show_team_workload_ceo=parse_bool('alamia_travel.dashboard_show_team_workload_ceo', True),
            dashboard_show_sales_by_service_ceo=parse_bool('alamia_travel.dashboard_show_sales_by_service_ceo', True),
            dashboard_show_sales_by_staff_ceo=parse_bool('alamia_travel.dashboard_show_sales_by_staff_ceo', True),

            dashboard_show_attention_operations=parse_bool('alamia_travel.dashboard_show_attention_operations', True),
            dashboard_show_quick_actions_operations=parse_bool('alamia_travel.dashboard_show_quick_actions_operations', True),
            dashboard_show_team_workload_operations=parse_bool('alamia_travel.dashboard_show_team_workload_operations', True),
            dashboard_show_sales_by_service_operations=parse_bool('alamia_travel.dashboard_show_sales_by_service_operations', True),
            dashboard_show_sales_by_staff_operations=parse_bool('alamia_travel.dashboard_show_sales_by_staff_operations', True),

            dashboard_show_attention_sales=parse_bool('alamia_travel.dashboard_show_attention_sales', True),
            dashboard_show_quick_actions_sales=parse_bool('alamia_travel.dashboard_show_quick_actions_sales', True),
            dashboard_show_team_workload_sales=parse_bool('alamia_travel.dashboard_show_team_workload_sales', False),
            dashboard_show_sales_by_service_sales=parse_bool('alamia_travel.dashboard_show_sales_by_service_sales', True),
            dashboard_show_sales_by_staff_sales=parse_bool('alamia_travel.dashboard_show_sales_by_staff_sales', True),

            dashboard_show_attention_ops_marketing=parse_bool('alamia_travel.dashboard_show_attention_ops_marketing', True),
            dashboard_show_quick_actions_ops_marketing=parse_bool('alamia_travel.dashboard_show_quick_actions_ops_marketing', True),
            dashboard_show_team_workload_ops_marketing=parse_bool('alamia_travel.dashboard_show_team_workload_ops_marketing', False),
            dashboard_show_sales_by_service_ops_marketing=parse_bool('alamia_travel.dashboard_show_sales_by_service_ops_marketing', True),
            dashboard_show_sales_by_staff_ops_marketing=parse_bool('alamia_travel.dashboard_show_sales_by_staff_ops_marketing', True),
        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        icp = self.env['ir.config_parameter'].sudo()

        icp.set_param('alamia_travel.dashboard_show_attention_ceo', str(self.dashboard_show_attention_ceo))
        icp.set_param('alamia_travel.dashboard_show_quick_actions_ceo', str(self.dashboard_show_quick_actions_ceo))
        icp.set_param('alamia_travel.dashboard_show_team_workload_ceo', str(self.dashboard_show_team_workload_ceo))
        icp.set_param('alamia_travel.dashboard_show_sales_by_service_ceo', str(self.dashboard_show_sales_by_service_ceo))
        icp.set_param('alamia_travel.dashboard_show_sales_by_staff_ceo', str(self.dashboard_show_sales_by_staff_ceo))

        icp.set_param('alamia_travel.dashboard_show_attention_operations', str(self.dashboard_show_attention_operations))
        icp.set_param('alamia_travel.dashboard_show_quick_actions_operations', str(self.dashboard_show_quick_actions_operations))
        icp.set_param('alamia_travel.dashboard_show_team_workload_operations', str(self.dashboard_show_team_workload_operations))
        icp.set_param('alamia_travel.dashboard_show_sales_by_service_operations', str(self.dashboard_show_sales_by_service_operations))
        icp.set_param('alamia_travel.dashboard_show_sales_by_staff_operations', str(self.dashboard_show_sales_by_staff_operations))

        icp.set_param('alamia_travel.dashboard_show_attention_sales', str(self.dashboard_show_attention_sales))
        icp.set_param('alamia_travel.dashboard_show_quick_actions_sales', str(self.dashboard_show_quick_actions_sales))
        icp.set_param('alamia_travel.dashboard_show_team_workload_sales', str(self.dashboard_show_team_workload_sales))
        icp.set_param('alamia_travel.dashboard_show_sales_by_service_sales', str(self.dashboard_show_sales_by_service_sales))
        icp.set_param('alamia_travel.dashboard_show_sales_by_staff_sales', str(self.dashboard_show_sales_by_staff_sales))

        icp.set_param('alamia_travel.dashboard_show_attention_ops_marketing', str(self.dashboard_show_attention_ops_marketing))
        icp.set_param('alamia_travel.dashboard_show_quick_actions_ops_marketing', str(self.dashboard_show_quick_actions_ops_marketing))
        icp.set_param('alamia_travel.dashboard_show_team_workload_ops_marketing', str(self.dashboard_show_team_workload_ops_marketing))
        icp.set_param('alamia_travel.dashboard_show_sales_by_service_ops_marketing', str(self.dashboard_show_sales_by_service_ops_marketing))
        icp.set_param('alamia_travel.dashboard_show_sales_by_staff_ops_marketing', str(self.dashboard_show_sales_by_staff_ops_marketing))
