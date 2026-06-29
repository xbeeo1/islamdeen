# -*- coding: utf-8 -*-
from sqlalchemy.engine import default

from odoo import fields, models
from odoo.exceptions import ValidationError


class BranchCommission(models.Model):
    _name = "branch.commission"
    _description = "Branch Commission"

    name = fields.Char(string='Name',required=True)
    date = fields.Datetime(string='Date',default=fields.Date.today(),required=True)
    state = fields.Selection([('draft','Draft'),('confirmed','Confirmed'),('cancelled','Cancelled')],string='State',default='draft')
    branch_commission_line = fields.One2many("branch.commission.line", "branch_commission_id",
                                            string="Branch Commission Line")

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

