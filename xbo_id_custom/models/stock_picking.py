# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class StockPickingInherit(models.Model):
    _inherit = 'stock.picking'
    _description = 'stock.picking.inherit'

    employee_id = fields.Many2one(comodel_name='hr.employee', string='Employee')

    picking_code = fields.Char(
        compute='_compute_picking_code',
        store=True,
    )

    @api.depends('picking_type_id', 'picking_type_id.code')
    def _compute_picking_code(self):
        for rec in self:
            rec.picking_code = rec.picking_type_id.code or ''


    @api.model_create_multi
    def create(self, vals_list):
        pickings = super().create(vals_list)
        for picking in pickings:
            if picking.origin:
                sale_order = self.env['sale.order'].search(
                    [('name', '=', picking.origin)],
                    limit=1
                )
                if sale_order:
                    picking.employee_id = sale_order.employee_id.id if sale_order.employee_id else None

        return pickings