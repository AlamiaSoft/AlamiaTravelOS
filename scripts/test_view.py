v_id = env.ref('alamia_travel_finance.view_travel_sub_agent_kanban').id
res = env['res.partner'].get_views([(v_id, 'kanban')])
print('--- VIEW ARCH ---')
print(res['views']['kanban']['arch'])
print('--- FIELDS IN VIEW ---')
print(list(res['views']['kanban']['fields'].keys()))
