import logging
from odoo import api, fields, models

_logger = logging.getLogger(__name__)

class ProductProduct(models.Model):
    _inherit = "product.product"

    thickness = fields.Float(string="Thickness")

    density = fields.Float(compute='_compute_density', string='Density', digits="12,4")
    
    @api.depends('volume', 'weight', 'recycled_material_id')
    def _compute_density(self):
        for prod in self:
            if prod.recycled_material_id:
                prod.density = prod.recycled_material_id.density
            elif prod.volume > 0.0:
                prod.density = prod.weight / prod.volume
                _logger.debug("product density = %0.4fkg/m3", prod.density)
            else:
                prod.density = 0.0

    bottle_equivalent = fields.Float(compute='_compute_product_bottle_equivalent', string='Bottle Equivalent', store=True)

    @api.depends('recycled_material_id', 'recycled_material_id.density', 'recycled_material_id.bottles_per_kg', 'volume')
    def _compute_product_bottle_equivalent(self):
        for product in self:
            if not product.bom_ids:
                equi = product.calculate_product_bottle_equivalent_for_volume(product.volume)
                product.bottle_equivalent = equi
            else:              
                pass

    def calculate_product_bottle_equivalent_for_volume(self, volume):
        self.ensure_one()
        bottles = 0.0
        if not self.bom_ids and self.recycled_material_id:
            bottles = self.recycled_material_id.calculate_pet_bottles_equivalent(volume)
        return bottles


    @api.onchange('thickness')
    def _update_volume(self):
        for prod in self:
            if prod.uom_id and not prod.bom_ids:
                if prod.surface_uom and prod.thickness != 0.0:
                    vol = prod.uom_id.factor_inv * (prod.thickness / 1000)
                    _logger.info("Volume: %0.2f * %0.4f = %0.4f", self.uom_id.factor_inv, (self.thickness / 1000), vol)                     
                    prod.volume = vol
                    _logger.info("set volume")
                    prod.weight = prod.calculate_product_weight_for_volume(prod.volume)
                    _logger.info("calculated weight")

    @api.onchange('volume')
    def _update_weight(self):
        _logger.info("triggered update weight")
        for prod in self:
            weight = prod.calculate_product_weight_for_volume(prod.volume)
            if weight:
                prod.weight = weight
            else:
                pass

    def calculate_product_weight_for_volume(self, volume):
        self.ensure_one()
        if self.uom_id and self.recycled_material_id:
            return self.recycled_material_id.calculate_weight(self.volume)   
        else:
            return 0.0     

    # @api.onchange('bottle_equivalent')
    # def _onchange_bottle_equivalent(self):
    #     message = "prod: %0f bottles"
    #     self.message_post(body=message, message_type='notification')