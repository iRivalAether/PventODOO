{
    'name': 'Pvent Inventory',
    'version': '20.0.1.0.0',
    'category': 'Inventory',
    'summary': 'Inventario y trazabilidad para Pvent',
    'author': 'Pvent',
    'license': 'LGPL-3',

    'depends': [
        'stock',
        'product',
    ],

    'data': [
        'security/pvent_inventory_groups.xml',
        'security/ir.access.csv',

        'views/product_views.xml',
        'views/project_views.xml',
        'views/movement_views.xml',
        'views/menu.xml',

    ],

    'installable': True,
    'application': True,
}