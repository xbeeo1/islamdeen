# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import timedelta, date, datetime
from odoo.exceptions import ValidationError
import calendar


class FundTransfer(models.TransientModel):
    _name = "fund.transfer"
    _description = "Fund Transfer"

    date = fields.Date(string="Date",default=fields.Date.today(),required=True)
    current_company_id = fields.Many2one(
        'res.company',
        default=lambda self: self.env.company,
        readonly=True
    )
    company_id = fields.Many2one(comodel_name='res.company', string="Branch",required=True,domain="[('id', '!=', current_company_id)]")
    sender_account_id = fields.Many2one(comodel_name='account.journal', string="Sender Account", required=True,
                                 domain="[('company_id', '=',current_company_id),('type','in',['cash','bank'])]")
    receiver_account_id = fields.Many2one(comodel_name='account.journal', string="Receiver Account", required=True,
                                 domain="[('company_id', '=', company_id),('type','in',['cash','bank'])]")
    amount = fields.Float(string="Amount",required=True)
    description = fields.Char(string="Description",required=True)



    def action_confirm(self):
        lines1 = []
        lines2 = []
        partner_obj_1 = self.env['res.partner'].search([('name','=',self.current_company_id.name)],limit=1)
        partner_obj_2 = self.env['res.partner'].search([('name','=',self.company_id.name)],limit=1)
        account_obj_1 = self.env['account.account'].search([('name','=','Inter-Company Fund Transfer'),('company_ids','in',self.current_company_id.id)],limit=1)
        account_obj_2 = self.env['account.account'].search([('name','=','Inter-Company Fund Transfer'),('company_ids','in',self.company_id.id)],limit=1)
        if not account_obj_1:
            raise ValidationError(
                _("The account 'Inter-Company Fund Transfer' is not configured for company '%s'. Please create this account and try again.")
                % self.current_company_id.name
            )

        if not account_obj_2:
            raise ValidationError(
                _("The account 'Inter-Company Fund Transfer' is not configured for company '%s'. Please create this account and try again.")
                % self.company_id.name
            )

        lines1.append((0, 0, {
            'account_id': account_obj_1.id,
            'debit': self.amount,
            'credit': 0.0,
            'name': self.description,
            'partner_id': partner_obj_2.id,
        }))
        lines1.append((0, 0, {
            'account_id': self.sender_account_id.default_account_id.id,
            'debit': 0.0,
            'credit': self.amount,
            'name': self.description,
            'partner_id': partner_obj_2.id,
        }))
        if lines1:
            move_obj = self.env['account.move'].create({
                'ref': self.description,
                'journal_id': self.sender_account_id.id,
                'move_type': 'entry',
                'line_ids': lines1,
                'company_id':self.current_company_id.id,
            })
        # second Company entry
        lines2.append((0, 0, {
            'account_id': self.receiver_account_id.default_account_id.id,
            'debit': self.amount,
            'credit': 0.0,
            'name': self.description,
            'partner_id': partner_obj_1.id,
        }))
        lines2.append((0, 0, {
            'account_id': account_obj_2.id,
            'debit': 0.0,
            'credit': self.amount,
            'name': self.description,
            'partner_id': partner_obj_1.id,
        }))
        if lines2:
            move_obj = self.env['account.move'].create({
                'ref': self.description,
                'journal_id': self.receiver_account_id.id,
                'move_type': 'entry',
                'line_ids': lines2,
                'company_id': self.company_id.id,
            })






