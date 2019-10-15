# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError

import logging

_logger = logging.getLogger(__name__)


class StockMove(models.Model):
    _inherit = "stock.move"

    previous_cost_price = fields.Float('Previous Cost', digits=dp.get_precision('Product Price'))

    list_price = fields.Float('Sales Price', compute='_compute_list_price', store=False, digits=dp.get_precision('Product Price'))
    lst_price = fields.Float('Public Price', compute='_compute_list_price', store=False, digits=dp.get_precision('Product Price'))
    standard_price = fields.Float('Cost', compute='_compute_list_price', store=False, digits=dp.get_precision('Product Price'))

    @api.multi
    @api.depends('product_id')
    def _compute_list_price(self):
        for record in self:
            record.list_price = record.product_id.list_price
            record.lst_price = record.product_id.lst_price
            record.standard_price = record.product_id.standard_price

    def get_search_last_purchase(self, picking_id):
        return self.search([['product_id', '=', self.product_id.id], ['picking_id', '<>', picking_id]], limit=1,
                           order='date desc')


class Picking(models.Model):
    _inherit = "stock.picking"

    move_ids_cost_prices = fields.One2many('stock.move', 'picking_id', string="Stock moves cost prices")

    @api.multi
    def button_validate(self):
        for line in self.move_lines:
            search = line.get_search_last_purchase(self.id)
            if search:
                line.previous_purchase_date = search.create_date
                line.previous_purchase_price = search.purchase_line_id.price_unit
            line.previous_cost_price = line.product_id.standard_price
            line.purchase_price = line.move_id.purchase_line_id.price_unit

        super(Picking, self).button_validate()

        for line in self.move_lines:
            line.cost_price = line.product_id.standard_price

    @api.multi
    def action_open_picking_prices(self):
        self.ensure_one()
        _logger.info(self.state)
        if self.state != 'done':
            raise UserError(_('The selected picking does not have validated yet. Please validate the picking and retry '))
            return

        view = self.env.ref('account_invoice_change_price.view_picking_price_form_inherit')

        action = {'name': _('Picking Prices'),
                  'view_type': 'form',
                  'view_mode': 'tree',
                  'res_model': 'stock.picking',
                  'view_id': view.id,
                  'views': [(view.id, 'form')],
                  'type': 'ir.actions.act_window',
                  'context': {'default_picking_id': self.id}}

        return action
