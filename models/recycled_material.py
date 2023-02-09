from odoo import api, fields, models
from odoo.exceptions import UserError

class RecycledMaterialCategory(models.Model):
    _name = 'jt.recycled.material'
    _description = 'Recycled material'

    # pet is 1380 kg/m3 ... a 1.5L pet bottle weighs 33g, so 43 bottles in a kg

    name = fields.Char('Name', required=True)
    density = fields.Float(string="Density", required=True)
    density_uom_name = fields.Char(string='Density unit of measure label', compute='_compute_density_uom_name')
    bottles_per_kg = fields.Float(string="Bottles per kg", help="100%% recylced would be about 43 bottles", required=True)
    percentage_recycled_material = fields.Float('Percentage recycled material (reference only)')

    def _compute_density_uom_name(self):
        self.density_uom_name = self._get_density_uom_id_from_ir_config_parameter().name

    @api.model
    def _get_density_uom_id_from_ir_config_parameter(self):
        density_in_kg_cubic_meters = self.env['ir.config_parameter'].sudo().get_param('jt_product_repeat.density_in_kg_cubic_meters')
        pipo = self.env.ref('jt_product_repeat.product_uom_kg_cubic_meter')
        if density_in_kg_cubic_meters == '1':
            return self.env.ref('jt_product_repeat.product_uom_kg_cubic_meter')
        else:
            # What the heck ... there is no alternative
            return self.env.ref('jt_product_repeat.product_uom_kg_cubic_meter')

    
    def calculate_pet_bottles_equivalent(self, volume):
        if volume < 0.0:
            raise UserError("Volme cannot be negative: %s", kg)
        
        self.ensure_one()
        kg = volume * self.density
        bottles = kg * self.bottles_per_kg        
        return bottles



    