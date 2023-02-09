from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    product_density_in_kg_cubic_meters = fields.Selection([
        ('0', 'Kilograms / Cubic Meters'),
        ('1', 'Something else'),
    ], 'Density unit of measure', config_parameter='product.density_in_kg_cubic_meters', default='0')
