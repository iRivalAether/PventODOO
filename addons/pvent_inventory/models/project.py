from odoo import models, fields


class PventProject(models.Model):

    _name = 'pvent.project'
    _description = 'Proyecto de vehículo Pvent'
    _order = 'name'

    name = fields.Char(
        string='Vehículo / Proyecto',
        required=True
    )

    owner = fields.Char(
        string='Propietario / Cliente'
    )

    description = fields.Text(
        string='Descripción'
    )

    observations = fields.Text(
        string='Observaciones'
    )

    image = fields.Image(
        string='Fotografía'
    )

    piece_ids = fields.One2many(
        'product.template',
        'pvent_project_id',
        string='Piezas'
    )

    movement_ids = fields.One2many(
        'pvent.movement',
        'project_id',
        string='Historial'
    )