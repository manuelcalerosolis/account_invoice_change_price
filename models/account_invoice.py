# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.addons import decimal_precision as dp
import logging


_logger = logging.getLogger(__name__)


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    price_old = fields.Float(string='Old Price', required=True, digits=dp.get_precision('Product Price'))

    def action_show_wizard(self):
        self.ensure_one()

        _logger.info("@"*80)
        _logger.info(self.id)
        _logger.info("@"*80)

        # if self.picking_id.picking_type_id.show_reserved:
        #     view = self.env.ref('stock.view_stock_move_operations')
        # else:
        #     view = self.env.ref('stock.view_stock_move_nosuggest_operations')
        #
        # picking_type_id = self.picking_type_id or self.picking_id.picking_type_id
        # return {
        #     'name': _('Detailed Operations'),
        #     'type': 'ir.actions.act_window',
        #     'view_type': 'form',
        #     'view_mode': 'form',
        #     'res_model': 'stock.move',
        #     'views': [(view.id, 'form')],
        #     'view_id': view.id,
        #     'target': 'new',
        #     'res_id': self.id,
        #     'context': dict(
        #         self.env.context,
        #         show_lots_m2o=self.has_tracking != 'none' and (
        #                     picking_type_id.use_existing_lots or self.state == 'done' or self.origin_returned_move_id.id),
        #         # able to create lots, whatever the value of ` use_create_lots`.
        #         show_lots_text=self.has_tracking != 'none' and picking_type_id.use_create_lots and not picking_type_id.use_existing_lots and self.state != 'done' and not self.origin_returned_move_id.id,
        #         show_source_location=self.location_id.child_ids and self.picking_type_id.code != 'incoming',
        #         show_destination_location=self.location_dest_id.child_ids and self.picking_type_id.code != 'outgoing',
        #         show_package=not self.location_id.usage == 'supplier',
        #         show_reserved_quantity=self.state != 'done'
        #     ),
        # }


