# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class TravelScheduleActivityWizard(models.TransientModel):
    _name = 'travel.schedule.activity.wizard'
    _description = 'Schedule Task & Activity Wizard'

    user_id = fields.Many2one(
        'res.users',
        string='Assigned Staff Member',
        required=True,
        default=lambda self: self.env.user,
        domain=[('share', '=', False), ('active', '=', True)]
    )

    activity_type_id = fields.Many2one(
        'mail.activity.type',
        string='Activity Type',
        required=True,
        default=lambda self: self.env['mail.activity.type'].search([], limit=1)
    )

    summary = fields.Char(
        string='Task Title / Summary',
        required=True
    )

    date_deadline = fields.Date(
        string='Due Date',
        required=True,
        default=fields.Date.context_today
    )

    partner_id = fields.Many2one(
        'res.partner',
        string='Related Customer / Partner'
    )

    note = fields.Text(
        string='Instructions / Notes'
    )

    def action_schedule_task(self):
        self.ensure_one()

        # Determine target record model and ID
        if self.partner_id:
            res_model = 'res.partner'
            res_id = self.partner_id.id
        else:
            # Default to the assigned user's partner record if no customer specified
            res_model = 'res.partner'
            res_id = self.user_id.partner_id.id

        res_model_id = self.env['ir.model']._get_id(res_model)

        activity = self.env['mail.activity'].sudo().create({
            'res_model_id': res_model_id,
            'res_id': res_id,
            'activity_type_id': self.activity_type_id.id,
            'summary': self.summary,
            'note': self.note or '',
            'date_deadline': self.date_deadline,
            'user_id': self.user_id.id,
        })

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Task Scheduled'),
                'message': _('Task "%s" successfully assigned to %s.') % (self.summary, self.user_id.name),
                'sticky': False,
                'type': 'success',
                'next': {'type': 'ir.actions.act_window_close'},
            }
        }
