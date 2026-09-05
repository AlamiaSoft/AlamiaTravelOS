{
    'name': 'Alamia Travel Reporting',
    'version': '19.0.1.0.0',
    'category': 'Travel OS',
    'summary': 'Dashboards and Reports for Travel OS',
    'description': """
        Provides role-specific executive and operational dashboards
        for CEO, Operations Director, Sales Director, and Assistant Operations/Marketing.
        Includes interactive OWL widgets, KPI metrics, charts, and financial analytics.
    """,
    'author': 'Ali Raza',
    'website': 'https://github.com/amrshah',
    'depends': ['alamia_travel_sales', 'alamia_travel_finance'],
    'data': [
        'views/reporting_views.xml',
        'views/dashboard_actions.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'alamia_travel_reporting/static/src/scss/travel_dashboard.scss',
            'alamia_travel_reporting/static/src/xml/travel_dashboard.xml',
            'alamia_travel_reporting/static/src/js/travel_dashboard.js',
        ],
    },
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
