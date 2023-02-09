# -*- coding: utf-8 -*-
{
    'name': "jt_product_repeat",

    'summary': "Eauzon Repeat Materials",

    'description': "",

    'author': "jaco tech",
    'website': "https://jaco.tech",
    "license": "AGPL-3",


    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'product', 'stock', 'mrp', 'sale'],

    # always loaded
    'data': [
        'report/sale_report_templates.xml',
        'security/ir.model.access.csv',
        'data/uom_data.xml',
        'views/product_template_view.xml',
        'views/recycled_material_views.xml',
        'views/res_config_settings_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
