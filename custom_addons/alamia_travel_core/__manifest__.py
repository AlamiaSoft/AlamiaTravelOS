{
    'name': 'Alamia Travel Core',
    'version': '19.0.1.0.0',
    'category': 'Travel',
    'summary': 'Core definitions for Alamia Travel OS',
    'description': """
        Provides the foundational master data and security models for Alamia Travel OS.
        Includes Service Catalogs, customized Partner logic, and standard user roles.
    """,
    'author': 'Ali Raza',
    'website': 'https://github.com/amrshah',
    'depends': ['base', 'contacts', 'account'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/users_data.xml',
        'views/menus.xml',
        'views/service_catalog_views.xml',
        'views/res_partner_views.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
