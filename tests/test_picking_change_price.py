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
            'categ_id': self.categ_average.id
        })

        self.product_b = self.env['product.product'].create({
            'name': 'Product B',
            'type': 'product',
            'default_code': 'prdb',
            'categ_id': self.categ_average.id
        })

        self.product_c = self.env['product.product'].create({
            'name': 'Product C',
            'type': 'product',
            'default_code': 'prdc',
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

        self.purchase_order_1 = self.env['purchase.order'].create({
            'partner_id': self.partner.id,
            'currency_id': self.currency.id,
            'order_line': [
                (0, 0, {
                    'name': self.product_a.name,
                    'product_id': self.product_a.id,
                    'product_qty': 1.0,
                    'product_uom': self.product_a.uom_po_id.id,
                    'price_unit': 100.0,
                    'date_planned': datetime.today(),
                }),
                (0, 0, {
                    'name': self.product_b.name,
                    'product_id': self.product_b.id,
                    'product_qty': 1.0,
                    'product_uom': self.product_b.uom_po_id.id,
                    'price_unit': 200.0,
                    'date_planned': datetime.today(),
                }),
                (0, 0, {
                    'name': self.product_c.name,
                    'product_id': self.product_c.id,
                    'product_qty': 1.0,
                    'product_uom': self.product_c.uom_po_id.id,
                    'price_unit': 300.0,
                    'date_planned': datetime.today(),
                }),
            ],
        })

    def test_product_created(self):
        """ This method test that product A, B and C was created.
        """
        self.assertEqual(self.product_a.name, 'Product A')
        self.assertEqual(self.product_b.name, 'Product B')
        self.assertEqual(self.product_c.name, 'Product C')

        self.assertEqual(self.purchase_order_1.partner_id, self.partner)
