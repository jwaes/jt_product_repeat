import logging
from odoo import api, fields, models

_logger = logging.getLogger(__name__)

class ProductProduct(models.Model):
    _inherit = "product.product"

    thickness = fields.Float(string="Thickness")

    bottle_equivalent = fields.Float(compute='_compute_product_bottle_equivalent', string='Bottle Equivalent', store=True, track_visibility='always')

    @api.depends('recycled_material_id', 'recycled_material_id.density', 'recycled_material_id.bottles_per_kg', 'volume')
    def _compute_product_bottle_equivalent(self):
        for product in self:
            product.bottle_equivalent = product.calculate_product_bottle_equivalent_for_volume(product.volume)

    def calculate_product_bottle_equivalent_for_volume(self, volume):
        if self.bom_ids:
            for bom in self.bom_ids:
                bom._calculate_bottle_equivalent()
                return bom.product_id.bottle_equivalent
        elif self.recycled_material_id:
            return self.recycled_material_id.calculate_pet_bottles_equivalent(volume)
        else:
            return 0.0


    @api.onchange('thickness')
    def _update_volume(self):
        if self.uom_id:
            if self.surface_uom and self.thickness != 0.0:
                vol = self.uom_id.factor_inv * (self.thickness / 1000)
                _logger.info("Surface: %0.2f * %0.2f = %0.2f", self.uom_id.factor_inv, (self.thickness / 1000), vol)                     
                self.volume = vol

    @api.onchange('volume', 'product_tmpl_id.volume')
    def _update_weight(self):
        weight = self.calculate_product_weight_for_volume(self.volume)
        if weight:
            self.weight = weight
        else:
            pass

    def calculate_product_weight_for_volume(self, volume):
        if self.uom_id and self.recycled_material_id:
            return self.recycled_material_id.calculate_weight(self.volume)   
        else:
            return 0.0     

    # @api.onchange('bottle_equivalent')
    # def _onchange_bottle_equivalent(self):
    #     message = "prod: %0f bottles"
    #     self.message_post(body=message, message_type='notification')