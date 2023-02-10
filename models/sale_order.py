import logging
from odoo import api, fields, models

_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = "sale.order"

    bottle_equivalent = fields.Float(compute='_compute_bottle_equivalent', string='Bottle Equivalent', store=True)

    @api.depends('order_line', 'order_line.product_id', 'order_line.product_template_id', 'order_line.product_uom_qty')
    def _compute_bottle_equivalent(self):

        for order in self:
            bottles = 0.0
            _logger.info("┌────────")
            for line in order.order_line:
                product_bottles = line.product_id.bottle_equivalent
                line_bottles = product_bottles * line.product_uom_qty
                bottles += line_bottles
                _logger.info("├─ %s: %0.2f bottles", line.product_id.name, line_bottles)
            _logger.info("└─> SO order %s:  %0.2f bottles", order.name, bottles)
            order.bottle_equivalent = bottles
