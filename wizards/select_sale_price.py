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
        logging.info("ya he creado las lineas")
        data = []
        self.price_line_ids = [(6, 0, [])]
        for line in self.picking_id.move_line_ids:
            data.append((0, False, self.get_dict_line(line)))
        self.price_line_ids = data

    def get_dict_line(self, line):
        sale_price_line = {'product_id': line.product_id,
                           'previous_cost_price': line.move_id.previous_cost_price,
                           'purchase_price': line.move_id.purchase_line_id.price_unit,
                           'cost_price': line.product_id.standard_price,
                           'list_price': line.product_id.list_price,
                           'eur_price': 0,
                           'usd_price': 0}

        search = self.get_search_last_purchase(line.product_id)
        if search:
            sale_price_line.update({'previous_purchase_date': search.create_date})
            sale_price_line.update({'previous_purchase_price': search.purchase_line_id.price_unit})

        for price_list_item in line.product_id.pricelist_item_ids:
            if price_list_item.pricelist_id.name == 'Tarifa pública':
                sale_price_line.update({'eur_price': price_list_item.fixed_price})

            if price_list_item.pricelist_id.name == 'Tarifa privada':
                sale_price_line.update({'usd_price': price_list_item.fixed_price})

        return sale_price_line

    def get_search_last_purchase(self, product_id):
        return self.env['stock.move'].search(
            [['product_id', '=', product_id.id], ['picking_id', '<>', self.picking_id.id]], limit=1,
            order='date desc')

    @api.multi
    def action_select_sale_price(self):
        # logging.info("+"*80)
        for line in self.price_line_ids.filtered(lambda r: r.selected):
            line.product_id.list_price = line.list_price

            for price_list_item in line.product_id.pricelist_item_ids:
                # logging.info(price_list_item.pricelist_id.name)
                if price_list_item.pricelist_id.name == 'Tarifa pública':
                    # logging.info("eur_price")
                    # logging.info(line.eur_price)
                    # logging.info(price_list_item.pricelist_id.id)
                    price_list_item.fixed_price = line.eur_price

                if price_list_item.pricelist_id.name == 'Tarifa privada':
                    # logging.info("usd_price")
                    # logging.info(line.usd_price)
                    # logging.info(price_list_item.pricelist_id.id)
                    price_list_item.fixed_price = line.usd_price


class SelectSalePriceLine(models.TransientModel):
    _name = 'select.sale.price.line'
    _description = 'Select Sale Price Line Wizard'

    sale_id = fields.Many2one('select.sale.price')
    selected = fields.Boolean(string='Selected', default=True, help='Indicate this line is coming to change')
    product_id = fields.Many2one('product.product', string='Product', required=True)
    previous_purchase_date = fields.Datetime('Previous Purchase Date', required=False)
    previous_purchase_price = fields.Float('Previous Purchase Price', digits=dp.get_precision('Product Price'))
    previous_cost_price = fields.Float('Previous Cost', digits=dp.get_precision('Product Price'))
    current_cost_price = fields.Float('Current Cost', compute='_compute_current_cost_price')
    purchase_price = fields.Float('Purchase Price', digits=dp.get_precision('Product Price'))
    cost_price = fields.Float('Cost Price', digits=dp.get_precision('Product Price'))
    list_price = fields.Float('List Price', digits=dp.get_precision('Product Price'))
    eur_price = fields.Float('EUR Price', digits=dp.get_precision('Product Price'))
    usd_price = fields.Float('USD Price', digits=dp.get_precision('Product Price'))

    @api.onchange('standard_price', 'eur_price', 'usd_price')
    def _onchange_standard_price(self):
        self.selected = True

    @api.multi
    def _compute_current_cost_price(self):
        for line in self:
            self.current_cost_price = self.product_id.standard_price

