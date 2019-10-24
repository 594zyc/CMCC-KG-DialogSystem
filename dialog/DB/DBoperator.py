"""
知识库查询接口
"""
from .KGsearch import *
from dialog.config import duplicate_attrs
# duplicate_attrs = {
#     '费用': ['费用', '月费', '功能费', '信息费', '月基本费'],
#     '流量': ['国内数据流量', '国内流量', '流量'],
#     '通话时长': [ '国内主叫通话时长', '通话时长', '国内主叫'],
#     '说明': ['资源说明', '说明'],
#     '扣费时间': ['套餐月费扣费时间', '扣费时间'],
#     '国内被叫': ['国内被叫', '国内免费被叫通话'],
#     '赠送业务': ['赠送业务', '加赠本地咪咕定向流量', '加赠套外国内流量', '国际漫游转赠频次'],
#     '介绍': ['业务介绍', '介绍'],
#     '开通方式': ['开通', '短信指令', '办理'],
#     '其他规则': ['其他规则', '特殊情况']}

class DBOperator(object):
    def __init__(self, save_path):
        init(save_path)
        self.duplicate_attrs = duplicate_attrs
        self.load_personal_info()

    def load_personal_info(self):
        # 载入模拟的个人信息
        self.personal_info = {
            "已办业务": ['4G飞享套餐58元档', '4G流量加油包30元档', '5元彩信套餐'],
            "当前主套餐": '4G飞享套餐58元档',
            '剩余流量': "1.10 GB",
            '剩余通话': "100 分钟",
            "套餐余量": "流量 1.10 GB，通话 100 分钟，国内彩信 15条",
            "话费余额": "110.20 元",
            "号码": "18811369685",
            "号卡品牌": "神州行",
            "归属地" : "北京",
            "停机": "否",
            "详单账单": "请登录网上营业厅、微厅或 APP 查询",
            "客户星级": "3星级",
            "积分": "1200分",
            "客服密码": "请致电10086查询"
        }

    def KGQueryByConstraints(self, info_state, search_type = ['和4G套餐', '4G飞享套餐', '畅享套餐', '移动大流量套餐', '全球通系列套餐', '畅游包', '4G流量加油包']):
        """
        按限制条件搜索实体
        :param info_state: 费用，流量，通话时长的取值范围，e.g. {'费用':(0，50)}
        :param search_type: 查找范围的：类别名的列表
        :return: 所有符合要求的套餐名称
        """
        urls = None
        for key, krange in info_state.items():
            if not krange:
                continue
            res_key = []
            for t in search_type:
                nodes = get_nodes_by_types(t)
                res_key += query_nodes_under_condition(nodes, key, krange)
            # print(key)
            # [print(get_name_by_url(i)) for i in res_key ]
            if urls is None:
                urls = set(res_key)
            else:
                urls = set(res_key) & urls
            # print(urls)
        if not urls:
            return []

        entity_list = []
        for url in urls:
            ent_name = get_name_by_url(url)
            entity_list.append(ent_name)

        return entity_list

    def KGQueryByName(self, ent_name):
        """
        按名字搜索实体
        return: rdfs label==ent_name的实体的所有信息
        """
        return get_nodes_by_name(ent_name)

    def KGQueryType(self, ent_name):
        """
        通过名字搜索类别标签
        return： rdfs label==ent_name的实体的类别标签
        """
        nodes = get_nodes_by_name(ent_name)
        if not nodes:
            return None
        node = nodes[0]
        if not node['types']:
            return None
        return node['types'][0]

    def KGQueryProperty(self, ent_name, relations):
        """
        查找实体的属性
        param: relations: 要查找的属性名称的列表
        returns: rdfs label==ent_name的实体的属性值，不存在的属性则为None
                     e.g. {'费用': '100元/月', '通话时长': None}
        """
        nodes = get_nodes_by_name(ent_name)
        if not nodes:
            return {}
        properties = {}
        for node in nodes:
            for relation in relations:
                if relation in ['办理限制', '适用品牌', '能否办理']:
                    if not node['types']:
                        continue
                    type_url = get_class_by_name(node['types'][0])
                    brand_urls = get_brand_by_url(type_url)
                    brands = [get_name_by_url(b) for b in brand_urls]
                    properties[relation] = brands
                elif relation == '互斥业务':
                    if not node['types']:
                        continue
                    type_url = get_class_by_name(node['types'][0])
                    mutex = get_mutexName_by_url(type_url)
                    properties[relation] = mutex
                else:
                    relation_alters = self.duplicate_attrs.get(relation, [relation])
                    properties[relation] = None
                    for rela in relation_alters:
                        value = node['properties'].get(rela)
                        if value:
                            properties[relation] = value[0]
                            break
        return properties


    def  KGQueryPropWoSubj(self, relation):
        """
        查找缺省主语的属性
        param: relation: 要查找的属性名称str
        returns:
            具有该属性的实体数量 if num>3 else {entity_name: relation value}
        """
        # properties = {}
        urls = getEntitytoProperty(relation)
        if len(urls) != 1:
            return len(urls), None
        for url in urls:
            node = get_nodes_by_url(url)[0]
            # name = node['name']
            value = node['properties'][relation][0]
        # properties[name] = value
        return len(urls), value




if __name__ == "__main__":
    KGO = DBOperator('./dialog/DB/ontology/mobile-ontology-5.2.ttl')
    ent_list = KGO.KGQueryByConstraints({'流量':(0,500),'通话时长':None})
    # '通话时长':(0,200)
    # for ent in ent_list:
    #     nodes = get_nodes_by_name(ent)[0]
    #     print(nodes['name'])
    #     print(nodes['properties'].get('国内数据流量'))
    #     print(nodes['properties'].get('国内主叫通话时长'))
    print(KGO.KGQueryProperty('积分计划', ['积分兑换', '取消积分计划']))

    # print(KGO.KGQueryByName('4G飞享套餐58元档'))
