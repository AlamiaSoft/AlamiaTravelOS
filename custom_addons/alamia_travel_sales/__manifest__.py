{
    'name': 'Alamia Travel Sales',
    'version': '1.0',
    'category': 'Travel OS',
    'summary': 'Core operational sales engine for travel agencies',
    'description': """
        Provides the Sale model to record customer transactions, 
        services booked, supplier costs, and calculate gross profit.
    """,
    'author': 'Ali Raza',
    'website': 'https://github.com/amrshah',
    
    'depends': ['alamia_travel_core', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/travel_sale_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
