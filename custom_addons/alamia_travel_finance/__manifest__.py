{
    'name': 'Alamia Travel Finance',
    'version': '1.0',
    'category': 'Travel OS',
    'summary': 'Accounting integration for Travel OS',
    'description': """
        Connects Travel Sales to standard Odoo Invoicing (account).
        Creates Customer Invoices and Vendor Bills automatically.
    """,
    'author': 'Ali Raza',
    'website': 'https://github.com/amrshah',
    
    'depends': ['alamia_travel_sales', 'account'],
    'data': [
        'views/travel_sale_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
