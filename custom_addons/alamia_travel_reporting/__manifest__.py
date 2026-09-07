{
    'name': 'Alamia Travel Reporting',
    'version': '19.0.1.0.0',
    'category': 'Travel OS',
    'summary': 'Dashboards, Reports, and Alamia Travels AI Copilot UI',
    'description': """
        Provides role-specific executive and operational dashboards
        for CEO, Operations Director, Sales Director, and Assistant Operations/Marketing.
        Includes interactive OWL widgets, KPI metrics, charts, financial analytics,
        and the Alamia Travels AI Employee Copilot UI.
    """,
    'author': 'Ali Raza',
    'website': 'https://github.com/amrshah',
    'depends': ['alamia_travel_sales', 'alamia_travel_finance'],
    'data': [
        'views/reporting_views.xml',
        'views/dashboard_actions.xml',
        'views/copilot_actions.xml',
        'views/res_config_settings_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'alamia_travel_reporting/static/src/scss/travel_dashboard.scss',
            'alamia_travel_reporting/static/src/xml/travel_dashboard.xml',
            'alamia_travel_reporting/static/src/js/travel_dashboard.js',
            'alamia_travel_reporting/static/src/scss/alamia_ai_copilot.scss',
            'alamia_travel_reporting/static/src/xml/alamia_ai_copilot.xml',
            'alamia_travel_reporting/static/src/js/alamia_ai_copilot.js',
        ],
    },
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
