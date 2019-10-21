# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models, api
from odoo.addons import decimal_precision as dp

import logging

_logger = logging.getLogger(__name__)


class SelectSalePrice(models.TransientModel):
    _name = 'select.sale.price'
    _description = 'Select Sale Price Wizard'

    picking_id = fields.Many2one('stock.picking', 'Stock Picking')
    price_line_ids = fields.One2many('select.sale.price.line', 'sale_id')

    @api.model
    def default_get(self, default_fields):
        result = super(SelectSalePrice, self).default_get(default_fields)
        if self._context.get('default_picking_id') is not None:
            result['picking_id'] = self._context.get('default_picking_id')
        return result

    @api.onchange('picking_id')
    def _onchange_picking_id(self):
        data = []
        self.price_line_ids = [(6, 0, [])]
        for line in self.picking_id.move_line_ids:
            data.append((0, False, self.get_dict_line(line)))
        self.price_line_ids = data

    def get_dict_line(self, line):
        sale_price_line = {'product_id': line.product_id,
                           'previous_cost_price': line.move_id.previous_cost_price,
                           'current_cost_price': line.move_id.current_cost_price,
                           'purchase_price': line.move_id.purchase_line_id.price_unit,
                           'cost_price': line.product_id.standard_price,
                           'standard_price': line.product_id.standard_price}

        search = self.get_search_last_purchase(line.product_id)
        if search:
            sale_price_line.update({'previous_purchase_date': search.create_date})
            sale_price_line.update({'previous_purchase_price': search.purchase_line_id.price_unit})

        return sale_price_line

    def get_search_last_purchase(self, product_id):
        return self.env['stock.move'].search(
            [['product_id', '=', product_id.id], ['picking_id', '<>', self.picking_id.id]], limit=1,
            order='date desc')

    @api.multi
    def action_select_sale_price(self):
        for line in self.price_line_ids.filtered(lambda r: r.selected):
            line.product_id.standard_price = line.standard_price


class SelectSalePriceLine(models.TransientModel):
    _name = 'select.sale.price.line'
    _description = 'Select Sale Price Line Wizard'

    sale_id = fields.Many2one('select.sale.price')
    selected = fields.Boolean(string='Selected', default=True, help='Indicate this line is coming to change')
    product_id = fields.Many2one('product.product', string='Product', required=True)
    previous_purchase_date = fields.Datetime('Previous Purchase Date', required=False)
    previous_purchase_price = fields.Float('Previous Purchase Price', digits=dp.get_precision('Product Price'))
    previous_cost_price = fields.Float('Previous Cost', digits=dp.get_precision('Product Price'))
    current_cost_price = fields.Float('Current Cost', digits=dp.get_precision('Product Price'))
    purchase_price = fields.Float('Purchase Price', digits=dp.get_precision('Product Price'))
    cost_price = fields.Float('Cost Price', digits=dp.get_precision('Product Price'))
    standard_price = fields.Float('Standard Price', digits=dp.get_precision('Product Price'))

    @api.onchange('standard_price')
    def _onchange_standard_price(self):
        self.selected = True

