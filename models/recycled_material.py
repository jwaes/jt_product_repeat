import logging
from odoo import api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


# pet is 1380 kg/m3 ... a 1.5L pet bottle weighs 33g, so 43 bottles in a kg
PET_BOTTLES_PER_KG = 43

class RecycledMaterialCategory(models.Model):
    _name = 'jt.recycled.material'
    _description = 'Recycled material'


    name = fields.Char('Name', required=True)
    density = fields.Float(string="Density", required=True)
    density_uom_name = fields.Char(string='Density unit of measure label', compute='_compute_density_uom_name')
    bottles_per_kg = fields.Float(string="Bottles per kg", help="100%% recylced would be about 43 bottles", default=PET_BOTTLES_PER_KG)

    percentage_recycled_material = fields.Float(compute='_compute_precentage_recycled_material', inverse='_inverse_precentage_recycled_material', string='Precentage Recycled Material')
    
    product_template_ids = fields.One2many('product.template', 'recycled_material_id', string='Product Templates')
    product_template_count = fields.Integer(compute='_compute_product_template_count', string='# Products')
    
    @api.depends('product_template_ids')
    def _compute_product_template_count(self):
        for rm in self:
            rm.product_template_count = len(rm.product_template_ids)

    @api.depends('bottles_per_kg')
    def _compute_precentage_recycled_material(self):
        self.percentage_recycled_material = self.bottles_per_kg / PET_BOTTLES_PER_KG

    def _inverse_precentage_recycled_material(self):
        self.bottles_per_kg = PET_BOTTLES_PER_KG * self.percentage_recycled_material

    def _compute_density_uom_name(self):
        self.density_uom_name = self._get_density_uom_id_from_ir_config_parameter().name

    @api.model
    def _get_density_uom_id_from_ir_config_parameter(self):
        density_in_kg_cubic_meters = self.env['ir.config_parameter'].sudo().get_param('jt_product_repeat.density_in_kg_cubic_meters')
        if density_in_kg_cubic_meters == '1':
            return self.env.ref('jt_product_repeat.product_uom_kg_cubic_meter')
        else:
            # What the heck ... there is no alternative
            return self.env.ref('jt_product_repeat.product_uom_kg_cubic_meter')

    @api.depends('percentage_recycled_material')
    def _calculate_bottles_per_kg_from_percentage(self):
        self.ensure_one()
        self.bottles_per_kg = PET_BOTTLES_PER_KG * self.percentage_recycled_material
    
    def calculate_pet_bottles_equivalent(self, volume):
        if volume < 0.0:
            raise UserError("Volme cannot be negative: %s", kg)
        
        self.ensure_one()
        kg = volume * self.density
        bottles = kg * self.bottles_per_kg        
        return bottles

    def calculate_weight(self, volume):
        weight = volume * self.density
        # _logger.info("Weight: %0.2f * %0.2f = %0.2f", volume, self.density, weight)
        return weight

    def open_recycled_material_products(self):
        self.ensure_one()
        return {
            'name': 'Products',
            'res_model': 'product.template',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            # 'views': [(self.env.ref('jt_mrp_housing.housing_batch_view_tree').id, 'tree'), (False, 'form')],
            'context': {
                'recycled_material_id': self.id,
            },
            'domain': [
                ['recycled_material_id', '=', self.id],
            ],   
         
        }        


    