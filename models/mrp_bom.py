import logging
from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    @api.onchange('bom_line_ids', 'bom_line_ids.product_id')
    def _calculate_bottle_equivalent(self):
        for bom in self:
            bottles = 0.0
            bom_product = bom.product_id
            if not bom_product:
                if bom.product_tmpl_id.product_variant_count == 1 and not bom.product_tmpl_id.has_configurable_attributes:
                    _logger.info("Bom for Template")
                    bom_product = bom.product_tmpl_id.product_variant_id
            else:
                _logger.info("Bom for Product")
            _logger.info("BOM for %s", bom_product.name)
            for bom_line in bom.bom_line_ids:                
                bom_line_bottles = bom_line.product_id.bottle_equivalent * bom_line.product_qty
                bottles += bom_line_bottles
                _logger.info("┣ ━ %s : %0.2f bottles * %0.2f = %0.2f", bom_line.product_id.name, bom_line.product_id.bottle_equivalent, bom_line.product_qty, bom_line_bottles)                
            bom_product.bottle_equivalent = bottles
            bom.product_tmpl_id._compute_bottle_equivalent()
            _logger.info("= %0.2f bottles", bottles)
                
                
