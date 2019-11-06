# -*- coding: utf-8 -*-

# Copyright 2019 Manuel Calero
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
#
# docker-compose run web --test-enable --stop-after-init -d test_db -i account_invoice_change_price
#

from odoo.tests import common, datetime
from odoo.tests import Form

import logging


class TestPickingChangePrice(common.TransactionCase):

    def setUp(self):
        super(TestPickingChangePrice, self).setUp()

        self.categ_average = self.env['product.category'].create({
            'name': 'Average',
            'property_cost_method': 'average'})

        self.product_a = self.env['product.product'].create({
            'name': 'Product A',
            'type': 'product',
            'default_code': 'prda',
            'standard_price': 10.0,
            'categ_id': self.categ_average.id
        })

        self.partner = self.env['res.partner'].create({
            'name': 'Vendor A'
        })

        self.uom_unit = self.env.ref('uom.product_uom_unit')

        self.price_list_eur = self.env['product.pricelist'].create({
            'name': 'EUR',
            'currency_id': self.env.ref('base.EUR').id
        })

        self.currency = self.env['res.currency'].search([('name', '=', 'EUR')])

    def test_previous_and_current_price_after_two_purchase_order(self):
        purchase_order_1 = self.env['purchase.order'].create({
            'partner_id': self.partner.id,
            'currency_id': self.currency.id,
            'order_line': [
                (0, 0, {
                    'name': self.product_a.name,
                    'product_id': self.product_a.id,
                    'product_qty': 10.0,
                    'product_uom': self.product_a.uom_po_id.id,
                    'price_unit': 20.0,
                    'date_planned': datetime.today(),
                }),
            ],
        })

        purchase_order_1.button_confirm()
        purchase_order_1.action_view_picking()

        picking_1 = purchase_order_1.picking_ids[0]

        move_line_1 = picking_1.move_lines[0]
        move_line_1.quantity_done = 10

        picking_1.button_validate()

        self.assertEqual(move_line_1.previous_cost_price, 10.0)
        self.assertEqual(move_line_1.price_unit, 20.0)
        self.assertEqual(move_line_1.current_cost_price, 20.0)
        self.assertEqual(self.product_a.standard_price, 20.0)

        purchase_order_2 = self.env['purchase.order'].create({
            'partner_id': self.partner.id,
            'currency_id': self.currency.id,
            'order_line': [
                (0, 0, {
                    'name': self.product_a.name,
                    'product_id': self.product_a.id,
                    'product_qty': 10.0,
                    'product_uom': self.product_a.uom_po_id.id,
                    'price_unit': 30.0,
                    'date_planned': datetime.today(),
                }),
            ],
        })

        purchase_order_2.button_confirm()
        purchase_order_2.action_view_picking()

        picking_2 = purchase_order_2.picking_ids[0]

        move_line_2 = picking_2.move_lines[0]
        move_line_2.quantity_done = 10

        picking_2.button_validate()

        self.assertEqual(move_line_2.previous_cost_price, 20.0)
        self.assertEqual(move_line_2.price_unit, 30.0)
        self.assertEqual(move_line_2.current_cost_price, 25.0)
        self.assertEqual(self.product_a.standard_price, 25.0)
