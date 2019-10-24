# -*- coding: UTF-8 -*-
"""
数值描述型的informable attrs 预测
"""
import re

Num_re = re.compile(r"(?P<thousand>[一二两三四五六七八九]+千)?"
                    r"(?P<hundred>[一二两三四五六七八九]+百)?零?"
                    r"(?P<ten>[一二三四五六七八九]+十)?零?"
                    r"(?P<one>[一二两三四五六七八九]*)")
# 费用模板
cost_re1 = re.compile(r"(?P<Num1>[0-9一二两三四五六七八九十百千]+)(?:多)?(?:元钱|元|块钱|块)?"
                      r"[-到和至、~](?P<Num2>[0-9一二两三四五六七八九十百千]+)(?:多)?(?:元钱|元|块钱|块)?")
cost_re2 = re.compile(r"(?P<Num1>[0-9一二两三四五六七八九十百千]+)"
                     r"(?:多)?(?:元钱|元|块钱|块)?(?P<Scope1>以上|以内|之内|之外|以外|以下|内|之下)"
                      r"(?P<Num2>[0-9一二两三四五六七八九十百千]+)"
                      r"(?:多)?(?:元钱|元|块钱|块)?(?P<Scope2>以上|以内|之内|之外|以外|以下|内|之下)")
cost_re3 = re.compile(r"(?P<MostLeast>至少|至多|最少|最多|最低|最高|"
                      r"(?:不要|不能|不可以|别|不|莫)?(?:超过|低于|高于|少于|多于|大于|小于))?"
                      r"(?:了|消费)?(?P<Num>[0-9一二两三四五六七八九十百千]+)"
                     r"(?:多)?(?:元钱|元|块钱|块)?(?P<Scope>以上|以内|之内|之外|以外|以下|内|之下)?(?:[^起点些个下Gg兆Mm分小]|$)")
# 通话时长模板
time_re1 = re.compile(r"(?P<Num1>[0-9一二两三四五六time七八九十百千]+)(?:多个|多|个)?(?P<Metric1>分钟|小时|分|时|min|h)?"
                      r"[-到和至、~](?P<Num2>[0-9一二两三四五六七八九十百千]+)(?:多个|多|个)?(?P<Metric2>分钟|小时|分|时|min|h)")
time_re2 = re.compile(r"(?P<Num1>[0-9一二两三四五六七八九十百千]+)"
                     r"(?:多个|多|个)?(?P<Metric1>分钟|小时|分|时|min|h)(?P<Scope1>以上|以内|之内|之外|以外|以下|内|之下)"
                      r"(?P<Num2>[0-9一二两三四五六七八九十百千]+)"
                      r"(?:多个|多|个)?(?P<Metric2>分钟|小时|分|时|min|h)(?P<Scope2>以上|以内|之内|之外|以外|以下|内|之下)")
time_re3 = re.compile(r"(?P<MostLeast>至少|至多|最少|最多|最低|最高|"
                      r"(?:不要|不能|不可以|别|不|莫)?(?:超过|低于|高于|少于|多于|大于|小于))?"
                      r"(?:时间|分钟数|分钟|打电话|通话|包打|包|打|主叫)?(?P<Num>[0-9一二两三四五六七八九十百千]+)"
                     r"(?:多个|多|个)?(?P<Metric>通话分钟|分钟|小时|分|时|min|h)(?P<Scope>以上|以内|之内|之外|以外|以下|内|之下)?")
# 流量模板
data_re1 = re.compile(r"(?P<Num1>[0-9一二两三四五六time七八九十百千]+)(?:多个|多|个)?(?P<Metric1>MB|GB|gb|mb|M|G|兆|m|g)?"
                      r"[-到和至、~](?P<Num2>[0-9一二两三四五六七八九十百千]+)(?:多个|多|个)?(?P<Metric2>MB|GB|gb|mb|M|G|兆|m|g)")
data_re2 = re.compile(r"(?P<Num1>[0-9一二两三四五六七八九十百千]+)"
                     r"(?:多个|多|个)?(?P<Metric1>MB|GB|gb|mb|M|G|兆|m|g)(?P<Scope1>以上|以内|之内|之外|以外|以下|内|之下)"
                      r"(?P<Num2>[0-9一二两三四五六七八九十百千]+)"
                      r"(?:多个|多|个)?(?P<Metric2>MB|GB|gb|mb|M|G|兆|m|g)(?P<Scope2>以上|以内|之内|之外|以外|以下|内|之下)")
data_re3 = re.compile(r"(?P<MostLeast>至少|至多|最少|最多|最低|最高|"
                      r"(?:不要|不能|不可以|别|不|莫)?(?:超过|低于|高于|少于|多于|大于|小于))?"
                      r"(?:流量|能有|包含|包流量|包|含|)?(?P<Num>[0-9一二两三四五六七八九十百千]+)"
                     r"(?:多个|个多|多|个)?(?P<Metric>MB|GB|gb|mb|M|G|兆|m|g)(?P<Scope>以上|以内|之内|之外|以外|以下|内|之下)?")

# # 开通天数模板， 目前暂不作为 informable slots
# days_re = re.compile(r"(?P<MostLeast>至少|至多|最少|最多|最低|最高|"
#                       r"(?:不要|不能|不可以|别|不|莫)?(?:超过|低于|高于|少于|多于|大于|小于))?"
#                       r"(?:流量|能有|包含|包流量|包|含|)?(?P<Num>[0-9一二两三四五六七八九十百千]+)"
#                      r"(?:多个|多|个)?(?P<Metric>MB|GB|gb|mb|M|G|兆|m|g)(?P<Scope>以上|以内|之内|之外|以外|以下|内|之下)?")

def Chinese2num(sent):
    """
    中文数字转英文数字，七八十，五百五，八十八，一千零五，一千五，一千零五十， 一千五百
    :param sent: 中文数字串
    :return: int list
    """
    if sent == "十":
        return [10]
    elif sent == "百":
        return [100]
    else:
        number = dict(zip("零一二两三四五六七八九",[0,1,2,2,3,4,5,6,7,8,9]))
        sent = re.sub(r"千([一二三四五六七八九])([^百]|$)", "千\g<1>百\g<2>", sent)
        sent = re.sub(r"百([一二三四五六七八九])([^十]|$)", "百\g<1>十\g<2>", sent)
        sent = re.sub(r"0", "零", sent)
        sent = re.sub(r"1", "一", sent)
        sent = re.sub(r"2", "二", sent)
        sent = re.sub(r"3", "三", sent)
        sent = re.sub(r"4", "四", sent)
        sent = re.sub(r"5", "五", sent)
        sent = re.sub(r"6", "六", sent)
        sent = re.sub(r"7", "七", sent)
        sent = re.sub(r"8", "八", sent)
        sent = re.sub(r"9", "九", sent)


        Nums = Num_re.findall(sent)
        num_list = []
        for num in Nums:
            if num[0]=="" and num[1]=="" and \
                num[2] == "" and num[3] == "":
                continue
            tmp = 0
            if len(num[0].rstrip('千'))>1:
                for ch in num[0].rstrip('千'):
                    num_list.append(number[ch]*1000)
            elif len(num[0].rstrip('千')) == 1:
                tmp += number[num[0].rstrip('千')]*1000
            if len(num[1].rstrip('百'))>1:
                for ch in num[1].rstrip('百'):
                    num_list.append(number[ch]*100)
            elif len(num[1].rstrip('百'))==1:
                tmp += number[num[1].rstrip('百')]*100
            if len(num[2].rstrip('十'))>1:
                for ch in num[2].rstrip('十'):
                    num_list.append(number[ch]*10)
            elif len(num[2].rstrip('十'))==1:
                tmp += number[num[2].rstrip('十')]*10
            if len(num[3])>1:
                for ch in num[3]:
                    num_list.append(number[ch])
            elif len(num[3])==1:
                tmp += number[num[3]]
            if tmp !=0:
                num_list.append(tmp)
        return num_list

def Cost_match(user_utter):
    """
    输入用户句子 ，输出匹配到的功能费范围， 否则返回None
    """
    user_utter = re.sub(r'\d+元档', '', user_utter)
    user_utter = re.sub(r"([一二两三四五六七八九]+)([到至][一二两三四五六七八九]+)([百十])", "\g<1>\g<3>\g<2>\g<3>", user_utter)
    if cost_re1.search(user_utter):
        data = cost_re1.search(user_utter)
        # print('re1:', data)
        num_list = []
        try:
            num1 = int(data.group("Num1"))
        except Exception as e:
            num1 = Chinese2num(data.group("Num1"))[0]
        try:
            num2 = int(data.group("Num2"))
        except Exception as e:
            num2 = Chinese2num(data.group("Num2"))[0]

        for num in [num1, num2]:
            num_list.append(num)
        num_list = sorted(list(set(num_list)))
        if len(num_list) >= 1:
            return num_list[0], num_list[-1]
        else:
            return None
    elif cost_re2.search(user_utter):
        num_list=[]
        data = cost_re2.search(user_utter)
        # print('re2:', data)
        try:
            num1 = int(data.group("Num1"))
        except Exception as e:
            num1 = Chinese2num(data.group("Num1"))[0]
        try:
            num2 = int(data.group("Num2"))
        except Exception as e:
            num2 = Chinese2num(data.group("Num2"))[0]

        for num in [num1, num2]:
            num_list.append(num)
        num_list = sorted(list(set(num_list)))
        if len(num_list) >= 1:
            return num_list[0], num_list[-1]
        else:
            return None
    elif cost_re3.search(user_utter):
        num_list = []
        for data in cost_re3.findall(user_utter):
            # print('re3:',data)
            num = data[1]
            try:
                num_list.append(int(num))
            except Exception as e:
                if sum(Chinese2num(num)) > 10:
                    num_list.extend(Chinese2num(num))
            scope = data[2]
            mostleast = data[0]

        if len(num_list) == 1:
            if re.match(r"至少|最少|最低|高于|超过|多于|大于|((不要|不能|不可以|别|不|莫)(低于|少于|小于))", mostleast):
                num_list.append(1e8)
            if re.match(r"至多|最多|最高|低于|少于|小于|((不要|不能|不可以|别|不|莫)(超过|高于|多于|大于))", mostleast):
                num_list.append(0)
            if re.match(r"以内|之内|以下|内|之下", scope):
                num_list.append(0)
            if re.match(r"以上|之外|以外", scope):
                num_list.append(1e8)
        num_list = sorted(list(set(num_list)))
        if len(num_list) >= 1:
            return num_list[0], num_list[-1]
        else:
            return None

def Time_match(user_utter):
    """
    输入用户句子 ，输出匹配到的通话时长范围， 否则返回None
    还返回去除掉 通话时间匹配span 的句子，因为 功能费 有时不带单位，剔除比较好
    """
    user_utter = re.sub(r"([一二两三四五六七八九]+)([到至][一二两三四五六七八九]+)([百十])", "\g<1>\g<3>\g<2>\g<3>", user_utter)
    user_utter = re.sub(r"钟头","小时",user_utter)
    if time_re1.search(user_utter):
        data = time_re1.search(user_utter)
        user_utter = time_re1.sub("",user_utter)
        # print('re1:', data)
        num_list = []
        if data.group("Metric2") == "小时" or data.group("Metric2") == "时" or data.group("Metric2") == "h":
            metric2 = 60
        else:
            metric2 = 1
        if data.group("Metric1") == "小时" or data.group("Metric1") == "时" or data.group("Metric1") == "h":
            metric1 = 60
        elif data.group("Metric1") == None:
            metric1 = metric2
        else:
            metric1 = 1
        try:
            num1 = int(data.group("Num1"))
        except Exception as e:
            num1 = Chinese2num(data.group("Num1"))[0]
        try:
            num2 = int(data.group("Num2"))
        except Exception as e:
            num2 = Chinese2num(data.group("Num2"))[0]

        for num,metric in [num1,metric1],[num2, metric2]:
            num_list.append(num*metric)
        num_list = sorted(list(set(num_list)))

        if len(num_list) >= 1:
            return num_list[0], num_list[-1], user_utter
        else:
            return None
    elif time_re2.search(user_utter):
        num_list = []
        data = time_re2.search(user_utter)
        user_utter = time_re2.sub("",user_utter)
        # print('re2:', data)
        if data.group("Metric2") == "小时" or data.group("Metric2") == "时" or data.group("Metric2") == "h":
            metric2 = 60
        else:
            metric2 = 1
        if data.group("Metric1") == "小时" or data.group("Metric1") == "时" or data.group("Metric1") == "h":
            metric1 = 60
        elif data.group("Metric1") == None:
            metric1 = metric2
        else:
            metric1 = 1
        try:
            num1 = int(data.group("Num1"))
        except Exception as e:
            num1 = Chinese2num(data.group("Num1"))[0]
        try:
            num2 = int(data.group("Num2"))
        except Exception as e:
            num2 = Chinese2num(data.group("Num2"))[0]

        for num,metric in [num1,metric1],[num2, metric2]:
            num_list.append(num*metric)
        num_list = sorted(list(set(num_list)))
        if len(num_list) >= 1:
            return num_list[0], num_list[-1], user_utter
        else:
            return None
    elif time_re3.search(user_utter):
        num_list = []
        for data in time_re3.findall(user_utter):
            # print('re3:', data)
            num = data[1]
            metric = data[2]
            if metric == "小时" or metric == "时" or metric == "h":
                metric = 60
            else:
                metric = 1
            try:
                num_list.append(int(num)*metric)
            except Exception as e:
                num_list.extend([i*metric for i in Chinese2num(num)])
            scope = data[3]
            mostleast = data[0]
            if re.match(r"至少|最少|最低|高于|超过|多于|大于|((不要|不能|不可以|别|不|莫)(低于|少于|小于))", mostleast):
                num_list.append(1e8)
            if re.match(r"至多|最多|最高|低于|少于|小于|((不要|不能|不可以|别|不|莫)(超过|高于|多于|大于))", mostleast):
                num_list.append(0)
            if re.match(r"以内|之内|以下|内|之下", scope):
                num_list.append(0)
            if re.match(r"以上|之外|以外", scope):
                num_list.append(1e8)
        newsent = time_re3.sub("", user_utter)
        num_list = sorted(list(set(num_list)))
        if len(num_list) >= 1:
            return num_list[0], num_list[-1], newsent
        else:
            return None

def Data_match(user_utter):
    """
    输入用户句子 ，输出匹配到的流量范围， 否则返回None
    """
    user_utter = re.sub(r'4[Gg]彩信', '', user_utter)
    user_utter = re.sub(r'4[Gg][飞分]享', '', user_utter)
    user_utter = re.sub(r'和4[Gg]', '', user_utter)
    user_utter = re.sub(r'4[Gg]流量', '', user_utter)

    user_utter = re.sub(r"([一二两三四五六七八九]+)([到至][一二两三四五六七八九]+)([百十])", "\g<1>\g<3>\g<2>\g<3>", user_utter)
    if data_re1.search(user_utter):
        data = data_re1.search(user_utter)
        user_utter = data_re1.sub("", user_utter)
        # print('re1:', data.groups())
        num_list = []
        if data.group("Metric2") != None and re.match(r"(GB|G|gb|g)", data.group("Metric2")):
            metric2 = 1024
        else:
            metric2 = 1
        if data.group("Metric1") != None and re.match(r"(GB|G|gb|g)", data.group("Metric1")):
            metric1 = 1024
        elif data.group("Metric1") == None:
            metric1 = metric2
        else:
            metric1 = 1
        try:
            num1 = int(data.group("Num1"))
        except Exception as e:
            num1 = Chinese2num(data.group("Num1"))[0]
        try:
            num2 = int(data.group("Num2"))
        except Exception as e:
            num2 = Chinese2num(data.group("Num2"))[0]

        for num, metric in [num1, metric1], [num2, metric2]:
            num_list.append(num * metric)
        num_list = sorted(list(set(num_list)))

        if len(num_list) >= 1:
            return num_list[0], num_list[-1], user_utter
        else:
            return None
    elif data_re2.search(user_utter):
        num_list = []
        data = data_re2.search(user_utter)
        user_utter = data_re2.sub("", user_utter)
        # print('re2:', data)
        if data.group("Metric2") != None and re.match(r"GB|G|gb|g", data.group("Metric2")):
            metric2 = 1024
        else:
            metric2 = 1
        if data.group("Metric1") != None and re.match(r"GB|G|gb|g", data.group("Metric1")):
            metric1 = 1024
        elif data.group("Metric1") == None:
            metric1 = metric2
        else:
            metric1 = 1
        try:
            num1 = int(data.group("Num1"))
        except Exception as e:
            num1 = Chinese2num(data.group("Num1"))[0]
        try:
            num2 = int(data.group("Num2"))
        except Exception as e:
            num2 = Chinese2num(data.group("Num2"))[0]

        for num, metric in [num1, metric1], [num2, metric2]:
            num_list.append(num * metric)
        num_list = sorted(list(set(num_list)))
        if len(num_list) >= 1:
            return num_list[0], num_list[-1], user_utter
        else:
            return None
    elif data_re3.search(user_utter):
        num_list = []
        for data in data_re3.findall(user_utter):
            # print('re3:', data)
            num = data[1]
            metric = data[2]
            if metric != None and re.match(r"GB|G|gb|g", metric):
                metric = 1024
            else:
                metric = 1
            try:
                num_list.append(int(num) * metric)
            except Exception as e:
                num_list.extend([i * metric for i in Chinese2num(num)])
            scope = data[3]
            mostleast = data[0]
            if re.match(r"至少|最少|最低|高于|超过|多于|大于|((不要|不能|不可以|别|不|莫)(低于|少于|小于))", mostleast):
                num_list.append(1e8)
            if re.match(r"至多|最多|最高|低于|少于|小于|((不要|不能|不可以|别|不|莫)(超过|高于|多于|大于))", mostleast):
                num_list.append(0)
            if re.match(r"以内|之内|以下|内|之下", scope):
                num_list.append(0)
            if re.match(r"以上|之外|以外", scope):
                num_list.append(1e8)
        newsent = data_re3.sub("", user_utter)
        num_list = sorted(list(set(num_list)))
        if len(num_list) >= 1:
            return num_list[0], num_list[-1], newsent
        else:
            return None

def Match_Cost_Time_Data(user_utter):
    """
    通话时长和数据流量是一定要有单位的，功能费则不一定，因此最后判断
    """
    time = Time_match(user_utter)
    if time != None:
        user_utter = time[2]
    data = Data_match(user_utter)
    if data != None:
        user_utter = data[2]
    cost = Cost_match(user_utter)
    results = {}
    if cost != None:
        results["费用"] = (cost[0], cost[1])
    if data != None:
        results["流量"] = (data[0], data[1])
    if time != None:
        results["通话时长"] = (time[0], time[1])
    return results


# 国家地区是考虑到日后可能需要这样的告知属性
COUNTRIES = {'乌拉圭', '芬兰艾伦岛', '冰岛', '西班牙马略卡岛', '斯图尔特岛', '尼加拉瓜', '多米尼加共和国', '约旦河西岸', '斯洛伐克', '法罗群岛', '哈萨克斯坦', '亚美尼亚', '安提瓜岛', '坦桑尼亚', '新加坡', '巴西', '塞班岛', '希腊克里特岛', '芬兰', '格林纳达', '象牙海岸', '葡萄牙圣港岛', '斯里兰卡', '圭亚那', '新西兰斯图尔特岛', '瑞典厄兰岛', '巴林', '古巴', '郝布里底群岛', '柬埔寨', '北爱尔兰', '马耳他', '蒙特塞拉特岛', '圣港岛', '台湾', '波兰', '洪都拉斯', '奥兰府', '博茨瓦纳', '科威特', '安的列斯群岛',
                 '西班牙梅诺卡岛', '希腊罗德岛', '法国', '西佛里西亚群岛', '特克斯和凯克斯群岛', '格林纳丁斯群岛', '伊朗', '危地马拉', '肯尼亚', '刚果', '英国郝布里底群岛', '突尼斯', '百慕大', '亚述尔群岛', '津巴布韦', '苏丹', '西班牙卡那利群岛', '挪威罗弗敦群岛', '尼日尔', '立陶宛', '爱沙尼亚', '意大利西西里岛', '英国北爱尔兰', '牙买加', '西班牙', '瑞士', '毛里求斯', '土耳其', '塞舌尔', '希腊爱奥尼亚', '乌干达', '乌克兰', '俄罗斯', '罗弗敦群岛', '罗德岛', '挪威斯雅尔巴群岛', '墨西哥', '瑙鲁', '巴拿马', '夏威夷',
                 '库拉索岛和博奈尔岛', '希腊伯罗奔尼撒', '新喀里多尼亚', '加纳', '也门', '多米尼克', '荷兰南贝佛兰岛', '马尔代夫', '乌兹别克斯坦', '秘鲁', '葡萄牙马德拉群岛', '苏里南', '美属维尔京群岛', '马提尼岛', '阿鲁巴', '缅甸', '斯洛文尼亚', '吉尔吉斯斯坦', '伯利兹', '斯雅尔巴群岛', '泰国', '格鲁吉亚', '西班牙伊比沙岛', '西班牙卡夫雷拉岛', '关岛', '斐济', '贝弗敖群岛', '意大利', '设得兰群岛', '巴勒斯坦', '巴布亚新几内亚', '阿根廷', '海地', '尼日利亚', '巴哈马', '纳米比亚', '海峡群岛', '阿尔及利亚', '英属维尔京群岛',
                 '文莱', '莫桑比克', '波恩荷尔摩岛', '马约特岛', '捷克', '哥特兰岛', '美国', '澳大利亚', '塞浦路斯', '哥斯达黎加', '丹麦', '英国', '蒙古', '巴基斯坦', '马其顿', '以色列', '刚果民主共和国', '科西嘉岛', '加蓬', '塔吉克斯坦', '列支敦士登', '日本', '约旦', '阿联酋', '曼岛', '塞内加尔', '伯罗奔尼撒', '泽西岛', '丹麦措辛厄岛', '保加利亚', '加拿大', '塞拉利昂', '新西兰', '英国设得兰群岛', '南非', '韩国', '西班牙美利利亚', '艾伦岛', '瑞典哥特兰岛', '法属圭亚那', '梵蒂冈', '帛琉岛', '印度', '摩尔多瓦', '葡萄牙亚述尔群岛',
                 '塞尔维亚', '丹麦波恩荷尔摩岛', '南贝佛兰岛', '越南', '卡塔尔', '圣文森特', '意大利撒丁岛', '阿富汗', '马德拉群岛', '圣卢西亚', '爱尔兰', '葡萄牙', '比利时', '西班牙切乌塔', '天宁岛', '希腊', '德国', '喀麦隆', '挪威西奥仑群岛', '帕劳', '尼泊尔', '丹麦朗厄兰岛', '不丹', '阿尔巴尼亚', '科特迪瓦', '波黑', '埃及', '萨尔瓦多', '荷兰西佛里西亚群岛', '沙特', '克里特岛', '摩纳哥', '奥地利', '直布罗陀', '基克拉泽', '阿塞拜疆', '开曼群岛', '海事漫游', '澳门', '奥克尼群岛', '汤加', '英国奥克尼群岛', '克罗地亚',
                 '卢森堡', '孟加拉', '马达加斯加', '印度尼西亚', '菲律宾', '巴布达', '巴拉圭', '孟加拉国', '萨摩亚', '西班牙福门特拉', '法国科西嘉岛', '瓜德罗普岛', '希腊基克拉泽', '白俄罗斯', '圣马力诺', '委内瑞拉', '玻利维亚', '安圭拉', '圣基茨和尼维斯', '马来西亚', '伊拉克', '东帝汶', '格陵兰', '老挝', '阿曼', '卢旺达', '西班牙加那利群岛', '香港', '瑞典', '匈牙利', '挪威', '哥伦比亚', '留尼汪岛', '厄瓜多尔', '赞比亚', '厄兰岛', '荷兰', '维尔京群岛', '摩洛哥', '黑山', '拉脱维亚', '罗马尼亚', '西奥仑群岛', '智利', '巴巴多斯',
                 '波多黎各', '爱奥尼亚', '黎巴嫩', '航空漫游', '瓦努阿图', '安哥拉'}

REGIONS = {
    # 使用美国为关键词查找北美流量包
    '美国': ['北美',  '美利坚', 'USA', ],
    # 使用巴西为关键词查找南美流量包
    '巴西': ['南美',],
    # 使用法国为关键词查找欧洲流量包
    '法国': ['欧洲', '欧盟',  '北欧', '东欧', '西欧', '法兰西', '英格兰', ],
    # 使用澳大利亚为关键词查找大洋洲流量包
    '澳大利亚': ['大洋洲', '澳洲', '袋鼠'],
    # 使用中国香港为关键词查找港澳台流量包
    '中国香港': ['港澳台', '赴台', '赴澳', '赴港', '港台',],
    '': ['',],
}

def Country_match(user_utter):
    """
    输入用户句子 ，输出匹配到的开通方向， 否则返回None
    """
    for country in COUNTRIES:
        if country in user_utter:
            return country
    for country, regions in REGIONS.items():
        for region in regions:
            if region in user_utter:
                return country
    return None

if __name__ == '__main__':
    while True:
        input_usr = input("请输入：")
        print(Match_Cost_Time_Data(input_usr))
        # print(Country_match(input_usr))
