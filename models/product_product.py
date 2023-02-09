from odoo import api, fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    thickness = fields.Float(string="Thickness")

    bottle_equivalent = fields.Float(compute='_compute_product_bottle_equivalent', string='Bottle Equivalent', store=True, track_visibility='always')

    @api.depends('recycled_material_id', 'recycled_material_id.density', 'recycled_material_id.bottles_per_kg', 'volume')
    def _compute_product_bottle_equivalent(self):
        for product in self:
            if product.bom_ids:
                for bom in product.bom_ids:
                    bom._calculate_bottle_equivalent()
            elif product.recycled_material_id:
                product.bottle_equivalent = product.recycled_material_id.calculate_pet_bottles_equivalent(product.volume)

    @api.onchange('thickness')
    def _update_volume(self):
        if self.uom_id:
            if self.uom_id.category_id.name == "Surface" and self.thickness != 0.0:
                vol = self.uom_id.factor_inv * (self.thickness / 1000)                       
                self.volume = vol

    @api.onchange('volume')                
    def _update_weight(self):
        if self.uom_id and self.recycled_material_id:
            self.weight = self.volume * self.recycled_material_id.density

    @api.onchange('bottle_equivalent')
    def _onchange_bottle_equivalent(self):
        message = "prod: %0f bottles"
        self.message_post(body=message, message_type='notification')