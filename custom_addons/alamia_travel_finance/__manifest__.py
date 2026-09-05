{
    'name': 'Alamia Travel Finance',
    'version': '19.0.1.0.0',
    'category': 'Travel OS',
    'summary': 'Accounting integration & Partner Settlements for Travel OS',
    'description': """
        Connects Travel Sales to standard Odoo Invoicing (account).
        Creates Customer Invoices, Vendor Bills, and Partner Settlements.
    """,
    'author': 'Ali Raza',
    'website': 'https://github.com/amrshah',
    'depends': ['alamia_travel_sales', 'account'],
    'data': [
        'security/ir.model.access.csv',
        'views/travel_sale_views.xml',
        'views/travel_partner_settlement_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
