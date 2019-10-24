import re
import xlrd, json
import pprint

QAs = {
    r'(流量包?)(都?有)(多少|什么)(钱|档)': {
    'question': '流量包都有多少钱的？',
    'answer': '有100/200/300/400/500共5档，分别包含x/xx/xxx/xxxx/xxxxx G流量',
    },
    r'(充值).*(优惠)': {
    'question': '充值现在有优惠吗？',
    'answer': '用支付宝/微信支付半价',
    },
    r'(通话)(可以|能)?(在香港)(可以|能)?(用)': {
    'question': '这些通话可以在香港用嘛',
    'answer': '不能，在港澳台正常收取国际漫游费用',
    },
    r'(流量)(可以|能)?(在香港)(可以|能)?(用)': {
    'question': '流量可以在香港用嘛',
    'answer': '不能，港澳台流量需要办理港澳台三地流量包',
    },
    r'(我)?[想要能]?(什么是|介绍|了解)(一下)?(家庭多终端)': {
    'question': '家庭多终端服务是什么服务？',
    'answer': '家庭多终端是xxxxxxxx(定义)',
    },
    r'(家庭多终端)(的)?(是什么|是啥|介绍|定义)': {
    'question': '家庭多终端服务是什么服务？',
    'answer': '家庭多终端是xxxxxxxx(定义)',
    },
    r'(我)?[想要能]?(什么是|介绍|了解)(一下)?(WLAN)': {
    'question': '什么是WLAN',
    'answer': 'WLAN是xxxxxxxx(定义)',
    },
    r'(WLAN)(的)?(是什么|是啥|介绍|定义)': {
    'question': '什么是WLAN',
    'answer': 'WLAN是xxxxxxxx(定义)',
    },
    r'(我)?[想要能]?(什么是|介绍|了解)(一下)?(号卡服务)': {
    'question': '什么是WLAN',
    'answer': 'WLAN是xxxxxxxx(定义)',
    },
    r'(号卡服务)(的)?(是什么|是啥|介绍|定义)': {
    'question': '什么是WLAN',
    'answer': 'WLAN是xxxxxxxx(定义)',
    },
}

[
# '家庭多终端服务是什么服务？'
# 'WLAN是什么服务'
]
answers = [
'有100/200/300/400/500共5档，分别包含x/xx/xxx/xxxx/xxxxx G流量',
'用支付宝/微信支付半价',
'不能，在港澳台正常收取国际漫游费用',
'不能，港澳台流量需要办理港澳台三地流量包'
]

def reverse(matched):
    findstr = matched.group("select"); #123
    findstr = re.sub(r'\[\?', '(', findstr)
    findstr = re.sub(r'\]', ')?', findstr)
    return findstr

QAid = len(QAs)+1
excel_dir = './场景123标准问题北京171010.xlsx'
data = xlrd.open_workbook(excel_dir)
for table_name in [ '场景1', '场景2', '场景3']:
    table = data.sheet_by_name(table_name)  # 通过名称获取
    nrows = table.nrows
    tmpl_col = 12
    q_col = 13
    a_col = 14

    for i in range(1, nrows):
        row_values = table.row_values(i)
        tmpls = row_values[tmpl_col]
        tmpls = re.sub(r'(?P<select>\[\?([\w\u4e00-\u9fa5]+\|)*[\w\u4e00-\u9fa5]+\])', reverse, tmpls)
        tmpls = re.sub(r'\?\]', ')?', tmpls)
        tmpls = re.sub(r'\[', '(', tmpls)
        tmpls = re.sub(r'\]', ')', tmpls)
        Q = row_values[q_col]
        A = row_values[a_col]
        for idx, tmpl in enumerate(tmpls.split('<<')):
            if idx==0 and tmpl in QAs or not tmpl:
                print(table_name+" %s："%i, tmpl)
                continue
            QAs[tmpl] = {}
            QAs[tmpl]['question'] = Q
            QAs[tmpl]['answer'] = A

jsObj = json.dumps(QAs, ensure_ascii=False, indent=4)

fileObject = open('QAs.json', 'w')
fileObject.write(jsObj)
fileObject.close()

# pprint.pprint(q_templates)
# pprint.pprint(questions)
# pprint.pprint(answers)

# print(len(questions)==len(q_templates))
# print(len(questions)==len(answers))






