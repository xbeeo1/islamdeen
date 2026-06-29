# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'

    @api.model
    def _default_employee(self):
        employee = self.env['hr.employee'].search(
            [('user_id', '=', self.env.user.id)],
            limit=1
        )
        return employee or False

    employee_id = fields.Many2one(comodel_name='hr.employee',string='Employee',default=_default_employee)



    def _prepare_invoice(self):
        invoice_vals = super(SaleOrderInherit, self)._prepare_invoice()
        invoice_vals['employee_id'] = self.employee_id.id
        return invoice_vals