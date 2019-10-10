# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class SelectSalePrice(models.TransientModel):
    _name = 'select.sale.price'
    _description = 'Select Sale Price Wizard'

    product_id = fields.Many2one('product.product', 'Product', readonly=True)
