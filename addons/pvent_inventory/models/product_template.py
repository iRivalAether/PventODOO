from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    pvent_internal_code = fields.Char(
        string='Identificador interno',
        readonly=True,
        copy=False,
        index=True
    )

    pvent_part_number = fields.Char(
        string='Número de parte'
    )

    pvent_short_name = fields.Char(
        string='Nombre corto'
    )

    pvent_quantity = fields.Float(
        string='Cantidad',
        default=0
    )

    pvent_unit = fields.Char(
        string='Unidad',
        default='Unidad'
    )

    pvent_entry_date = fields.Date(
        string='Fecha de entrada'
    )

    pvent_location = fields.Selection(
        [
            ('warehouse', 'Almacén central'),
            ('reception', 'Área de recepción'),
            ('rack', 'Rack y sección'),
            ('workshop_1', 'Taller 1: tapicería'),
            ('workshop_2', 'Taller 2: mecánica y hojalatería'),
            ('worker', 'Entregada a trabajador'),
            ('vehicle', 'Instalada en vehículo'),
            ('not_located', 'No localizada'),
            ('archive', 'Archivo o baja'),
        ],
        string='Ubicación'
    )

    pvent_workshop = fields.Selection(
        [
            ('warehouse', 'Almacén central'),
            ('workshop_1', 'Taller 1: tapicería'),
            ('workshop_2', 'Taller 2: mecánica y hojalatería'),
        ],
        string='Taller actual'
    )

    pvent_status = fields.Selection(
        [
            ('available', 'Disponible'),
            ('assigned', 'Asignada'),
            ('delivered', 'Entregada'),
            ('installed', 'Instalada'),
            ('damaged', 'Dañada'),
            ('lost', 'Perdida'),
            ('located', 'Localizada'),
            ('discarded', 'Desechada'),
            ('archived', 'Archivada'),
        ],
        string='Estado',
        default='available'
    )

    pvent_review_status = fields.Selection(
        [
            ('pending', 'Pendiente'),
            ('reviewed', 'Revisada'),
        ],
        string='Estado de revisión',
        default='pending'
    )

    pvent_responsible_id = fields.Many2one(
        'res.users',
        string='Responsable actual'
    )

    pvent_project_id = fields.Many2one(
        'pvent.project',
        string='Proyecto'
    )

    pvent_supplier = fields.Char(
        string='Proveedor / lugar de compra'
    )

    pvent_purchase_url = fields.Char(
        string='Enlace de compra'
    )

    pvent_unit_price = fields.Float(
        string='Precio unitario'
    )

    pvent_customer_cost = fields.Float(
        string='Costo para cliente'
    )

    pvent_description = fields.Text(
        string='Descripción'
    )

    pvent_observations = fields.Text(
        string='Observaciones'
    )

    pvent_admin_notes = fields.Text(
        string='Notas administrativas'
    )

    @api.model
    def create(self, vals):

        if not vals.get('pvent_internal_code'):
            vals['pvent_internal_code'] = self.env['ir.sequence'].next_by_code(
                'pvent.inventory.piece'
            ) or 'PVENT-00001'

        return super().create(vals)