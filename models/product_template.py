import logging
from odoo import api, fields, models

_logger = logging.getLogger(__name__)

class ProductTemplate(models.Model):
    _inherit = "product.template"

    recycled_material_id = fields.Many2one('jt.recycled.material', string="Recycled material")

    thickness = fields.Float(compute='_compute_thickness', inverse='_set_thickness', string='Thickness')
    
    bottle_equivalent = fields.Float(compute='_compute_bottle_equivalent', string='Bottle Equivalent', store=True, track_visibility='always')

    @api.depends('product_variant_ids', 'product_variant_ids.thickness')
    def _compute_thickness(self):
        unique_variants = self.filtered(lambda template: len(template.product_variant_ids) == 1)
        for template in unique_variants:
            template.thickness = template.product_variant_ids.thickness
        for template in (self - unique_variants):
            template.thickness = 0.0

    
    @api.depends('recycled_material_id', 'recycled_material_id.density', 'recycled_material_id.bottles_per_kg', 'volume', 'bom_ids')
    def _compute_bottle_equivalent(self):
        unique_variants = self.filtered(lambda template: len(template.product_variant_ids) == 1)
        for template in unique_variants:
            template.bottle_equivalent = template.product_variant_ids.bottle_equivalent
        for template in (self - unique_variants):
            _logger.warning("Hard setting to 0.0")
            template.bottle_equivalent = 0.0

    def _set_thickness(self):
        for template in self:
            if len(template.product_variant_ids) == 1:
                template.product_variant_ids.thickness = template.thickness

    @api.onchange('thickness', 'uom_id')
    def _update_volume(self):
        if self.uom_id:
            if self.uom_id.category_id.name == 'Surface' and self.thickness != 0.0:
                vol = self.uom_id.factor_inv * (self.thickness / 1000)                        
                self.volume = vol

    # @api.onchange('bottle_equivalent')
    # def _onchange_bottle_equivalent(self):
    #     message = "template: %0f bottles"
    #     self.message_post(body=message, message_type='notification')