from odoo import api, fields, models, _
from odoo.exceptions import UserError


class PventMovement(models.Model):
    _name = "pvent.movement"
    _description = "Movimiento de inventario Pvent"
    _order = "movement_date desc, id desc"

    name = fields.Char(
        string="Referencia",
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: self.env[
            "ir.sequence"
        ].next_by_code("pvent.inventory.movement"),
    )

    movement_date = fields.Datetime(
        string="Fecha y hora",
        required=True,
        default=fields.Datetime.now,
    )

    movement_type = fields.Selection([
        ("receipt", "Entrada"),
        ("delivery", "Entrega"),
        ("transfer", "Traslado"),
        ("return", "Devolución"),
        ("installation", "Instalación"),
        ("damage", "Daño"),
        ("loss", "Pérdida"),
        ("archive", "Archivo / baja"),
    ], string="Tipo de movimiento", required=True)

    product_id = fields.Many2one(
        "product.product",
        string="Pieza",
        required=True,
        ondelete="restrict",
    )

    quantity = fields.Float(
        string="Cantidad",
        required=True,
        default=1.0,
    )

    uom_id = fields.Many2one(
        "uom.uom",
        string="Unidad",
        related="product_id.uom_id",
        readonly=True,
    )

    source_location_id = fields.Many2one(
        "stock.location",
        string="Ubicación origen",
        domain="[('usage', '=', 'internal')]",
    )

    destination_location_id = fields.Many2one(
        "stock.location",
        string="Ubicación destino",
        domain="[('usage', '=', 'internal')]",
    )

    project_id = fields.Many2one(
        "pvent.project",
        string="Proyecto / vehículo",
        ondelete="set null",
    )

    responsible_id = fields.Many2one(
        "res.users",
        string="Responsable",
        default=lambda self: self.env.user,
        required=True,
    )

    notes = fields.Text(
        string="Observaciones",
    )

    state = fields.Selection([
        ("draft", "Borrador"),
        ("confirmed", "Confirmado"),
    ], string="Estado", default="draft", required=True)

    confirmed_by = fields.Many2one(
        "res.users",
        string="Confirmado por",
        readonly=True,
    )

    confirmed_at = fields.Datetime(
        string="Fecha de confirmación",
        readonly=True,
    )

    reversal_of_id = fields.Many2one(
        "pvent.movement",
        string="Reversión de",
        readonly=True,
    )

    @api.constrains("quantity")
    def _check_quantity(self):
        for record in self:
            if record.quantity <= 0:
                raise UserError(
                    _("La cantidad debe ser mayor que cero.")
                )

    def action_confirm(self):
        for record in self:

            if record.state == "confirmed":
                continue

            product = record.product_id
            template = product.product_tmpl_id

            # Validaciones
            if record.movement_type in (
                "delivery",
                "installation",
                "transfer",
            ):
                if not record.source_location_id:
                    raise UserError(
                        _("Este movimiento requiere una ubicación de origen.")
                    )

            if record.movement_type in (
                "receipt",
                "return",
                "transfer",
            ):
                if not record.destination_location_id:
                    raise UserError(
                        _("Este movimiento requiere una ubicación de destino.")
                    )

            decreases_stock = record.movement_type in (
                "delivery",
                "installation",
                "damage",
                "loss",
                "archive",
            )

            increases_stock = record.movement_type in (
                "receipt",
                "return",
            )

            # Evitar inventario negativo
            if decreases_stock:
                if product.pvent_stock_qty < record.quantity:
                    raise UserError(
                        _(
                            "No hay suficiente inventario.\n"
                            "Disponible: %(available)s\n"
                            "Solicitado: %(requested)s"
                        )
                        % {
                            "available": product.pvent_stock_qty,
                            "requested": record.quantity,
                        }
                    )

                product.pvent_stock_qty -= record.quantity

            elif increases_stock:
                product.pvent_stock_qty += record.quantity

            # Traslado: no cambia cantidad
            elif record.movement_type == "transfer":
                template.pvent_location_id = (
                    record.destination_location_id.id
                )

            # Actualizar proyecto
            if record.project_id:
                template.pvent_project_id = record.project_id.id

            # Actualizar responsable
            template.pvent_responsible_id = record.responsible_id.id

            # Estado
            status_map = {
                "receipt": "available",
                "return": "available",
                "delivery": "assigned",
                "installation": "installed",
                "damage": "damaged",
                "loss": "lost",
                "archive": "archived",
            }

            if record.movement_type in status_map:
                template.pvent_status = status_map[
                    record.movement_type
                ]

            # Ubicación destino
            if record.destination_location_id:
                template.pvent_location_id = (
                    record.destination_location_id.id
                )

            record.write({
                "state": "confirmed",
                "confirmed_by": self.env.user.id,
                "confirmed_at": fields.Datetime.now(),
            })

        return True

    def action_reverse(self):
        for record in self:

            if record.state != "confirmed":
                raise UserError(
                    _("Solo se pueden revertir movimientos confirmados.")
                )

            if self.search_count([
                ("reversal_of_id", "=", record.id),
                ("state", "=", "confirmed"),
            ]):
                raise UserError(
                    _("Este movimiento ya fue revertido.")
                )

            reverse_type = {
                "receipt": "archive",
                "delivery": "return",
                "return": "delivery",
                "installation": "delivery",
                "damage": "receipt",
                "loss": "receipt",
                "archive": "receipt",
                "transfer": "transfer",
            }.get(record.movement_type)

            if not reverse_type:
                raise UserError(
                    _("No existe una reversión definida para este movimiento.")
                )

            reverse = self.create({
                "movement_type": reverse_type,
                "product_id": record.product_id.id,
                "quantity": record.quantity,
                "source_location_id": record.destination_location_id.id,
                "destination_location_id": record.source_location_id.id,
                "project_id": record.project_id.id,
                "responsible_id": self.env.user.id,
                "notes": _("Reversión del movimiento %s") % record.name,
                "reversal_of_id": record.id,
            })

            reverse.action_confirm()

        return True

    def unlink(self):
        raise UserError(
            _(
                "Los movimientos de inventario no se eliminan. "
                "Utilice una reversión o corrección."
            )
        )