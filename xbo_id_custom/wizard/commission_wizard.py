# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import timedelta, date, datetime,time
from odoo.exceptions import ValidationError
import calendar


class CommissionWizard(models.TransientModel):
    _name = "commission.wizard"
    _description = "Commission Wizard"


    commission_type = fields.Selection([('branch','Branch'),('department','Department'),('product_categ','Product Category')], default='branch', required=True)
    company_id = fields.Many2one(comodel_name='res.company', string="Branch", required=True)
    department_id = fields.Many2one(comodel_name='hr.department', string="Department",domain="[('company_id', '=', company_id)]")
    product_categ_id = fields.Many2one(comodel_name='product.category', string="Product Category")
    employee_ids = fields.Many2many(comodel_name='hr.employee', string='Employee', domain="[('company_id', '=', company_id)]")
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
    ], required=True)

    @api.onchange('commission_type')
    def onchange_commission_type(self):
        for x in self:
            x.company_id = None
            x.department_id = None
            x.product_categ_id = None
            x.employee_ids = None

    def action_confirm(self):
        year = fields.Date.today().year
        month = int(self.month)

        first_date = date(year, month, 1)

        last_day = calendar.monthrange(year, month)[1]
        last_date = date(year, month, last_day)
        if self.commission_type == 'branch' and self.company_id:
            partner_obj = self.env['res.partner'].search([('name', '=', self.company_id.name)], limit=1)
            if not partner_obj:
                raise ValidationError('Branch does not have a Partner.')
            moves_bill = self.env['account.move'].search([
                ('move_type', '=', 'in_invoice'),
                ('invoice_date', '>=', first_date),
                ('invoice_date', '<=', last_date),
                ('partner_id', '=', partner_obj.id),
                ('commission_type', '=', self.commission_type),
                ('state', '!=', 'cancel'),

            ])

            if moves_bill:
                raise ValidationError(
                    _("A commission bill has already been generated for Branch '%s' in the selected month.")
                    % self.company_id.name
                )

            inv_move = self.env['account.move'].search([
                ('move_type', '=', 'out_invoice'),
                ('invoice_date', '>=', first_date),
                ('invoice_date', '<=', last_date),
                ('payment_state', '=', 'paid'),

            ])
            inv_total_amount = sum(inv_move.mapped('amount_untaxed'))
            pos_orders = self.env['pos.order'].search([
                ('date_order', '>=', datetime.combine(first_date, time.min)),
                ('date_order', '<=', datetime.combine(last_date, time.max)),
                ('state', '=', 'done')
            ])

            pos_total_amount = sum(pos_orders.mapped('lines.price_subtotal'))

            grand_total = inv_total_amount + pos_total_amount

            branch_commission = self.env['branch.commission'].search([
                ('state', '=', 'confirmed')
            ], limit=1)

            if not branch_commission:
                raise ValidationError(_("Please Configure Branch Commission."))
            branch_line = branch_commission.branch_commission_line.filtered(
                lambda l: l.company_id.id == self.company_id.id
            )

            if not branch_line:
                raise ValidationError(
                    _("No commission configuration found for branch %s.")
                    % self.company_id.name
                )
            branch_line = branch_line[0]

            if grand_total < branch_line.target_amount:
                raise ValidationError(
                    _("Target amount has not been achieved.\n"
                      "Target: %.2f\n"
                      "Current Sales: %.2f")
                    % (branch_line.target_amount, grand_total)
                )

            commission_amount = grand_total * (branch_line.percentage / 100)

            commission_product = self.env['product.product'].search([
                ('is_commission', '=', True)
            ], limit=1)

            if not commission_product:
                raise ValidationError(
                    "Please configure a product with 'Is Commission' enabled."
                )


            bill = self.env['account.move'].create({
                'move_type': 'in_invoice',
                'partner_id': partner_obj.id,
                'month':self.month,
                'commission_type': self.commission_type,
                'state': 'draft',
                'invoice_date': fields.Date.today(),
                'invoice_line_ids': [(0, 0, {
                    'product_id': commission_product.id,
                    'quantity': 1,
                    'price_unit': commission_amount,
                })]
            })
            bill.action_post()
        elif self.commission_type == 'department' and self.department_id:
            partner_obj = self.env['res.partner'].search([('name', '=', self.department_id.name)], limit=1)
            if not partner_obj:
                raise ValidationError('Department does not have a Partner.')
            moves_bill = self.env['account.move'].search([
                ('move_type', '=', 'in_invoice'),
                ('invoice_date', '>=', first_date),
                ('invoice_date', '<=', last_date),
                ('partner_id', '=', partner_obj.id),
                ('commission_type', '=', self.commission_type),
                ('state', '!=', 'cancel'),

            ])

            if moves_bill:
                raise ValidationError(
                    _("A commission bill has already been generated for department '%s' in the selected month.")
                    % self.company_id.name
                )

            inv_move = self.env['account.move'].search([
                ('move_type', '=', 'out_invoice'),
                ('invoice_date', '>=', first_date),
                ('invoice_date', '<=', last_date),
                ('payment_state', '=', 'paid'),

            ])
            inv_total_amount = sum(inv_move.mapped('amount_untaxed'))
            pos_orders = self.env['pos.order'].search([
                ('date_order', '>=', datetime.combine(first_date, time.min)),
                ('date_order', '<=', datetime.combine(last_date, time.max)),
                ('state', '=', 'done')
            ])

            pos_total_amount = sum(pos_orders.mapped('lines.price_subtotal'))

            grand_total = inv_total_amount + pos_total_amount

            dep_commission = self.env['department.commission'].search([
                ('state', '=', 'confirmed')
            ], limit=1)

            if not dep_commission:
                raise ValidationError(_("No confirmed Department Commission found."))
            dep_line = dep_commission.department_commission_line.filtered(
                lambda l: l.department_id.id == self.department_id.id
            )

            if not dep_line:
                raise ValidationError(
                    _("No commission configuration found for department %s.")
                    % self.company_id.name
                )
            dep_line = dep_line[0]

            if grand_total < dep_line.target_amount:
                raise ValidationError(
                    _("Target amount has not been achieved.\n"
                      "Target: %.2f\n"
                      "Current Sales: %.2f")
                    % (dep_line.target_amount, grand_total)
                )

            commission_amount = grand_total * (dep_line.percentage / 100)

            commission_product = self.env['product.product'].search([
                ('is_commission', '=', True)
            ], limit=1)

            if not commission_product:
                raise ValidationError(
                    "Please configure a product with 'Is Commission' enabled."
                )

            bill = self.env['account.move'].create({
                'move_type': 'in_invoice',
                'partner_id': partner_obj.id,
                'month': self.month,
                'commission_type': self.commission_type,
                'state': 'draft',
                'invoice_date': fields.Date.today(),
                'invoice_line_ids': [(0, 0, {
                    'product_id': commission_product.id,
                    'quantity': 1,
                    'price_unit': commission_amount,
                })]
            })
            bill.action_post()
        elif self.commission_type == 'product_categ' and self.product_categ_id:
            products = self.env['product.product'].search([
                ('categ_id', '=', self.product_categ_id.id)
            ])

            if not products:
                raise ValidationError(_("No products found in the selected category."))
            if self.employee_ids:
                for employee in self.employee_ids:
                    partner_obj = self.env['res.partner'].search([
                        ('employee_ids', 'in', employee.id)
                    ], limit=1)
                    if not partner_obj:
                        raise ValidationError(
                            _("Employee %s does not have a Partner.")
                            % employee.name
                        )
                    moves_bill = self.env['account.move'].search([
                        ('move_type', '=', 'in_invoice'),
                        ('invoice_date', '>=', first_date),
                        ('invoice_date', '<=', last_date),
                        ('employee_id', '=', employee.id),
                        ('partner_id', '=', partner_obj.id),
                        ('commission_type', '=', self.commission_type),
                        ('product_categ_id', '=', self.product_categ_id.id),
                        ('state', '!=', 'cancel'),
                    ], limit=1)

                    if moves_bill:
                        raise ValidationError(_(
                            "Commission bill for employee '%s' and category '%s' has already been generated for the selected month."
                        ) % (employee.name, self.product_categ_id.name))

                    invoice_lines = self.env['account.move.line'].search([
                        ('move_id.move_type', '=', 'out_invoice'),
                        ('move_id.payment_state', '=', 'paid'),
                        ('move_id.invoice_date', '>=', first_date),
                        ('move_id.invoice_date', '<=', last_date),
                        ('product_id', 'in', products.ids),
                        ('move_id.employee_id', '=', employee.id),
                    ])
                    sale_amount = sum(invoice_lines.mapped('price_subtotal'))
                    pos_lines = self.env['pos.order.line'].search([
                        ('order_id.state', '=', 'done'),
                        ('order_id.date_order', '>=', datetime.combine(first_date, time.min)),
                        ('order_id.date_order', '<=', datetime.combine(last_date, time.max)),
                        ('product_id', 'in', products.ids),
                        ('order_id.employee_id', '=', employee.id),
                    ])

                    pos_amount = sum(pos_lines.mapped('price_subtotal'))

                    grand_total = sale_amount + pos_amount
                    commission_amount = grand_total * (employee.commission_per / 100)

                    commission_product = self.env['product.product'].search([
                        ('is_commission', '=', True)
                    ], limit=1)

                    if not commission_product:
                        raise ValidationError(
                            "Please configure a product with 'Is Commission' enabled."
                        )

                    bill = self.env['account.move'].create({
                        'move_type': 'in_invoice',
                        'partner_id': partner_obj.id,
                        'employee_id': employee.id,
                        'month': self.month,
                        'commission_type': 'product_categ',
                        'product_categ_id': self.product_categ_id.id,
                        'invoice_date': fields.Date.today(),
                        'invoice_line_ids': [(0, 0, {
                            'product_id': commission_product.id,
                            'quantity': 1,
                            'price_unit': commission_amount,
                        })]
                    })

                    bill.action_post()

            else:
                invoice_lines = self.env['account.move.line'].search([
                    ('move_id.move_type', '=', 'out_invoice'),
                    ('move_id.payment_state', '=', 'paid'),
                    ('move_id.invoice_date', '>=', first_date),
                    ('move_id.invoice_date', '<=', last_date),
                    ('product_id', 'in', products.ids),
                ])

                employee_totals = {}

                for line in invoice_lines:
                    employee = line.move_id.employee_id
                    if not employee:
                        continue

                    employee_totals.setdefault(employee.id, 0)
                    employee_totals[employee.id] += line.price_subtotal

                pos_lines = self.env['pos.order.line'].search([
                    ('order_id.state', '=', 'done'),
                    ('order_id.date_order', '>=', datetime.combine(first_date, time.min)),
                    ('order_id.date_order', '<=', datetime.combine(last_date, time.max)),
                    ('product_id', 'in', products.ids),
                ])

                for line in pos_lines:
                    employee = line.order_id.employee_id
                    if not employee:
                        continue

                    employee_totals.setdefault(employee.id, 0)
                    employee_totals[employee.id] += line.price_subtotal

                for employee_id, sale in employee_totals.items():
                    employee = self.env['hr.employee'].browse(employee_id)

                    if sale <= 0:
                        continue

                    partner = self.env['res.partner'].search([
                        ('employee_ids', 'in', employee.id)
                    ], limit=1)

                    if not partner:
                        raise ValidationError(
                            _("Employee %s does not have a Partner.")
                            % employee.name
                        )

                    # Duplicate Bill Check
                    moves_bill = self.env['account.move'].search([
                        ('move_type', '=', 'in_invoice'),
                        ('invoice_date', '>=', first_date),
                        ('invoice_date', '<=', last_date),
                        ('employee_id', '=', employee.id),
                        ('partner_id', '=', partner.id),
                        ('commission_type', '=', 'product_categ'),
                        ('product_categ_id', '=', self.product_categ_id.id),
                        ('state', '!=', 'cancel'),
                    ], limit=1)

                    if moves_bill:
                        raise ValidationError(_(
                            "Commission bill for employee '%s' and category '%s' has already been generated for the selected month."
                        ) % (employee.name, self.product_categ_id.name))

                    commission_amount = sale * (employee.commission_per / 100)

                    if commission_amount <= 0:
                        continue

                    commission_product = self.env['product.product'].search([
                        ('is_commission', '=', True)
                    ], limit=1)

                    if not commission_product:
                        raise ValidationError(
                            _("Please configure a product with 'Is Commission' enabled.")
                        )

                    bill = self.env['account.move'].create({
                        'move_type': 'in_invoice',
                        'partner_id': partner.id,
                        'employee_id': employee.id,
                        'month': self.month,
                        'commission_type': 'product_categ',
                        'product_categ_id': self.product_categ_id.id,
                        'invoice_date': fields.Date.today(),
                        'invoice_line_ids': [(0, 0, {
                            'product_id': commission_product.id,
                            'quantity': 1,
                            'price_unit': commission_amount,
                        })]
                    })

                    bill.action_post()

        return True



