"""
基于规则的自然语言生成
"""
import re, random
from copy import deepcopy

def MB_to_GB(v):
    if v.upper().endswith('MB') or v.upper().endswith('M'):
        num = int(re.search(r'[\d]+', v).group())
        v = v if num<1024 else str(num//1024)+'GB'
    return v

def cl(nl):
    return '\n' if nl else ''

def is_code(s):
    return s.replace('+', '').isalnum()


no_prop = lambda e,p: '%s 套餐中不存在 %s 的信息，或不包含该内容'%(e, '、'.join(p))
kg_lack = lambda e,s: '知识图谱中暂缺 %s 的 %s'%(e, s)
info_inform = {
    '费用': '费用',
    '流量': '包含数据流量',
    '通话时长': '免费通话时长',
}
code_inform = lambda v:'发送短信代码"%s"到10086'%v
price_request = [
'请问您对套餐价格有什么要求吗？',
'请问您想要什么价位的套餐？',
'您希望了解什么价位的套餐呢？',
]
call_request = [
'您对套餐每月包含的免费通话时长有什么要求？',
'您需要包含多少分钟通话的套餐呢？']
flow_request = [
'您每个月需要多少数据流量？',
'您对月数据流量有什么要求吗？',
'您每个月需要多少流量上网呢？']
request_templ = {
    '费用':price_request,
    '通话时长':call_request,
    '流量':flow_request,
}
cant_find = [
'很抱歉，没有找到符合您要求的业务，请您重新描述对费用、包含流量、通话时长的要求',
'很抱歉，目前暂时没有符合您要求的业务，请放宽对费用、包含流量和通话时长的限制',]

saygoodbye = [
'感谢您的使用，再见！',
'欢迎您再次使用本系统，再见！'
]
sysintro = [
'我可以根据您对套餐价格、包含流量、通话时长的需求，帮您推荐套餐'
]
chatting = [
'您好，我是中国移动业务咨询机器人，可以帮助您进行套餐推荐或信息查询，请问您需要什么帮助吗？',
'抱歉，您说的这些我不太理解，但您如果需要办理套餐，我可以为您提供帮助的',
]

class CMCCRuleNLG(object):
    def __init__(self, brand='神州行', plantype='4G飞享套餐', number='18811369685'):
        self.ps_brand = brand
        self.ps_plantype = plantype
        self.ps_number = number

    def sys_act_to_nl(self, sys_act):
        """
        通过系统动作生成自然语言回复的主函数
        """
        sys_act = deepcopy(sys_act)
        act = sys_act.act
        entity = sys_act.entity

        nl = ''
        if '结束对话' in act:
            return random.choice(saygoodbye)
        if '重启对话' in act:
            return
        if '闲聊' in act:
            return random.choice(chatting)

        if sys_act.personal:
            nl += cl(nl)+ '正在为您查询个人信息'
            param = sys_act.act['告知']
            if '当前主套餐' in param:
                nl += '\n您的当前主套餐为：%s'%param.pop('当前主套餐')
                temp = '基本信息：'
                plan_info = param.pop('基本信息')
                for p in ['费用', '流量', '通话时长']:
                    if p in plan_info:
                        v = plan_info[p] if p != '流量' else MB_to_GB(plan_info[p])
                        temp += info_inform[p] + v + '，'
                nl += '\n' + temp[:-1]
            if '已办业务' in param:
                nl += '\n您目前开通的业务有：%s'%'、'.join(param.pop('已购业务'))
            if '停机' in param:
                if param.pop('停机') == '否':
                    nl += '\n您的号码%s停机情况：未停机'%self.ps_number
                else:
                    nl += '\n您的号码%s停机情况：已停机'%self.ps_number
            for s in ['客服密码', '详单账单']:
                if s in param:
                    nl += '\n%s：%s'%(s, param.pop(s))
            for s,v in param.items():
                nl += '\n您的%s为%s'%(s, v)
            return nl

        if '系统介绍' in act:
            nl += random.choice(sysintro)
            if '问询' in act:
                nl += '\n' + random.choice(request_templ[act['问询']])
            return nl

        if '找不到实体' in act:
            if act['找不到实体'] == '无法更换':
                return '除了 %s 没有其他符合要求的套餐了'%entity
            else :
                return random.choice(cant_find)

        if '确认' in act:
            param = act['确认']
            if not param:
                return '我没能理解您的意思，请重新描述您的需求'
            elif '套餐名称' in param and '问询属性' in param:
                if param['套餐名称'] and not param['问询属性']:
                    return '您是想了解 %s 套餐的什么信息呢？'%param['套餐名称']
                elif not param['套餐名称'] and param['问询属性']:
                    return '您是在询问哪个套餐/业务的%s呢？'%'、'.join(param['问询属性'])
                else:
                    return '我没能理解您的意思，请重新描述您的需求'
            elif '套餐名称' in param:
                return '请问您在问哪个套餐呢？'
            elif '问询属性' in param:
                return '我没能理解您的意思，请重新描述您的问题'
            else:
                raise ValueError('不存在的系统动作：'+str(param))

        if '告知' in act:
            param = act['告知']
            give_entity = False
            if not entity and not sys_act.only_parent:
                if not param:
                    raise ValueError('告知属性为空')
                else:
                    for rel, val in param.items():
                        nl += cl(nl) + '%s：\n%s'%(rel ,val)
            elif not param:
                if '找不到属性' not in act:
                    raise ValueError('告知bug：无参数')
                else:
                    nl += cl(nl) + no_prop(entity, act.pop('找不到属性'))
            else:
                if '介绍' in param:
                    give_entity = True
                    if sys_act.entity_way == 'KG':
                        nl += cl(nl) + '已为您找到满足要求的套餐：%s'%entity
                    elif sys_act.entity_way == 'mention':
                        if entity in ['全球通', '动感地带', '神州行']:
                            nl += cl(nl) + '找到号卡品牌：%s'%entity
                        else:
                            nl += cl(nl) + '找到套餐：%s'%entity
                    elif sys_act.entity_way == 'inherit':
                        nl += cl(nl) + '套餐：%s'%entity

                    intro = param.pop('介绍')
                    if not intro:
                        nl += cl(nl) + kg_lack(entity, '介绍')
                    elif '介绍' in intro:
                        nl += cl(nl) + intro
                    else:
                        nl += cl(nl) + '介绍：' + intro
                temp = []
                for p in ['费用', '流量', '通话时长']:
                    if p in param:
                        v = param.pop(p) if p != '流量' else MB_to_GB(param.pop(p))
                        temp.append(info_inform[p] + v)
                if temp:
                    ent = entity if not give_entity else ''
                    nl += cl(nl)+ ent+'基本信息：' + '，'.join(temp)

                if '开通方式' in param:
                    method = param.pop('开通方式')
                    if not method:
                        nl += cl(nl) + kg_lack(entity, '开通方式')
                    else:
                        method = code_inform(method) if is_code(method) else method
                        if not give_entity:
                            nl += cl(nl) + entity + '开通方式：' + method
                            give_entity = True
                        else:
                            nl += cl(nl) + '开通方式：' + method
                    if '互斥业务' in param:
                        if self.ps_plantype in param.get('互斥业务', []):
                            nl += cl(nl) + '提示：您的已有套餐"%s"和"%s"互斥，开通时会将"%s"替换为"%s"'\
                                %(self.ps_plantype, entity, self.ps_plantype, entity)
                        param.pop('互斥业务')

                flag = False
                for s in ['办理限制', '适用品牌', '能否办理']:
                    if s in param:
                        brands = param.pop(s)
                        if not flag:
                            give_entity = True
                            if self.ps_brand not in brands:
                                nl += cl(nl) + '%s 仅限号卡品牌为%s的用户办理，您的号卡品牌为%s，无法办理' \
                                                    %(entity, '、'.join(brands), self.ps_brand)
                                flag = True
                            else:
                                nl += cl(nl) + '%s 仅限号卡品牌为%s的用户办理，您的号卡品牌为%s，可以办理' \
                                                    %(entity, '、'.join(brands), self.ps_brand)
                                flag = True
                if param:
                    if not give_entity:
                        nl += cl(nl) + '%s 信息查询'%entity
                    for s, v in param.items():
                        if v is None:
                            nl += cl(nl) + kg_lack(entity, s)
                        else:
                            nl += cl(nl) + '%s：%s'%(s,v)
        if '找不到属性' in act:
            nl += cl(nl) + no_prop(entity, act['找不到属性'])

        if '问询更多' in act:
            nl += cl(nl) + '您还需要查询其他信息吗？'

        if '问询档位' in act:
            nl += cl(nl) + '档位越高套餐资源越丰富，请您选择套餐价位'

        if '问询' in act:
            param = act['问询']
            nl = ''
            if param == '费用':
                nl += cl(nl) + random.choice(price_request)
            elif param == '通话时长':
                nl += cl(nl) + random.choice(call_request)
            elif param == '流量':
                nl += cl(nl) + random.choice(flow_request)

        return nl
