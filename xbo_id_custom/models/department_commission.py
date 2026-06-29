# -*- coding: utf-8 -*-
from sqlalchemy.engine import default

from odoo import fields, models
from odoo.exceptions import ValidationError

class DepartmentCommission(models.Model):
    _name = "department.commission"
    _description = "Department Commission"

    name = fields.Char(string='Name',required=True)
    date = fields.Datetime(string='Date',default=fields.Date.today(),required=True)
    company_id = fields.Many2one(comodel_name='res.company', string="Branch")
    state = fields.Selection([('draft','Draft'),('confirmed','Confirmed'),('cancelled','Cancelled')],string='State',default='draft')
    department_commission_line = fields.One2many("department.commission.line", "department_commission_id",
                                            string="Department Commission Line")

    def action_confirmed(self):
        for rec in self:
            already_done = self.search([
                ('id', '!=', rec.id),
                ('state', '=', 'confirmed')
            ], limit=1)
            if already_done:
                raise ValidationError('A record is already in confirmed state. Please cancel it first.')
        self.state = 'confirmed'

    def action_cancelled(self):
        self.state = 'cancelled'
