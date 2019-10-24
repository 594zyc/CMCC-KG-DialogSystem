"""
201905清华中移动客服对话系统第二次语料
预处理脚本，整理为对话数据
"""

import xlrd, json
from collections import defaultdict

data_file = 'data.xlsx'
task_file = 'tasks.xlsx'

collect_data = {}

with xlrd.open_workbook(data_file) as f:
    table = f.sheet_by_name('问询')
    for row in range(1, table.nrows):
        idx = table.cell(row,1).value
        if idx not in collect_data:
            collect_data[int(idx)] = []
            for i in [5,6,7,3]:
                tmp = table.cell_value(row, i)
                if tmp != '/':
                    collect_data[int(idx)].append(tmp)
        else:
            collect_data[int(idx)].append(table.cell_value(row, 3))
    table = f.sheet_by_name('告知')
    for row in range(1, table.nrows):
        idx = table.cell(row, 1).value
        if idx not in collect_data:
            collect_data[int(idx)] = []
            for i in [3,4,5,10]:
                tmp = table.cell_value(row, i)
                if tmp != '/':
                    collect_data[int(idx)].append(tmp)
        else:
            collect_data[int(idx)].append(table.cell_value(row, 10))


output_file = {}
header = ['任务id', '任务种类', '任务数量', '条数/用户', '任务要求', '任务说明', '对话历史']
import re
with xlrd.open_workbook(task_file) as f:
    table = f.sheet_by_name('问询')
    for row in range(1, table.nrows):
        tmp = table.cell(row, header.index('任务id')).value
        if not tmp:
            break
        idx = int(tmp)
        output_file[idx] = {}
        output_file[idx]['user_act'] = '问询'
        output_file[idx]['领域'] = '套餐流量'
        task_desc = table.cell(row, header.index('任务要求')).value
        if re.match(r'向系统询问信息："(.+)"的"(.+)"', task_desc):
            m = re.match(r'向系统询问信息："(.+)"的"(.+)"', task_desc)
            subject, requestable = m.groups()
            output_file[idx]['主语'] = subject
            output_file[idx]['问询属性'] = requestable.split('""')
        elif re.match(r'向系统询问该套餐的："(.+)"', task_desc):
            m = re.match(r'向系统询问该套餐的："(.+)"', task_desc)
            requestable = m.groups()[0]
            output_file[idx]['问询属性'] = requestable.split('""')
        elif re.match(r'向系统询问个人信息："(.+)"', task_desc):
            m = re.match(r'向系统询问个人信息："(.+)"', task_desc)
            requestable = m.groups()[0]
            output_file[idx]['领域'] = '个人'
            output_file[idx]['问询属性'] = requestable.split('""')
        else:
            pass
        output_file[idx]['对话历史'] = table.cell(row, header.index('对话历史')).value


    table = f.sheet_by_name('告知')
    for row in range(1, table.nrows):
        tmp = table.cell(row, header.index('任务id')).value
        if not tmp:
            break
        idx = int(tmp)
        output_file[idx] = {}
        output_file[idx]['user_act'] = '告知'
        output_file[idx]['领域'] = '套餐流量'
        task_desc = table.cell(row, header.index('任务种类')).value
        m = re.match(r'^告知\((.+)=(.+)\)', task_desc)
        informable, object = m.groups()
        if '价格' in informable:
            output_file[idx]['告知属性'] = '费用'
            output_file[idx]['宾语'] = object
        elif '流量' in informable:
            output_file[idx]['告知属性'] = '流量'
            output_file[idx]['宾语'] = object
        else:
            output_file[idx]['告知属性'] = '通话时长'
            output_file[idx]['宾语'] = object
        output_file[idx]['对话历史'] = table.cell(row, header.index('对话历史')).value

    table = f.sheet_by_name('其他')
    for row in range(1, table.nrows):
        tmp = table.cell(row, header.index('任务id')).value
        if not tmp:
            break
        idx = int(tmp)
        output_file[idx] = {}
        output_file[idx]['领域'] = '套餐流量'
        user_act = table.cell(row, header.index('任务种类')).value
        output_file[idx]['user_act'] = user_act
        output_file[idx]['对话历史'] = table.cell(row, header.index('对话历史')).value

for k in output_file:
    output_file[k]['data'] = collect_data[k]

with open('raw_data.json', 'w', encoding='utf-8') as f:
    json.dump(output_file, f, indent=2, ensure_ascii=False)

ctt = 0
hit = 0
for k, data in output_file.items():
    for d in data['data']:
        ctt += 1
        if '主语' in data and data['主语'] not in d:
            print(data['主语'], d)
            hit += 1
print(hit / ctt)

### 套餐名称 98% 都是原名
### 个别例子见下
# 畅享卡 -->   畅行卡， 畅想卡
# 畅享卡年包卡 -> 畅想卡年包卡, 畅享卡包年卡, 畅享卡年包
# 畅享卡双月卡 -> 畅想双月卡, 畅享双月卡, 畅享的双月卡, 畅想卡双月卡
# 畅享卡郊区版 -> 畅享郊区卡, 畅享卡郊区板, 畅享卡郊区, 郊区畅销卡, 畅想卡郊区版, 畅享卡的郊区版, 郊区版, 畅享卡郊区卡
# 彩信套餐 -> 彩信
# 4G流量卡 -> 4G卡, 4g流量卡, 4G 流量卡, 4G流量档位, 4g流量卡套餐
# 4G彩信包 -> 4g彩信包
# 畅游包  -> 畅享包, 畅流包, 畅留包, 畅游包, 畅邮包
# 4G流量加油包 -> 4G流量套餐加油包, 4G流量包, 4G加油包, 4g流量包, 4g流量加油包
# 和4G套餐 -> 和4g, 和4g套餐
# 4G飞享套餐 -> 4G分享套餐, 4g飞享套餐, 4g 飞享套餐, 4G飞享
# 全球通畅享套餐 -> 全球畅享套餐, 全球通畅想套餐, 全球畅想套餐, 全球通套餐,  全球通畅销套餐, 全球畅享套餐
# 全球通无限尊享计划套餐 -> 全球无限通尊享计划套餐, 全球通的无限尊享计划套餐, 全球通无限尊享计划, 全球通无限尊享, 全球通无线尊享计划, 全球通无限尊享套餐
# 畅享套餐 -> 畅想套餐, 畅销套餐, 畅享流量









