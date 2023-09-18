import logging
from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    surface = fields.Float('Surface overruled')

    surface_uom = fields.Boolean(compute='_compute_surface_uom', string='Surface Uom')
    
    @api.depends('product_uom_category_id')
    def _compute_surface_uom(self):
        for bom in self:
            bom.surface_uom = bom.product_uom_category_id.name == 'Surface'

    @api.model_create_multi
    def create(self, vals):
        res = super(MrpBom, self).create(vals)
        self._calculate_bottle_equivalent()
        return res

    def write(self, vals):
        res = super(MrpBom, self).write(vals)
        self._calculate_bottle_equivalent()
        return res


    # @api.onchange('bom_line_ids', 'bom_line_ids.product_id', 'product_uom_id', 'surface')
    def _calculate_bottle_equivalent(self):
        for bom in self:
            bottles = 0.0
            product = bom.product_id
            if not product:
                if bom.product_tmpl_id.product_variant_count == 1 and not bom.product_tmpl_id.has_configurable_attributes:
                    product = bom.product_tmpl_id.product_variant_id
                    self._calculate_bottle_equivalent_for_product(bom, product)
                else:
                    for variant in bom.product_tmpl_id.product_variant_ids:
                        self._calculate_bottle_equivalent_for_product(bom, variant)
            else:
                self._calculate_bottle_equivalent_for_product(bom, product)

            # bom_product_type = "product.product"
            # if not bom_product:
            #     if bom.product_tmpl_id.product_variant_count == 1 and not bom.product_tmpl_id.has_configurable_attributes:
            #         bom_product = bom.product_tmpl_id.product_variant_id
            #         bom_product_type = "product.template"
            # _logger.info("┌── BOM for (%s) %s", bom_product_type, bom_product.name)
            # bom_surface= 0.0
            # if bom.surface_uom:
            #     bom_surface = bom.product_uom_id.ratio
            # if bom.surface != 0.0:
            #     bom_surface = bom.surface
            # _logger.info("├─ surface: %0.4fm^2", bom_surface)
            # bom_thickness = 0.0
            # bom_weight = 0.0
            # for bom_line in bom.bom_line_ids:
            #     bom_line_product = bom_line.product_id
            #     bom_thickness += bom_line_product.thickness
            #     _logger.info("├─┬─ %s", bom_line_product.name)
            #     thickness_m = bom_line_product.thickness / 1000
            #     volume = bom_surface * thickness_m
            #     # if volume:
            #     #     bom_line_weight = bom_line_product.calculate_product_weight_for_volume(volume) * bom_line.product_qty
            #     # else:
            #     #     bom_line_weight = bom_line_product.weight * bom_line.product_qty
            #     bom_line_weight = 0.0
            #     if bom_line_product.density > 0.0:
            #         bom_line_weight = volume * bom_line_product.density
            #     elif bom_line_product.recycled_material_id:
            #         bom_line_weight = volume * bom_line_product.recycled_material_id.density
            #     bom_weight += bom_line_weight
            #     _logger.info("│ ├─ %0.4fm^2 * %0.4fm = %0.4fm^3 (%0.2fkg)", bom_surface, thickness_m, volume, bom_line_weight)
            #     bom_line_bottles = 0.0
            #     if bom_line_product.bottle_equivalent > 0.0:
            #         bom_line_bottles = bom_line_product.bottle_equivalent * bom_line.product_qty
            #     else:
            #         bom_line_bottles = bom_line_product.calculate_product_bottle_equivalent_for_volume(volume) * bom_line.product_qty
            #     bottles += bom_line_bottles
            #     _logger.info("│ └─ %0.2f bottles * %0.2f = %0.2f", bom_line_product.bottle_equivalent, bom_line.product_qty, bom_line_bottles)    
            # bom_product.bottle_equivalent = bottles    
            # bom_product.thickness = bom_thickness
            # bom_product.weight = bom_weight
            # bom_product.volume = bom_surface * bom_thickness / 1000
            # _logger.info("└─> %0f bottles, %0.4fmm thickness, %0.4fm^3, %0.4fkg", bom_product.bottle_equivalent, bom_product.thickness, bom_product.volume, bom_product.weight)
                
                
    def _calculate_bottle_equivalent_for_product(self, bom, product):
        bottles = 0.0
        bom_product = product
        # if not bom_product:
        #     if bom.product_tmpl_id.product_variant_count == 1 and not bom.product_tmpl_id.has_configurable_attributes:
        #         bom_product = bom.product_tmpl_id.product_variant_id
        #         bom_product_type = "product.template"
        _logger.info("┌── BOM for %s", bom_product.name)
        bom_surface= 0.0
        if bom.surface_uom:
            bom_surface = bom.product_uom_id.ratio
        if bom.surface != 0.0:
            bom_surface = bom.surface
        _logger.info("├─ surface: %0.4fm^2", bom_surface)
        bom_thickness = 0.0
        bom_weight = 0.0
        for bom_line in bom.bom_line_ids:
            bom_line_product = bom_line.product_id
            if not bom_line._skip_bom_line(product):
                
                bom_thickness += bom_line_product.thickness
                _logger.info("├─┬─ %s", bom_line_product.name)
                thickness_m = bom_line_product.thickness / 1000
                volume = bom_surface * thickness_m
                # if volume:
                #     bom_line_weight = bom_line_product.calculate_product_weight_for_volume(volume) * bom_line.product_qty
                # else:
                #     bom_line_weight = bom_line_product.weight * bom_line.product_qty
                bom_line_weight = 0.0
                if bom_line_product.density > 0.0:
                    bom_line_weight = volume * bom_line_product.density
                elif bom_line_product.recycled_material_id:
                    bom_line_weight = volume * bom_line_product.recycled_material_id.density
                bom_weight += bom_line_weight
                _logger.info("│ ├─ %0.4fm^2 * %0.4fm = %0.4fm^3 (%0.2fkg)", bom_surface, thickness_m, volume, bom_line_weight)
                bom_line_bottles = 0.0
                if bom_line_product.bottle_equivalent > 0.0:
                    bom_line_bottles = bom_line_product.bottle_equivalent * bom_line.product_qty
                else:
                    bom_line_bottles = bom_line_product.calculate_product_bottle_equivalent_for_volume(volume) * bom_line.product_qty
                bottles += bom_line_bottles
                _logger.info("│ └─ %0.2f bottles * %0.2f = %0.2f", bom_line_product.bottle_equivalent, bom_line.product_qty, bom_line_bottles)
            else:
               _logger.info("├─XXXX %s", bom_line_product.name)    
        bom_product.bottle_equivalent = bottles    
        bom_product.thickness = bom_thickness
        bom_product.weight = bom_weight
        bom_product.volume = bom_surface * bom_thickness / 1000
        _logger.info("└─> %0f bottles, %0.4fmm thickness, %0.4fm^3, %0.4fkg", bom_product.bottle_equivalent, bom_product.thickness, bom_product.volume, bom_product.weight)
                    