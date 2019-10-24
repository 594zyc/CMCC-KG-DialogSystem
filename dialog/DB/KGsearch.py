# -*- coding: utf-8 -*-
"""
知识图谱查询API
"""
import os,codecs,sys,json,re,rdflib,datetime
from rdflib import Namespace, RDF

global g
g = rdflib.Graph()
prefixOWL = 'prefix owl: <http://www.w3.org/2002/07/owl#>'
prefixSyntax = 'prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>'
prefixSchema = 'prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>'
def init(save_path):
    global g
    g.parse(save_path, format='turtle')
    # print("init finish")
global depthContent

#通过结点的自然语言标签(rdfs:label)查找结点(entity_node)
def get_nodes_by_name(name):
    global g
    nodeList = []
    q = prefixOWL + prefixSyntax + prefixSchema + " select ?s where { ?s rdfs:label '"+ name +"' . ?s rdf:type owl:NamedIndividual}"
    x = g.query(q)
    t = list(x)
    for node in t:
        url = str(node[0])
        types = get_class_by_url(url)
        properties = get_nodeLabel_by_url(url)
        parents = get_parents_by_url(url)
        prop_contents = {}
        for prop in set(properties):
            prop_contents[prop] = get_property_content(url, prop)
        jsonData = {"url":url, "types":types, "name":name, "properties":prop_contents, "parents":parents}
        nodeList.append(jsonData)
    return nodeList

def get_entities_by_name(name):
    global g
    nodeList = []
    q = prefixOWL + prefixSyntax + prefixSchema + " select ?s where { ?s rdfs:label '"+ name +"' . ?s rdf:type owl:NamedIndividual}"
    x = g.query(q)
    t = list(x)
    for node in t:
        nodeList.append(str(node[0]))
    return nodeList

def get_parents_by_url(url):
    global g
    nodeList = []
    q = prefixOWL +prefixSyntax + prefixSchema +" select ?label where {  ?s ?p <" + url + "> . ?p rdf:type owl:ObjectProperty .{?s rdfs:label ?label}} "
    x = g.query(q)
    t = list(x)
    for node in t:
        cont = str(node[0])
        nodeList.append(cont)
    return nodeList

def get_objNode_by_name(name):
    global g
    nodeList = []
    q = prefixOWL + prefixSyntax + prefixSchema + " select ?s where { ?s rdfs:label '"+ name +"' . ?s rdf:type owl:ObjectProperty}"
    x = g.query(q)
    t = list(x)
    for node in t:
        nodeList.append(str(node[0]))
    return nodeList

def get_nodeLabel_by_url(url):
    global g
    nodeList = []
    q = prefixOWL +prefixSyntax + prefixSchema +" select ?label where { <" + url + "> ?p ?o  . ?p rdf:type owl:DatatypeProperty .{?p rdfs:label ?label}} "
    x = g.query(q)
    t = list(x)
    for node in t:
        cont = str(node[0])
        nodeList.append(cont)
    return nodeList

def get_objNodes_by_url(url):
    global g
    nodeList = []
    q = prefixSyntax + prefixSchema +" select ?o where { <" + url + "> ?p ?o . MINUS { <" + url + "> rdfs:label ?o } MINUS { <" + url + "> rdf:type ?o}} "
    x = g.query(q)
    t = list(x)
    for node in t:
        cont = str(node[0])
        if cont.__contains__("http://cmcc.com/ontology/shcema/"):
            nodeList.append(cont)
    return nodeList

def get_dataNode_by_name(name):
    global g
    nodeList = []
    q = prefixOWL + prefixSyntax + prefixSchema + " select ?s where { ?s rdfs:label '"+ name +"' . ?s rdf:type owl:DatatypeProperty}"
    x = g.query(q)
    t = list(x)
    for node in t:
        return str(node[0])
    return ""

#查询主语结点是否直接有property
def get_property_content(node,prop):
    global g
    nodeList = []
    q = prefixSchema + " select ?obj where { ?url2 rdfs:label '" + prop + "' . <" + node + "> ?url2 ?obj }"
    # print(q)
    x = g.query(q)
    t = list(x)

    for node2 in t:
        nodeList.append(str(node2[0]))
    return nodeList

def search_path(path):
    path = path

#搜索sub_node的所有相邻entity_node直到达到search_depth
def get_search_path(node, prop, depth):
    global g
    global depthContent
    path = ''
    depthContent = []
    nodeList = get_entities_by_name(node)
    propUrl = get_dataNode_by_name(prop)
    contList = []
    q = prefixOWL + prefixSyntax + prefixSchema + " select ?obj where { ?url1 rdfs:label '" + node + "' .\
    ?url2 rdfs:label '" + prop + "' . \
    ?url1 ?url2 ?obj }"
    x = g.query(q)
    t = list(x)
    if(len(t) == 0):
        for node2 in nodeList:
            if depth > 0:
                get_depth(node2, propUrl, depth - 1, path)
    else:
        # for node2 in t:
            # depthContent.append(str(node2[0]))
        depthContent.append(path)
        return depthContent

    return depthContent
#开始深度查询
def get_depth(node, prop, depth,path):
    global g
    global depthContent

    q = "select ?o where { <" + node + "> <"+ prop +"> ?o }"
    x = g.query(q)
    t = list(x)
    if (len(path)>0):
        path += ',' + get_name_by_url(node)
    else:
        path += get_name_by_url(node)
    if(len(t) == 0):
        for node2 in get_objNodes_by_url(node):
            get_depth(node2,prop,depth - 1, path)
    else:
        # for node2 in t:
            # depthContent.append(str(node2[0]))
        depthContent.append(path)
        return depthContent
    return depthContent
#通过url获得类别
def get_class_by_url(url):
    global g
    nodeList = []
    q = prefixSyntax + " select ?label where { <" + url + "> rdf:type ?o . {?o rdfs:label ?label } }"
    x = g.query(q)
    t = list(x)
    for node in t:
        cont = str(node[0])
        nodeList.append(cont)
    return nodeList

#通过名称获得类别
def get_class_by_name(name):
    global g
    nodeList = []
    q = prefixOWL + prefixSyntax + prefixSchema + " select ?s where { ?s rdfs:label '"+ name +"' . ?s rdf:type owl:Class}"
    x = g.query(q)
    t = list(x)
    for node in t:
        return str(node[0])
    return ""

#通过url获得label
def get_name_by_url(url):
    global g
    q = prefixOWL + prefixSyntax + prefixSchema + " select ?name where { <" + url + "> rdfs:label ?name . ?s rdf:type owl:NamedIndividual}"
    x = g.query(q)
    t = list(x)
    for node in t:
        return str(node[0])
    return ""

#获得类别下的url信息
def get_urls_by_types(type):
    global g
    concept = get_class_by_name(type)
    contList = []
    q = prefixSyntax + " select ?s where { ?s rdf:type <" + concept + ">}"
    x = g.query(q)
    t = list(x)
    for node in t:
        contList.append(str(node[0]))
    return contList

#获得类别下的名称信息
def get_nodes_by_types(name):
    global g
    concept = get_class_by_name(name)
    contList = []
    q = prefixOWL + prefixSyntax + prefixSchema + " select ?s where { ?s rdf:type <" + concept + "> }"
    # q = prefixOWL + prefixSyntax + prefixSchema + " select ?concept where { ?s rdfs:label '"+ name +"' . ?s rdf:type owl:Class .?concept rdf:type ?s }"
    x = g.query(q)
    t = list(x)
    for node in t:
        cont = str(node[0])
        nodes = get_node_urls_by_url(cont)
        contList.append(nodes[0])
    return contList

#通过结点的url查找结点(entity_node)
def get_nodes_by_url(url):
    global g
    nodeList = []
    q = prefixOWL + prefixSyntax + prefixSchema + " select ?o ?url where { <"+ url +"> rdfs:label ?o . <"+ url +"> rdf:type owl:NamedIndividual .{ ?url rdfs:label ?o} }"
    x = g.query(q)
    t = list(x)
    for node in t:
        name = str(node[0])
        url = str(node[1])
        # print("name: ", name, " \n url: ", url)
        types = get_class_by_url(url)
        properties = get_nodeLabel_by_url(url)
        parents = get_parents_by_url(url)
        prop_contents = {}
        for prop in set(properties):
            prop_contents[prop] = get_property_content(url, prop)
        jsonData = {"url":url, "types":types, "name":name, "properties":prop_contents, "parents":parents}
        nodeList.append(jsonData)
    return nodeList

def get_node_urls_by_url(url):
    global g
    nodeList = []
    q = prefixOWL + prefixSyntax + prefixSchema + " select ?o ?url where { <"+ url +"> rdfs:label ?o . <"+ url +"> rdf:type owl:NamedIndividual .{ ?url rdfs:label ?o} }"
    x = g.query(q)
    t = list(x)
    for node in t:
        name = str(node[0])
        url = str(node[1])
        prop_contents = {}
        # for prop in set(properties):
        #     prop_contents[prop] = get_property_content(url, prop)
        jsonData = {"url":url, "name":name}
        nodeList.append(jsonData)
    return nodeList

#给定宾语限制和属性的自然语言标签，查询满足条件的主语结点
def query_nodes_under_condition(nodes, key, krange):
    global g
    if not krange:
        return []
    nodeURLList = []
    minValue = krange[0]
    maxValue = krange[1]

    if key == '费用' :
        key = '月费'
    if key == '通话时长':
        key = '国内主叫通话时长'
    if key == '流量':
        key = '国内数据流量'

    for node in nodes:
        url = node['url']
        q = prefixOWL + prefixSchema + " select ?obj where { ?url1 rdfs:label '"+ key +"' .?url1 rdf:type owl:DatatypeProperty .<"+ url +"> ?url1 ?obj }"
        x = g.query(q)
        t = list(x)
        for node2 in t:
            cont = str(node2[0])
            if key.__contains__('月费'):
                cont = cont.replace('元/月','')
            if key.__contains__('国内数据流量'):
                cont = cont.replace('MB','')
            if key.__contains__('国内主叫通话时长'):
                cont = cont.replace('分钟','')
            if cont.__contains__('不限量'):
                cont = '88888888'
            if cont.__contains__('达量限速'):
                cont = '88888888'
            num = int(cont)
            if (minValue < num and num < maxValue):
                nodeURLList.append(node['url'])
    return nodeURLList

def get_all_individualName():
    global g
    nodeList = []
    q = prefixOWL + prefixSyntax + prefixSchema + " select ?o where { ?s rdfs:label ?o . ?s rdf:type owl:NamedIndividual}"
    x = g.query(q)
    t = list(x)
    for node in t:
        nodeList.append(str(node[0]))
    return nodeList

def get_all_propertyName():
    global g
    nodeList = []
    q = prefixOWL + prefixSyntax + prefixSchema + " select ?o where { ?s rdfs:label ?o . ?s rdf:type owl:DatatypeProperty   }"
    x = g.query(q)
    t = list(x)
    for node in t:
        nodeList.append(str(node[0]))
    return nodeList

def get_brand_by_url(url):
    global g
    nodeList = []
    q = prefixOWL + prefixSyntax + prefixSchema + " select ?o where {<" + url +"> owl:brand ?o }"
    x = g.query(q)
    t = list(x)
    for node in t:
        nodeList.append(str(node[0]))
    return nodeList

# def get_mutex_by_url(url):
#     global g
#     nodeList = []
#     q = prefixOWL + prefixSyntax + prefixSchema + " select ?name where {<" + url +"> owl:mutex ?o }"
#     x = g.query(q)
#     t = list(x)
#     for node in t:
#         nodeList.append(str(node[0]))
#     return nodeList
def get_mutex_by_url(url):
    global g
    nodeList = []
    q = prefixOWL + prefixSyntax + prefixSchema + " select ?o where {<" + url +"> owl:mutex ?o}"
    x = g.query(q)
    t = list(x)
    for node in t:
        nodeList.append(str(node[0]))
    return nodeList

def get_mutexName_by_url(url):
    global g
    nodeList = []
    q = prefixOWL + prefixSyntax + prefixSchema + " select ?name where {<" + url +"> owl:mutex ?o .?o rdfs:label ?name}"
    x = g.query(q)
    t = list(x)
    for node in t:
        nodeList.append(str(node[0]))
    return nodeList

def get_topProperty(propList):
    global g
    nodeList = []
    for propurl in propList:
        q = prefixSchema + "select ?name where {?s <"+propurl+"> ?o .<"+propurl+"> rdfs:label ?name}"
        x = g.query(q)
        t = list(x)
        frequency = len(t)
        url = propurl
        for node in t:
            label = str(node[0])
            tmp = {"label":label,"url":url,"frequency":frequency}
            nodeList.append(tmp)
            break
    nodeList = sorted(nodeList, key = operator.itemgetter('frequency'),reverse=True)
    return nodeList

def get_all_propertyURL():
    global g
    nodeList = []
    q = prefixOWL + prefixSyntax + prefixSchema + " select ?s where {?s rdf:type owl:DatatypeProperty   }"
    x = g.query(q)
    t = list(x)
    for node in t:
        nodeList.append(str(node[0]))
    return nodeList

def getEntitytoProperty(label):
    global g
    nodeList = []
    url = get_dataNode_by_name(label)
    q = prefixOWL + prefixSyntax + prefixSchema + " select ?s where {?s <" + url +"> ?o}"
    # print(q)
    x = g.query(q)
    t = list(x)
    for node in t:
        nodeList.append(str(node[0]))
    return nodeList

if __name__ == "__main__":

    # save_dir = './data/tmp'
    init('./dialog/DB/ontology/mobile-ontology-5.2.ttl')
    starttime = datetime.datetime.now()

    # 0. 查找具有某属性的所有结点
    rel = '开通移动数据流量'
    urls = getEntitytoProperty(rel)
    print(len(urls))
    for url in urls:
        nodes = get_nodes_by_url(url)
        # print(nodes)
        print(nodes[0]['name'])
        print(nodes[0]['properties'][rel])


    # 1.通过结点的自然语言标签(rdfs:label)查找结点(entity_node)
    # nodes = get_nodes_by_name('畅享套餐组合套餐88元档')
    # print(nodes)
    # print(get_nodes_by_name('业务介绍'))
    # for node in nodes:
    #     print(node['name'])
    #     print(node['url'])
    #     print('type:', get_class_by_url(node['url']))
    #     for prop,cont in node['properties'].items():
    #         print(prop, ": ", cont)

    # # 2.查询主语结点是否直接有property

    # nodes = get_nodes_by_name('4G飞享套餐38元档')
    # print(get_property_content(nodes[0]['url'], "月费"))
    # url = 'http://cmcc.com/ontology/shcema/0191'
    # print(get_entities_by_name('4G飞享套餐38元档'))
    # print(get_name_by_url(url))
    # print(get_objNodes_by_url(url))
    # print(get_parents_by_url(url))
    # print(get_dataNode_by_name('取消'))

    # 3.搜索sub_node的所有相邻entity_node直到达到search_depth
    # prop = "品牌"
    # result = get_search_path("4G飞享套餐138元档", prop, 10)
    # for obj in result:
    #     print('path:', obj[0])
    #     for idx, cont in enumerate(obj[1]):
    #         print('%s %d: '%(prop, idx), cont)

    # 4.同时具有types中所有类别标签的individuals中查找
    # print(get_nodes_by_types("畅享卡"))

    # 5.给定宾语限制和属性的自然语言标签，查询满足条件的主语结点
    # jsonData = {'国内主叫通话时长':(0,200)}
    jsonData = {'流量':(0,500)}
    #
    # for node in get_nodes_by_types("和4G套餐"):
    #     print(node['name'])
    # res1, res2 = [], []
    # for t in ['和4G套餐', '4G飞享套餐', '畅享套餐', '移动大流量套餐', '全球通系列套餐']:
    #     res1 += query_nodes_under_condition(get_nodes_by_types(t), '流量', (0,500))
    #     res2 += query_nodes_under_condition(get_nodes_by_types(t), '通话时长', (0,200))
    # print(res1)
    # print(res2)
    # res = set(res1)&set(res2)
    # print(res)
    #     # print(res)
    # for url in res:
    #     ent = get_nodes_by_url(url)[0]
    #     print(ent)
    #     prop = get_property_content(ent['url'], '国内主叫通话时长')
    #     print(ent['name'],":", prop)

    #     prop = get_property_content(ent['url'], '国内数据流量')
    #     print(ent['name'],":", prop)
    # endtime = datetime.datetime.now()
    # print (endtime - starttime)
    # 6.获得所有individual name

    # iname = get_all_individualName()
    # with open(os.path.join(save_dir, 'KG_individual_list.txt'), 'w', encoding='utf-8') as f:
    #     for i in sorted(list(set(iname)), key=lambda x:len(x)):
    #         f.write(i+'\n')

    # 7.获得所有property name
    # p_name = get_all_propertyName()
    # with open(os.path.join(save_dir, 'KG_property_list.txt'), 'w', encoding='utf-8') as f:
    #     for i in sorted(list(set(p_name)), key=lambda x:len(x)):
    #         f.write(i+'\n')

    # 8.获得套餐适用品牌的url
    # nodes = get_nodes_by_name('4G飞享套餐38元档')
    # # nodes = get_nodes_by_name('4G飞享套餐')
    # # print(nodes)
    # # ntype =
    # print(nodes[0]['types'])
    # tpurl = get_class_by_name(nodes[0]['types'][0])
    # print(tpurl)
    # brand = get_brand_by_url(tpurl)
    # for b in brand:
    #     print(b)
    #     print(get_name_by_url(b))



    # # 9.获得互斥套餐的url
    # nodes = get_nodes_by_name('畅享套餐58元档')
    # print(nodes)
    # tpurl = get_class_by_name(nodes[0]['types'][0])
    # print(tpurl)
    # # brand = get_brand_by_url(tpurl)
    # print(get_mutex_by_url(tpurl))
    # print(get_mutexName_by_url(tpurl))

    # 获得排序后的结果
    # nlist = get_topProperty(get_all_propertyURL())
    # with open(os.path.join(save_dir, 'KG_property_with_freq.txt'), 'w', encoding='utf-8') as f:
    #     for i in nlist:
    #         f.write('%s %s\n'%(i['label'], i['frequency']))
