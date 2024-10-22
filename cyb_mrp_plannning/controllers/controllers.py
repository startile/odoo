# -*- coding: utf-8 -*-
# from odoo import http


# class CybMrpPlannning(http.Controller):
#     @http.route('/cyb_mrp_plannning/cyb_mrp_plannning', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/cyb_mrp_plannning/cyb_mrp_plannning/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('cyb_mrp_plannning.listing', {
#             'root': '/cyb_mrp_plannning/cyb_mrp_plannning',
#             'objects': http.request.env['cyb_mrp_plannning.cyb_mrp_plannning'].search([]),
#         })

#     @http.route('/cyb_mrp_plannning/cyb_mrp_plannning/objects/<model("cyb_mrp_plannning.cyb_mrp_plannning"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('cyb_mrp_plannning.object', {
#             'object': obj
#         })
