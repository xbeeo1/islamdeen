# -*- coding: utf-8 -*-

from odoo import fields, models


class ProductVariantInherit(models.Model):
    _inherit = 'product.product'

    is_commission = fields.Boolean(string="Is commission",related='product_tmpl_id.is_commission', store=True)
