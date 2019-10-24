'''
划分数据集：训练集，测试集, 比例 3:1
'''
import json
with open('raw_data.json', encoding='utf8') as f:
    data = json.load(f)

from collections import defaultdict
import random

ratio = 4
# user_act
act_data = defaultdict(list)
total_data = 0
for idx in data:
    act_data[data[idx]["user_act"]].extend(data[idx]["data"])
    total_data += len(data[idx]["data"])
print('total_data:', total_data)

for k in act_data:
    random.shuffle(act_data[k])
with open('traning_data_act.json', 'w', encoding='utf8') as f:
    training_data = defaultdict(list)
    for k in act_data:
        training_data[k] = act_data[k][len(act_data[k])//ratio:]
    json.dump(training_data, f, ensure_ascii=False, indent=2)

with open('test_data_act.json', 'w', encoding='utf8') as f:
    test_data = defaultdict(list)
    for k in act_data:
        test_data[k] = act_data[k][:len(act_data[k])//ratio]
    json.dump(test_data, f, ensure_ascii=False, indent=2)

# 三元组中的 属性
attr_data = defaultdict(list)
test_attr_data = []
for idx in data:
    data_len = len(data[idx]["data"])
    random.shuffle(data[idx]["data"])
    if "属性" in data[idx]:
        if isinstance(data[idx]["属性"], list):
            for r in data[idx]["属性"]:
                attr_data[r].extend(data[idx]["data"][data_len//ratio:])
        else:
            attr_data[data[idx]["属性"]].extend(data[idx]["data"][data_len//ratio:])
        for d in data[idx]["data"][:data_len//ratio]:
            test_attr_data.append([d, data[idx]["属性"]])
    else:
        attr_data["无"].extend(data[idx]["data"][data_len//ratio:])
        for d in data[idx]["data"][:data_len//ratio]:
            test_attr_data.append([d, []])
print('total attrs:', len(attr_data))

for k in attr_data:
    random.shuffle(attr_data[k])
with open('traning_data_attr.json', 'w', encoding='utf8') as f:
    json.dump(attr_data, f, ensure_ascii=False, indent=2)

with open('test_data_attr.json', 'w', encoding='utf8') as f:
    json.dump(test_attr_data, f, ensure_ascii=False, indent=2)

# 三元组中的 值
value_data = defaultdict(list)
test_value_data = []
for idx in data:
    data_len = len(data[idx]["data"])
    random.shuffle(data[idx]["data"])
    if "宾语" in data[idx]:
        for d in data[idx]["data"][data_len//ratio:]:
            if data[idx]["宾语"] in ['低','少']:
                value_data['少'].append(d)
            elif data[idx]['宾语'] in ['中']:
                value_data['中'].append(d)
            elif data[idx]['宾语'] in ['高', '多']:
                value_data['多'].append(d)
            elif data[idx]['宾语'] in ['更多', '更高']:
                value_data['更多'].append(d)
            elif data[idx]['宾语'] in ['更少', '更低']:
                value_data['更少'].append(d)
            else:
                value_data['任意'].append(d)

        for d in data[idx]["data"][:data_len//ratio]:
            if data[idx]["宾语"] in ['低','少']:
                test_value_data.append([d, '少'])
            elif data[idx]['宾语'] in ['中']:
                test_value_data.append([d, '中'])
            elif data[idx]['宾语'] in ['高', '多']:
                test_value_data.append([d, '多'])
            elif data[idx]['宾语'] in ['更多', '更高']:
                test_value_data.append([d, '更多'])
            elif data[idx]['宾语'] in ['更少', '更低']:
                test_value_data.append([d, '更少'])
            else:
                test_value_data.append([d, '任意'])

for k in value_data:
    random.shuffle(value_data[k])
with open('training_data_value.json', 'w', encoding='utf8') as f:
    json.dump(value_data, f, ensure_ascii=False, indent=2)

with open('test_data_value.json', 'w', encoding='utf8') as f:
    json.dump(test_value_data, f, ensure_ascii=False, indent=2)


