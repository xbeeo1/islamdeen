# -*- coding: utf-8 -*-
from sqlalchemy.engine import default

from odoo import fields, models


class DepartmentCommissionLine(models.Model):
    _name = "department.commission.line"
    _description = "Department Commission Line"

    department_id = fields.Many2one(comodel_name='hr.department', string="Department")
    target_amount = fields.Float(string="Target Amount")
    percentage = fields.Float(string="Percentage %")
    department_commission_id = fields.Many2one(comodel_name='department.commission',string="Department Commission")