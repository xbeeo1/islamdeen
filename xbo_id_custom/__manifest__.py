# -*- coding: utf-8 -*-
{
    "name": "Xbo ID Custom",

    'version': '19.0.0.0',

    'summary': """Xbo ID Custom""",

    'description': """Xbo ID Custom""",

    'category': 'custom',

    'author': "Xbeeo",

    'website': 'https://xbeeo.com/',

    "depends": ['base','account','sale_management','hr','stock'],

    "data": [
        'security/ir.model.access.csv',
        'views/sale_order_views.xml',
        'views/stock_picking_views.xml',
        'views/hr_employee_views.xml',
        'views/account_move_views.xml',
        'views/branch_commission_views.xml',
        'views/department_commission_views.xml',
        'views/product_template_views.xml',
        'views/product_variant_views.xml',
        'wizard/fund_transfer_wizard_views.xml',
        'wizard/commission_wizard_views.xml',
    ],

}
