# -*- coding: utf-8 -*-
from sqlalchemy.engine import default

from odoo import fields, models


class BranchCommissionLine(models.Model):
    _name = "branch.commission.line"
    _description = "Branch Commission Line"

    company_id = fields.Many2one(comodel_name='res.company', string="Branch")
    target_amount = fields.Float(string="Target Amount")
    percentage = fields.Float(string="Percentage %")
    branch_commission_id = fields.Many2one(comodel_name='branch.commission',string="Branch Commission")








