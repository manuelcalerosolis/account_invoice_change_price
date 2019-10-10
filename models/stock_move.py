# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.addons import decimal_precision as dp
import logging

_logger = logging.getLogger(__name__)


class StockMove(models.Model):
    _inherit = "stock.move"

    cost_price = fields.Float('Cost', digits=dp.get_precision('Product Price'))


class Picking(models.Model):
    _inherit = "stock.picking"

    move_ids_cost_prices = fields.One2many('stock.move', 'picking_id', string="Stock moves cost prices",
                                           domain=['|', ('package_level_id', '=', False),
                                                   ('picking_type_entire_packs', '=', False)])

    @api.multi
    def button_validate(self):
        _logger.info("**** Stock picking ****")

        for line in self.move_lines:
            _logger.info(line.product_id.standard_price)
            line.cost_price = line.product_id.standard_price

        _logger.info("*" * 80)

        super(Picking, self).button_validate()
