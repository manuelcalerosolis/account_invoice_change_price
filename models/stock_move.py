# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.addons import decimal_precision as dp
import logging

_logger = logging.getLogger(__name__)


class StockMove(models.Model):
    _inherit = "stock.move"

    cost_price = fields.Float('Previous Cost', digits=dp.get_precision('Product Price'))
    list_price = fields.Float('Sales Price', compute='_compute_list_price', store=False, digits=dp.get_precision('Product Price'))
    lst_price = fields.Float('Public Price', compute='_compute_list_price', store=False, digits=dp.get_precision('Product Price'))
    standard_price = fields.Float('Cost', compute='_compute_list_price', store=False, digits=dp.get_precision('Product Price'))

    @api.multi
    @api.depends('product_id')
    def _compute_list_price(self):
        for record in self:
            record.list_price = record.product_id.list_price
            record.list_price = record.product_id.lst_price
            record.standard_price = record.product_id.standard_price

        # list_price = fields.Float(
        #     'Sales Price', default=1.0,
        #     digits=dp.get_precision('Product Price'),
        #     help="Price at which the product is sold to customers.")
        # # lst_price: catalog price for template, but including extra for variants
        # lst_price = fields.Float(
        #     'Public Price', related='list_price', readonly=False,
        #     digits=dp.get_precision('Product Price'))
        # standard_price = fields.Float(
        #     'Cost', compute='_compute_standard_price',
        #     inverse='_set_standard_price', search='_search_standard_price',
        #     digits=dp.get_precision('Product Price'), groups="base.group_user",
        #     help="Cost used for stock valuation in standard price and as a first price to set in average/FIFO.")
        #
        # self.product_id.name

class Picking(models.Model):
    _inherit = "stock.picking"

    move_ids_cost_prices = fields.One2many('stock.move', 'picking_id', string="Stock moves cost prices")

    @api.multi
    def button_validate(self):
        _logger.info("**** Stock picking ****")

        for line in self.move_lines:
            _logger.info(line.product_id.standard_price)
            line.cost_price = line.product_id.standard_price

        _logger.info("*" * 80)

        super(Picking, self).button_validate()
