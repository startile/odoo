# -*- coding: utf-8 -*-
# from odoo import http


# class CybMrpOrderButton(http.Controller):
#     @http.route('/cyb_mrp_order_button/cyb_mrp_order_button', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/cyb_mrp_order_button/cyb_mrp_order_button/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('cyb_mrp_order_button.listing', {
#             'root': '/cyb_mrp_order_button/cyb_mrp_order_button',
#             'objects': http.request.env['cyb_mrp_order_button.cyb_mrp_order_button'].search([]),
#         })

#     @http.route('/cyb_mrp_order_button/cyb_mrp_order_button/objects/<model("cyb_mrp_order_button.cyb_mrp_order_button"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('cyb_mrp_order_button.object', {
#             'object': obj
#         })
