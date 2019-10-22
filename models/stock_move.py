# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError

import logging

_logger = logging.getLogger(__name__)


class StockMove(models.Model):
    _inherit = "stock.move"

    previous_cost_price = fields.Float('Previous Cost', digits=dp.get_precision('Product Price'))
    current_cost_price = fields.Float('Current Cost', digits=dp.get_precision('Product Price'))


class Picking(models.Model):
    _inherit = "stock.picking"

    move_ids_cost_prices = fields.One2many('stock.move', 'picking_id', string="Stock moves cost prices")

    @api.multi
    def button_validate(self):
        for line in self.move_lines:
            line.previous_cost_price = line.product_id.standard_price

        result = super(Picking, self).button_validate()

        for line in self.move_lines:
            line.current_cost_price = line.product_id.standard_price

        return result

    @api.multi
    def action_open_picking_prices(self):
        self.ensure_one()
        if self.state != 'done':
            raise UserError(_('The selected picking does not have validated yet. Please validate the picking.'))
            return

        view = self.env.ref('account_invoice_change_price.select_sale_price_form')

        return {'name': _('Picking Prices'),
                'view_type': 'form',
                'view_mode': 'form',
                'target': 'new',
                'res_model': 'select.sale.price',
                'view_id': view.id,
                'views': [(view.id, 'form')],
                'type': 'ir.actions.act_window',
                'context': {'default_picking_id': self.id}}
