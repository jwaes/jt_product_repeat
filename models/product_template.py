import logging
from odoo import api, fields, models

_logger = logging.getLogger(__name__)

class ProductTemplate(models.Model):
    _inherit = "product.template"

    recycled_material_id = fields.Many2one('jt.recycled.material', string="Recycled material")

    thickness = fields.Float(compute='_compute_thickness', inverse='_set_thickness', string='Thickness')
    
    bottle_equivalent = fields.Float(compute='_compute_bottle_equivalent', string='Bottle Equivalent', store=True,)

    has_bottles = fields.Char(compute='_compute_has_bottles', string='has_bottles')
    
    @api.depends('bottle_equivalent')
    def _compute_has_bottles(self):
        self.ensure_one()
        self.has_bottles = self.bottle_equivalent > 0.0

    surface_uom = fields.Boolean(compute='_compute_surface_uom', string='Surface Uom')
    
    @api.depends('uom_id.category_id')
    def _compute_surface_uom(self):
        self.surface_uom = self.uom_id.category_id.name == 'Surface'

    @api.depends('product_variant_ids', 'product_variant_ids.thickness')
    def _compute_thickness(self):
        unique_variants = self.filtered(lambda template: len(template.product_variant_ids) == 1)
        for template in unique_variants:
            template.thickness = template.product_variant_ids.thickness
        for template in (self - unique_variants):
            template.thickness = 0.0

    
    @api.depends('recycled_material_id', 'recycled_material_id.density', 'recycled_material_id.bottles_per_kg', 'volume', 'bom_ids', 'product_variant_ids', 'product_variant_ids.bottle_equivalent')
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
            if self.surface_uom and self.thickness != 0.0:
                thickness_m = self.thickness / 1000
                vol = self.uom_id.factor_inv * thickness_m    
                _logger.info("Volume: %0.3fm^2 * %0.6fm = %0.4fm^3", self.uom_id.factor_inv, thickness_m, vol)
                self.volume = vol

    @api.onchange('volume','recycled_material_id')                
    def _update_weight(self):
        unique_variants = self.filtered(lambda template: len(template.product_variant_ids) == 1)
        for template in unique_variants:
            template.product_variant_ids._update_weight()
            template.weight = template.product_variant_ids.weight
        for template in (self - unique_variants):
            _logger.warning("Hard setting to 0.0")
            template.weight = self._update_volume()        

    def update_repeat_info(self):
        for template in self:
            template._compute_thickness()


    # @api.onchange('bottle_equivalent')
    # def _onchange_bottle_equivalent(self):
    #     message = "template: %0f bottles"
    #     self.message_post(body=message, message_type='notification')