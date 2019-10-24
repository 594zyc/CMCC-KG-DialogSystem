# THUEE-CMCC Dialog System V1.0 
基于知识图谱进行套餐推荐、套餐信息查询、个人信息查询等任务的中移动智能对话系统。

## 环境
* python 3.6
* TensorFlow 1.8
* jieba 0.39
* scikit-learn 0.19.2
* scipy 1.1.0
* matplotlib 2.2.3

## 使用方式

####进行对话
```
python Agent.py
```
测试版系统的默认用户名为test，对话历史和日志保存在logs/test/<br>
重启对话关键词：restart|重新开始|重启对话<br>
结束对话关键词：finish|再见|结束|拜拜|谢谢<br>


####执行逻辑
1. 接受用户输入。
2. 调用NLUManage模块返回各个NLU模块的识别结果。
3.	调用DialogManager模块，其输入为NLU识别结果，输出为当前对话状态。DialogManager包括DialogStateTracker和PolicyManager两个子模块，依次完成对话状态的更新以及策略生成，目前使用的是基于规则的对话策略，见policy_rules.py。
4.	DialogManager会与知识图谱进行交互。基于知识图谱的系统通过DBoperator查询图谱的本体文件mobile-ontology-5.2.ttl，图谱交互的API见KGsearch.py，运行该文件可完成图谱查询API的测试。
5. 最后调用NLGManager生成系统的自然语言回复，输出。目前使用的是基于规则模板的NLG，见NLG_rules.py。
6. 若检测到结束信号（用户输入再见，结束等），程序退出，保存日志。


####训练模型
我们一共有 用户动作识别器、 属性识别器 和 值识别器 三个识别器。使用到的模型有两种: 
1. 词袋模型(BOW)
2. 富对话状态跟踪模型 (EDST)

BOW 相比 EDST 得到了结果更加稳定且运行快得多，但是识别的准确率和 F1 score EDST 比 BOW 要高一些。最终我们的 值识别器 采用 EDST, 用户动作识别器 和 属性识别器 采用 BOW。用于训练的脚本 分别是 train_NLU_useracts.py, train_NLU_attrs.py, train_NLU_values.py。训练使用 early stopping, 词向量是经过DASI后处理过的 word2vec.

在众包数据集上的识别结果如下：  
用户动作

| 模型 | accu |   
| --- | --- |    
| BOW | 0.9923 |  
| EDST | 0.9926 |    
 
 属性识别

| 模型 | accu | F1 | 
| --- | --- | --- |   
| BOW | 0.9922 | 0.8729|
| EDST | 0.9919 | 0.8745| 

值识别

| 模型 | accu | F1 | 
| --- | --- | --- |   
| BOW | 0.9108 | 0.7926|
| EDST | 0.9307 | 0.8512 |

## 特别说明
1. 对话系统能够识别、处理的内容定义见dialog/config.py
2. 在系统实现时对知识图谱中缺失的少量必要属性编写了默认值
3. 当前系统并未使用单独的QA模块(disabled)，“场景123标准问题”中的QA对暂未使用，但可以处理知识图谱中包含的“QA”形式的属性。
		


## Contributor

Yichi Zhang  
Yinpei Dai  
[Zhijian Ou](http://oa.ee.tsinghua.edu.cn/ouzhijian/index.htm)  