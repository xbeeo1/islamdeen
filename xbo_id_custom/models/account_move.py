# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import timedelta, date, datetime
import calendar

class AccountMoveInherit(models.Model):
    _inherit = 'account.move'

    employee_id = fields.Many2one(comodel_name='hr.employee', string='Employee',)
    month = fields.Selection([
        ('1', 'January'),
        ('2', 'February'),
        ('3', 'March'),
        ('4', 'April'),
        ('5', 'May'),
        ('6', 'June'),
        ('7', 'July'),
        ('8', 'August'),
        ('9', 'September'),
        ('10', 'October'),
        ('11', 'November'),
        ('12', 'December'),
    ])

    commission_type = fields.Selection(
        [('branch', 'Branch'), ('department', 'Department'), ('product_categ', 'Product Category')], default='branch')

    product_categ_id = fields.Many2one(
        'product.category',
        string='Product Category'
    )

