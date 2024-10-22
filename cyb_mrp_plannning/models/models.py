# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from odoo import fields, models


class MrpWorkorder(models.Model):
    _inherit = 'mrp.workorder'
    
    
    def button_finish(self):
        end_date = datetime.now()
        for workorder in self:
            if workorder.state in ('done', 'cancel'):
                continue
            workorder.end_all()
            vals = {
                'qty_produced': workorder.qty_produced or workorder.qty_producing or workorder.qty_production,
                'state': 'done',
                'date_finished': end_date,
                'date_planned_finished': end_date,
                'costs_hour': workorder.workcenter_id.costs_hour
            }
            if not workorder.date_start:
                vals['date_start'] = end_date
            if not workorder.date_planned_start or end_date < workorder.date_planned_start:
                vals['date_planned_start'] = end_date
            workorder.with_context(bypass_duration_calculation=True).write(vals)
            work_order_ids = workorder.production_id.workorder_ids.ids
            index = work_order_ids.index(workorder.id)
            next_line = int(index) + 1
            next_line_id = work_order_ids[next_line] if next_line < len(work_order_ids) else None
            if next_line_id :
                next_line_id_obj = self.browse(int(next_line_id))
                start_date = fields.datetime.now() + timedelta(minutes=10)
                planned_end_date = workorder._calculate_date_planned_finished(date_planned_start=start_date)
                next_line_id_obj.write({
                    'date_planned_start' : start_date,
                    'date_planned_finished' :planned_end_date
                })
        return True

