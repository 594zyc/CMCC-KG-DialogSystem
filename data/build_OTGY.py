import json
with open('raw_data.json', encoding='utf8') as f:
    data = json.load(f)

user_acts = set()
names = set()
requestable_attrs = set()
informable_attrs = set()
values = set()

for task_id, item in data.items():
    user_acts.add(item['user_act'])
    if '主语' in item:
        names.add(item['主语'])
    if '问询属性' in item:
        for r in item['问询属性']:
            requestable_attrs.add(r)
    if '告知属性' in item:
        informable_attrs.add(item['告知属性'])
    if '宾语' in item:
        values.add(item['宾语'])

output_file = {
    'name': list(names),
    'user_acts': list(user_acts),
    'requestable_attrs':list(requestable_attrs),
    'informable_attrs': list(informable_attrs),
    'values': list(values)
}


with open('CMCC_OTGY.json', 'w', encoding='utf-8') as f:
    json.dump(output_file, f, ensure_ascii=False, indent=2)