# -*- coding: utf-8 -*-

from odoo import fields, models
from odoo.exceptions import ValidationError


class StockTransferAccount(models.Model):
    _name = "stock.transfer.account"
    _description = "Stock Transfer Account"

    account_debit = fields.Many2one(comodel_name='account.account', string="Account Debit",required=True)
    account_credit = fields.Many2one(comodel_name='account.account', string="Account Credit",required=True)
    company_id = fields.Many2one(comodel_name='res.company', string="Company",required=True)