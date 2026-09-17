# -*- coding: utf-8 -*-
"""荣勋之路 · Kivy v9 · 战争系统"""
import kivy
kivy.require('2.0.0')

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.core.text import LabelBase
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivy.graphics import Color, Rectangle
import random
import os
import sys
from datetime import datetime

# 兼容 PyInstaller 打包
if getattr(sys, 'frozen', False):
    BASE = sys._MEIPASS
else:
    BASE = os.path.dirname(os.path.abspath(__file__))

# 中文字体注册
_FONT_PATH = os.path.join(BASE, "assets", "font.ttf")
LabelBase.register(name='Chinese', fn_regular=_FONT_PATH)

# 全屏（手机端）
from kivy.utils import platform
if platform == 'android':
    Window.fullscreen = True
    Window.softinput_mode = 'below_target'
else:
    Window.size = (1100, 750)
Window.clearcolor = (0.04, 0.05, 0.06, 1)# 兼容 PyInstaller 打包
if getattr(sys, 'frozen', False):
    BASE = sys._MEIPASS
else:
    BASE = os.path.dirname(os.path.abspath(__file__))

IMG_DIR = os.path.join(BASE, "assets", "images")
MUSIC_DIR = os.path.join(BASE, "assets", "music")
FONT_PATH = os.path.join(BASE, "assets", "font.ttf")

RANKS = ["列兵","上等兵","下士","中士","二级上士","一级上士",
         "三级军士长","二级军士长","一级军士长","少尉","中尉","上尉",
         "少校","中校","上校","少将","中将","上将","军委副主席"]
RANK_TYPE = ["士兵"]*4+["军士"]*5+["尉官"]*3+["校官"]*3+["将官"]*3+["最高"]
MEDAL_POINTS = {"嘉奖":0,"三等功":1,"二等功":3,"一等功":6,"荣誉称号":10}
REWARD_THRESHOLDS = [(150,"一等功"),(80,"二等功"),(40,"三等功"),(20,"嘉奖")]

HOSPITALS = {
    "连卫生队":{"level":1,"recover":4,"desc":"条件简陋，只能处理轻伤"},
    "营卫生所":{"level":2,"recover":7,"desc":"有军医和基础设备"},
    "旅（团）医院":{"level":3,"recover":11,"desc":"科室较全，有手术能力"},
    "军队中心医院":{"level":4,"recover":16,"desc":"三甲，设备先进"},
    "总医院":{"level":5,"recover":22,"desc":"全军顶级，专家云集"},
}

EDUCATION_LEVELS = [
    ("初中",18,20),("高中",18,22),("中专",18,22),
    ("大专",18,24),("本科",18,24),("研究生",18,26),
]

PROVINCES = [
    ("北京",{"politics":5,"reputation":3}),("天津",{"leadership":4,"morale":4}),
    ("河北",{"fitness":5,"discipline":4}),("山西",{"discipline":5,"fitness":4}),
    ("内蒙古",{"fitness":6,"morale":4}),("辽宁",{"fitness":6,"discipline":3}),
    ("吉林",{"fitness":6,"morale":3}),("黑龙江",{"fitness":7,"discipline":3}),
    ("上海",{"tactics":5,"politics":3}),("江苏",{"politics":5,"leadership":3}),
    ("浙江",{"tactics":4,"morale":4}),("安徽",{"leadership":4,"discipline":4}),
    ("福建",{"tactics":5,"morale":4}),("江西",{"morale":6,"politics":4}),
    ("山东",{"fitness":6,"discipline":4}),("河南",{"fitness":5,"leadership":4}),
    ("湖北",{"tactics":5,"leadership":4}),("湖南",{"leadership":5,"morale":5}),
    ("广东",{"tactics":5,"fitness":3}),("广西",{"fitness":6,"tactics":4}),
    ("海南",{"fitness":5,"morale":4}),("重庆",{"morale":6,"fitness":3}),
    ("四川",{"morale":6,"leadership":4}),("贵州",{"fitness":5,"discipline":4}),
    ("云南",{"fitness":6,"tactics":3}),("西藏",{"fitness":7,"morale":5}),
    ("陕西",{"discipline":5,"fitness":4}),("甘肃",{"fitness":6,"discipline":5}),
    ("青海",{"fitness":6,"morale":4}),("宁夏",{"discipline":5,"morale":4}),
    ("新疆",{"fitness":6,"morale":4}),
]

ARMIES = {
    "陆军":{"fitness":8,"tactics":5},
    "海军":{"tactics":8,"discipline":5},
    "空军":{"tactics":6,"fitness":4},
    "火箭军":{"tactics":10,"politics":3},
    "武警部队":{"tactics":8,"discipline":5,"leadership":3},
}

ROUTES = {
    "指挥路线":{"desc":"带兵打仗，核心：指挥/领导/战术"},
    "技术路线":{"desc":"技术攻关，核心：技术/战术"},
    "政工路线":{"desc":"政治工作，核心：政工值/思想/组织"},
}

RELATION_TARGETS = {
    "班长":{"desc":"你的第一任班长"},
    "连长":{"desc":"连队主官"},
    "政委":{"desc":"政治主官"},
    "战友":{"desc":"同吃同住的战友"},
}

SUBORDINATE_NAMES = ["小王","小李","老张","小刘","老赵","小陈","小杨","老周"]

# ========== 战争事件链 ==========
WAR_EVENTS = [
    {"title":"战前动员",
     "text":"上级下达战备命令，你部进入一级战备。\n\n全连紧急集合，等待作战任务。",
     "choices":[
        {"text":"全员紧急集合，快速动员","effects":{"troop_power":8,"morale":5,"reward_score":3}},
        {"text":"分批集结，有序准备","effects":{"troop_power":5,"discipline":3,"reward_score":2}}]},
    {"title":"首战",
     "text":"敌军前锋逼近，你部担任主攻。\n\n战场形势复杂，需要快速决策。",
     "choices":[
        {"text":"正面强攻，硬碰硬","effects":{"command":8,"health":-12,"troop_power":-10,"reputation":10,"reward_score":8}},
        {"text":"侧翼迂回，出奇制胜","effects":{"tactics":10,"command":6,"troop_power":-5,"reputation":12,"reward_score":10}}]},
    {"title":"相持阶段",
     "text":"连续作战多日，部队疲惫，弹药给养告急。",
     "choices":[
        {"text":"节约弹药，减少消耗","effects":{"discipline":6,"troop_power":-5,"reward_score":3}},
        {"text":"冒险空投，补充给养","effects":{"tactics":5,"health":-5,"troop_power":5,"reward_score":6}},
        {"text":"就地征集，补充物资","effects":{"leadership":5,"reputation":-5,"reward_score":2}}]},
    {"title":"敌军反扑",
     "text":"敌军集中优势兵力反扑，你部承受巨大压力。",
     "choices":[
        {"text":"死守阵地，寸土不让","effects":{"discipline":8,"health":-15,"reputation":12,"reward_score":10}},
        {"text":"主动撤退，保存实力","effects":{"health":-5,"reputation":-8,"reward_score":-3}},
        {"text":"呼叫增援，请求支援","effects":{"leadership":5,"troop_power":5,"reward_score":5}}]},
    {"title":"决战时刻",
     "text":"上级下达总攻命令。\n\n这是决定胜负的一战。",
     "choices":[
        {"text":"集中优势兵力，全力一击","effects":{"command":12,"tactics":10,"troop_power":-20,"reputation":20,"medal":"一等功"}},
        {"text":"多路突击，分割包围","effects":{"tactics":10,"leadership":8,"troop_power":-15,"reputation":15,"medal":"二等功"}},
        {"text":"稳扎稳打，逐点推进","effects":{"tactics":5,"leadership":5,"troop_power":-8,"reputation":8,"reward_score":10}}]},
]




# ========== 成就系统 ==========
ACHIEVEMENTS = {
    # 军衔成就
    "rank_5":   {"name":"士官之路",  "desc":"晋升到二级上士",    "check":lambda s:s["rank_index"]>=4, "reward":{"reputation":5}},
    "rank_9":   {"name":"军官起点",  "desc":"晋升到少尉",        "check":lambda s:s["rank_index"]>=9, "reward":{"reputation":10,"morale":5}},
    "rank_12":  {"name":"校官之列",  "desc":"晋升到少校",        "check":lambda s:s["rank_index"]>=12,"reward":{"reputation":15,"leadership":5}},
    "rank_15":  {"name":"将军之路",  "desc":"晋升到少将",        "check":lambda s:s["rank_index"]>=15,"reward":{"reputation":25,"leadership":10}},
    "rank_18":  {"name":"军委副主席","desc":"晋升到军委副主席",  "check":lambda s:s["rank_index"]>=18,"reward":{"reputation":50,"leadership":15}},
    # 战斗成就
    "war_win":  {"name":"实战老兵",  "desc":"赢得一场常规战争",  "check":lambda s:s.get("war_done"), "reward":{"reputation":10}},
    "sunset_win":{"name":"落日英雄", "desc":"赢得落日行动",      "check":lambda s:s.get("sunset_done") and not s.get("sacrifice"), "reward":{"reputation":30}},
    # 勋章成就
    "medal_3":  {"name":"初露锋芒",  "desc":"获得3枚勋章",       "check":lambda s:sum(s.get("medals",{}).values())>=3, "reward":{"reputation":10}},
    "medal_5":  {"name":"功勋卓著",  "desc":"获得5枚勋章",       "check":lambda s:sum(s.get("medals",{}).values())>=5, "reward":{"reputation":20}},
    "medal_hero":{"name":"时代楷模", "desc":"获得荣誉称号",      "check":lambda s:s.get("medals",{}).get("荣誉称号",0)>0, "reward":{"reputation":25}},
    # 感情成就
    "love":     {"name":"军人恋歌",  "desc":"找到恋人",          "check":lambda s:s.get("lover"), "reward":{"morale":5}},
    "married":  {"name":"军婚不易",  "desc":"结婚",              "check":lambda s:s.get("married"), "reward":{"morale":10}},
    "children": {"name":"军爸",      "desc":"有孩子",            "check":lambda s:s.get("children",0)>0, "reward":{"morale":10}},
    # 品格成就
    "letter_3": {"name":"未雨绸缪",  "desc":"写下3封遗书",       "check":lambda s:len(s.get("letters",[]))>=3, "reward":{"reputation":8}},
    "hospital": {"name":"劫后重生",  "desc":"从住院中恢复",       "check":lambda s:s.get("hospital_done"), "reward":{"morale":5}},
    # 特殊成就
    "all_arms": {"name":"足迹全军",  "desc":"完成一次常规战争+落日行动", "check":lambda s:s.get("war_done") and s.get("sunset_done"), "reward":{"reputation":20}},
    "perfect":  {"name":"完美指挥",  "desc":"落日行动0失误",     "check":lambda s:s.get("sunset_done") and s.get("sunset_mistakes",0)==0, "reward":{"reputation":50}},
    "rich":     {"name":"经济独立",  "desc":"金钱≥10000",        "check":lambda s:s["money"]>=10000, "reward":{"reputation":5}},
    "fitness_max":{"name":"体能巅峰","desc":"体能达到100",       "check":lambda s:s["fitness"]>=100, "reward":{"morale":5}},
    "review_top":{"name":"民主典范", "desc":"民主评议获得优秀",  "check":lambda s:s.get("review_score",0)>=85, "reward":{"reputation":10}},
}

# ========== 感情系统 ==========
MEET_METHODS = {
    "联谊会":{"desc":"部队和地方单位联谊","names":["小雅","小琴","小娟","小芳","小婷"],
              "traits":["温柔","活泼","文静","爽朗"],
              "work":["教师","护士","公务员","会计"],
              "initial_affection":30},
    "战友介绍":{"desc":"战友的亲戚或同学","names":["小曼","小雯","小丽","小倩"],
                "traits":["贤惠","朴实","乐观","独立"],
                "work":["医生","工程师","教师","职员"],
                "initial_affection":40},
    "同学重逢":{"desc":"中学/大学老同学","names":["小雨","小月","小燕","小梅"],
                "traits":["知性","感性","理性","温柔"],
                "work":["教师","律师","记者","公务员"],
                "initial_affection":45},
    "家人介绍":{"desc":"父母托人介绍","names":["小慧","小玉","小桃","小荷"],
                "traits":["传统","勤快","孝顺","朴实"],
                "work":["护士","幼师","护理","文员"],
                "initial_affection":35},
}

LOVE_STAGES = ["单身","相识","恋爱","订婚","结婚","怀孕","生子","育儿","白首"]

# ========== 遗书系统 ==========
LETTER_TEMPLATES = {
    "父母":{
        "title":"致父母",
        "content":"爸、妈：\n\n儿子不孝，不能给您二老养老送终了。\n\n儿子是为国捐躯，死得其所。\n\n不孝子 {name} 绝笔\n{date}",
        "reply_delay":"三个月后",
        "reply":"【父母回信】\n儿啊：\n你的信我们收到了。\n你妈哭了三天三夜。\n下辈子，还做我们的儿子。\n父 字",
    },
    "妻儿":{
        "title":"致妻儿",
        "content":"吾妻：\n\n若有来生，我仍愿娶你为妻。\n\n孩子还小，望你好好抚养他长大。\n\n夫 {name} 绝笔\n{date}",
        "reply_delay":"半年后",
        "reply":"【妻子回信】\n夫君：\n信我收到了。我不怪你。\n等你回家。\n妻 字",
    },
    "战友":{
        "title":"致战友",
        "content":"亲爱的战友们：\n\n若有来生，我们还做战友！\n\n{name} 绝笔\n{date}",
        "reply_delay":"追悼会上",
        "reply":"【连队回信】\n{name}同志：\n你的遗书，全连传阅。\n你的位置，永远给你留着。\n全连答：到！",
    },
    "祖国":{
        "title":"致祖国",
        "content":"祖国：\n\n若有战，召必回，战必胜。\n愿山河无恙，愿国泰民安。\n\n{name} 绝笔\n{date}",
        "reply_delay":"一年后",
        "reply":"【祖国回信】\n{name}同志：\n你的名字，将永远刻在人民英雄纪念碑上。\n祖国 永远铭记",
    },
    "空白":{
        "title":"空白信纸",
        "content":"（你拿起笔，却不知从何写起。）\n\n“若有战，召必回。”\n\n{name}\n{date}",
        "reply_delay":"多年后",
        "reply":"【无名回信】\n没有署名，没有地址。\n但所有人都知道，这封信写给谁。",
    },
}

LETTER_KEEPERS = {
    "士兵":"连队指导员保管","军士":"连队指导员保管",
    "尉官":"营政治教导员保管","校官":"师政治部保管",
    "将官":"军委政治工作部保管","最高":"军委政治工作部保管",
}

def get_letter_keeper(rank_index):
    return LETTER_KEEPERS.get(RANK_TYPE[rank_index],"连队指导员保管")

def T(name,desc,**eff):
    return {"name":name,"desc":desc,"effects":eff}

BASE_TASKS = {
    0:[T("新兵队列","站军姿、踢正步。",fitness=4,discipline=4,morale=-1),
       T("五公里越野","背装具跑五公里。",fitness=6,health=-3,morale=-1),
       T("站岗执勤","哨位站两小时。",discipline=5,health=-2,morale=-2)],
    1:[T("战术基础","卧倒、匍匐、利用地形。",tactics=5,fitness=2),
       T("帮带新兵","带新兵练队列。",leadership=4),
       T("政治学习","读报、写心得。",politics=5)],
    2:[T("带新兵班","负责一个班训练。",leadership=6),
       T("班战术训练","组织班组战术。",tactics=6,leadership=4),
       T("专业集训","参加团专业集训。",tactics=5,fitness=3,reputation=5)],
    3:[T("代理班长","代理班长职务。",leadership=7,discipline=3),
       T("组织训练","负责课目组训。",leadership=6,tactics=4,reputation=3),
       T("团比武","团级军事比武。",fitness=5,tactics=5,reputation=8,health=-5)],
}

ROUTE_TASKS = {
    "指挥路线":{
        4:[T("班长骨干","连队班长骨干。",leadership=8,tactics=4,command=5),
           T("专业比武","师级专业比武。",tactics=6,fitness=4,command=4,reputation=8,health=-4)],
        9:[T("排长","正式担任排长。",leadership=8,tactics=7,command=9,troop_power=8),
           T("营演习","带全排参加营演习。",tactics=9,command=10,troop_power=10,reputation=10)],
        12:[T("营长","指挥全营。",leadership=12,tactics=10,command=16,troop_power=20,reputation=16)],
    },
    "技术路线":{
        4:[T("装备维修","排除装备故障。",tech=6,discipline=4,tech_points=5),
           T("技能比武","专业技能比武。",tech=8,fitness=3,reputation=8,tech_points=6)],
        9:[T("技术方案","制定技术方案。",tech=10,leadership=5,tech_points=12),
           T("科研项目","参与科研项目。",tech=12,tech_points=15,reputation=8)],
        12:[T("技术体系","构建技术体系。",tech=16,leadership=9,tech_points=25)],
    },
    "政工路线":{
        4:[T("板报宣传","负责连队板报。",pol_work=6,politics=5,thought=3),
           T("谈心谈话","与战士一对一谈心。",pol_work=5,leadership=3,thought=5)],
        9:[T("政治教育","组织政治教育。",pol_work=8,politics=6,thought=6),
           T("心理疏导","为战士心理疏导。",pol_work=8,leadership=6,thought=10)],
        12:[T("教导员","担任营教导员。",pol_work=16,politics=12,leadership=10,thought=20,reputation=16)],
    },
}


# ========== 落日行动（六层指挥体系） ==========
SUNSET_LAYERS = [
    # 第一层：士兵
    {
        "title":"第一层 · 士兵","role":"突击部队 · 一线士兵",
        "intro":"登陆艇舱门打开，海水涌进来。你握着步枪冲上滩头。",
        "decisions":[
            {"title":"决策1/6 · 抢滩","text":"前方30米开阔滩头，碉堡机枪扫射。",
             "choices":[
                {"text":"跟班长第一个冲出去","score":3,"effects":{"leadership":4,"health":-8},"note":"勇敢但危险"},
                {"text":"等第二波再冲","score":1,"effects":{"health":-3},"note":"安全"},
                {"text":"跳水从侧面游过去","score":3,"effects":{"tactics":5,"health":-6},"note":"出奇制胜"},
                {"text":"躲在艇后等支援","score":-2,"effects":{"health":-15},"note":"艇会被炸毁"},
             ]},
            {"title":"决策2/6 · 碉堡","text":"前方碉堡火力全开。",
             "choices":[
                {"text":"主动请缨扛炸药包","score":3,"effects":{"leadership":6,"health":-12},"note":"九死一生"},
                {"text":"用火箭筒远程打击","score":3,"effects":{"tactics":6,"health":-4},"note":"正确做法"},
                {"text":"匍匐过去用手榴弹","score":1,"effects":{"health":-8},"note":"危险"},
                {"text":"呼叫炮火覆盖","score":-2,"effects":{"health":-5},"note":"会误伤"},
             ]},
            {"title":"决策3/6 · 俘虏","text":"一名敌军举着手喊投降。",
             "choices":[
                {"text":"让他举手搜身检查","score":3,"effects":{"tactics":4},"note":"标准流程"},
                {"text":"直接搜身","score":-3,"effects":{"health":-10},"note":"可能藏手雷"},
                {"text":"让他自己走过来","score":-1,"effects":{"health":-5},"note":"可能诈降"},
                {"text":"叫战友一起包围","score":2,"effects":{"discipline":3},"note":"稳妥"},
             ]},
            {"title":"决策4/6 · 战友","text":"战友倒在开阔地，腿部中弹。",
             "choices":[
                {"text":"先扔烟雾弹再救","score":3,"effects":{"tactics":5,"health":-6},"note":"战术正确"},
                {"text":"直接冲出去救","score":1,"effects":{"health":-15},"note":"鲁莽"},
                {"text":"呼叫卫生员","score":-2,"effects":{"morale":-3},"note":"过不来"},
                {"text":"继续前进","score":-3,"effects":{"morale":-8},"note":"煎熬"},
             ]},
            {"title":"决策5/6 · 指挥","text":"班长和排长都牺牲。",
             "choices":[
                {"text":"站出来指挥继续进攻","score":3,"effects":{"leadership":8,"reputation":12},"note":"担当"},
                {"text":"组织就地防守等援军","score":1,"effects":{"discipline":5},"note":"被动"},
                {"text":"带大家撤退","score":-2,"effects":{"reputation":-10},"note":"军法不容"},
                {"text":"让老兵指挥","score":1,"effects":{"leadership":3},"note":"尊重"},
             ]},
            {"title":"决策6/6 · 战场缴获","text":"发现一台加密通讯设备。",
             "choices":[
                {"text":"立即上报情报部门","score":3,"effects":{"tactics":3,"reputation":8,"intel":2},"note":"正确"},
                {"text":"自己试着破解","score":0,"effects":{"tactics":5},"note":"越权"},
                {"text":"原地销毁","score":-1,"effects":{"discipline":3},"note":"浪费"},
                {"text":"占为己有","score":-3,"effects":{"reputation":-15},"note":"违纪"},
             ]},
        ],
    },
    # 第二层：军士
    {
        "title":"第二层 · 军士","role":"基层骨干 · 班长",
        "intro":"你是一名老班长，带着一个班。",
        "decisions":[
            {"title":"决策1/6 · 突击路线","text":"两条路：开阔地快；建筑群慢。",
             "choices":[
                {"text":"走建筑群逐屋清剿","score":3,"effects":{"discipline":5,"health":-5},"note":"稳妥"},
                {"text":"走开阔地快速突进","score":0,"effects":{"health":-10},"note":"伤亡大"},
                {"text":"分兵两路","score":-1,"effects":{"tactics":4},"note":"分散"},
                {"text":"无人机侦察后再定","score":3,"effects":{"tactics":6,"health":-2},"note":"情报优势"},
             ]},
            {"title":"决策2/6 · 敌方舰队","text":"敌方航母战斗群接近。",
             "choices":[
                {"text":"加快进攻速度","score":3,"effects":{"tactics":5},"note":"抢时间"},
                {"text":"请示上级","score":1,"effects":{"discipline":4},"note":"浪费时间"},
                {"text":"分散隐蔽","score":0,"effects":{"health":-3},"note":"失去战机"},
                {"text":"主动出击","score":3,"effects":{"tactics":6,"leadership":4,"health":-10},"note":"出其不意"},
             ]},
            {"title":"决策3/6 · 班内矛盾","text":"两个老兵动手了。",
             "choices":[
                {"text":"私下谈话调解","score":3,"effects":{"leadership":5,"relations":{"战友":8}},"note":"以情带兵"},
                {"text":"当场处分","score":1,"effects":{"discipline":5},"note":"严厉"},
                {"text":"战后再说","score":1,"effects":{"tactics":3},"note":"务实"},
                {"text":"上报连部","score":-1,"effects":{"discipline":3},"note":"推卸"},
             ]},
            {"title":"决策4/6 · 弹药告急","text":"弹药消耗过半。",
             "choices":[
                {"text":"组织人员去搬运","score":3,"effects":{"leadership":5,"health":-5},"note":"主动"},
                {"text":"节约弹药","score":2,"effects":{"discipline":5},"note":"稳妥"},
                {"text":"从敌尸上搜集","score":0,"effects":{"tactics":3,"health":-3},"note":"危险"},
                {"text":"继续猛打","score":-3,"effects":{"troop_power":-10},"note":"后患"},
             ]},
            {"title":"决策5/6 · 代理排长","text":"排长牺牲，你代理排长。",
             "choices":[
                {"text":"重新编组明确任务","score":3,"effects":{"leadership":8,"tactics":5},"note":"正确"},
                {"text":"沿袭原部署","score":1,"effects":{"discipline":4},"note":"稳妥"},
                {"text":"让各班长自行指挥","score":-2,"effects":{"leadership":-5},"note":"混乱"},
                {"text":"请求派新排长","score":0,"effects":{"discipline":3},"note":"耽误"},
             ]},
            {"title":"决策6/6 · 俘虏审讯","text":"抓到一名敌军军官。",
             "choices":[
                {"text":"按程序送情报部门","score":3,"effects":{"discipline":5,"intel":2},"note":"标准"},
                {"text":"当场审讯","score":1,"effects":{"tactics":4,"intel":1},"note":"违规"},
                {"text":"答应他的条件","score":-2,"effects":{"reputation":-8},"note":"越权"},
                {"text":"无视继续战斗","score":-1,"note":"错失情报"},
             ]},
        ],
    },
    # 第三层：尉官
    {
        "title":"第三层 · 尉官","role":"连级指挥 · 连长",
        "intro":"你是连长，负责夺取3号高地。",
        "decisions":[
            {"title":"决策1/6 · 攻坚方案","text":"敌军一个加强连，工事坚固。",
             "choices":[
                {"text":"夜间渗透突袭","score":3,"effects":{"tactics":8},"note":"高回报"},
                {"text":"呼叫空中支援","score":3,"effects":{"tactics":6},"note":"依赖空军"},
                {"text":"正面强攻","score":0,"effects":{"troop_power":-10},"note":"伤亡大"},
                {"text":"断水断粮围困","score":2,"effects":{"discipline":5},"note":"耗时"},
             ]},
            {"title":"决策2/6 · 敌军空袭","text":"敌军舰载机飞来。",
             "choices":[
                {"text":"呼叫己方空军拦截","score":3,"effects":{"tactics":6},"note":"正确"},
                {"text":"进入防空洞","score":2,"effects":{"health":-3},"note":"保存实力"},
                {"text":"组织对空射击","score":0,"effects":{"troop_power":-8},"note":"有限"},
                {"text":"分散隐蔽","score":1,"effects":{"health":-5},"note":"减少损失"},
             ]},
            {"title":"决策3/6 · 战俘营","text":"关押数百名我国侨民。",
             "choices":[
                {"text":"立即组织撤离","score":3,"effects":{"reputation":15},"note":"人道"},
                {"text":"登记后移交","score":2,"effects":{"discipline":5},"note":"程序"},
                {"text":"就地补充兵员","score":-3,"effects":{"reputation":-15},"note":"违纪"},
                {"text":"请示上级","score":0,"effects":{"discipline":3},"note":"慢"},
             ]},
            {"title":"决策4/6 · 伤亡过大","text":"伤亡三分之一，要求继续进攻。",
             "choices":[
                {"text":"调整部署重点突破","score":3,"effects":{"tactics":8},"note":"正确"},
                {"text":"向营长报告实情","score":2,"effects":{"discipline":5},"note":"实事求是"},
                {"text":"继续强攻","score":-2,"effects":{"troop_power":-15},"note":"蛮干"},
                {"text":"擅自撤退","score":-3,"effects":{"reputation":-15},"note":"军法不容"},
             ]},
            {"title":"决策5/6 · 敌军反扑","text":"敌军集结残余兵力反扑。",
             "choices":[
                {"text":"诱敌深入两翼包抄","score":3,"effects":{"tactics":10},"note":"高明"},
                {"text":"正面阻击","score":1,"effects":{"discipline":8},"note":"消耗大"},
                {"text":"请求炮火支援","score":2,"effects":{"tactics":5},"note":"稳妥"},
                {"text":"放弃阵地后撤","score":-2,"effects":{"reputation":-10},"note":"丧失主动"},
             ]},
            {"title":"决策6/6 · 情报分析","text":"敌军部署图有矛盾。",
             "choices":[
                {"text":"交叉验证后再用","score":3,"effects":{"tactics":6,"intel":2},"note":"严谨"},
                {"text":"按图行动","score":-1,"effects":{"tactics":3},"note":"可能中计"},
                {"text":"派侦察兵核实","score":2,"effects":{"tactics":5,"intel":1,"health":-3},"note":"稳妥"},
                {"text":"凭经验打","score":-2,"effects":{"reputation":-5},"note":"冒险"},
             ]},
        ],
    },
    # 第四层：校官
    {
        "title":"第四层 · 校官","role":"战役指挥 · 师长",
        "intro":"你是师长，指挥数万部队。",
        "decisions":[
            {"title":"决策1/6 · 主攻方向","text":"参谋部提出四个方向。",
             "choices":[
                {"text":"北线：复杂但敌军薄弱","score":3,"effects":{"tactics":6},"note":"出其不意"},
                {"text":"南线：迂回断敌后路","score":3,"effects":{"tactics":8,"command":5},"note":"战略迂回"},
                {"text":"中线：正面突破","score":0,"effects":{"troop_power":-10},"note":"伤亡大"},
                {"text":"三路并进","score":-1,"effects":{"troop_power":-5},"note":"分散"},
             ]},
            {"title":"决策2/6 · 多国参战","text":"域外大国参战，其盟友配合。",
             "choices":[
                {"text":"请求北方大国牵制","score":3,"effects":{"politics":8},"note":"外交"},
                {"text":"加快进攻速战速决","score":3,"effects":{"tactics":8,"health":-10},"note":"抢时间"},
                {"text":"分兵阻击","score":0,"effects":{"troop_power":-10},"note":"两线风险"},
                {"text":"转入防御","score":-2,"effects":{"morale":-5},"note":"丧失主动"},
             ]},
            {"title":"决策3/6 · 邻国态度","text":"邻国边境异动。",
             "choices":[
                {"text":"外交斡旋","score":3,"effects":{"politics":10},"note":"政治"},
                {"text":"调兵防备","score":1,"effects":{"troop_power":-8},"note":"分散"},
                {"text":"先发制人威慑","score":0,"effects":{"tactics":5},"note":"冒险"},
                {"text":"置之不理","score":-2,"effects":{"health":-5},"note":"风险大"},
             ]},
            {"title":"决策4/6 · 后勤危机","text":"补给线遭潜艇袭击。",
             "choices":[
                {"text":"组织护航编队","score":3,"effects":{"tactics":8},"note":"根本"},
                {"text":"改用空运","score":2,"effects":{"tactics":5},"note":"快但量小"},
                {"text":"就地征集","score":-2,"effects":{"reputation":-10},"note":"民愤"},
                {"text":"缩减补给","score":-1,"effects":{"troop_power":-10},"note":"影响战力"},
             ]},
            {"title":"决策5/6 · 战役转折","text":"敌国主力被围，盟友要求停火。",
             "choices":[
                {"text":"边打边谈","score":3,"effects":{"tactics":10,"politics":8},"note":"正确"},
                {"text":"拒绝谈判彻底歼灭","score":1,"effects":{"tactics":6},"note":"强硬"},
                {"text":"立即停火","score":0,"effects":{"politics":5},"note":"失去战机"},
                {"text":"请示军委","score":1,"effects":{"discipline":5},"note":"稳妥"},
             ]},
            {"title":"决策6/6 · 战役协同","text":"陆海两方主官有分歧。",
             "choices":[
                {"text":"召两方开会协商","score":3,"effects":{"leadership":8,"command":5},"note":"民主"},
                {"text":"按陆军方案打","score":1,"effects":{"tactics":5},"note":"偏袒"},
                {"text":"按海军方案打","score":1,"effects":{"tactics":5},"note":"偏袒"},
                {"text":"让两方自协调","score":-2,"effects":{"leadership":-5},"note":"失职"},
             ]},
        ],
    },
    # 第五层：将官
    {
        "title":"第五层 · 将官","role":"战区指挥 · 战区主官",
        "intro":"你是战区主官。多国势力交汇。",
        "decisions":[
            {"title":"决策1/6 · 多国联军","text":"敌方联合盟友介入。",
             "choices":[
                {"text":"集中兵力各个击破","score":3,"effects":{"command":10,"tactics":8},"note":"经典"},
                {"text":"避实击虚攻击弱敌","score":3,"effects":{"tactics":10,"command":5},"note":"打弱"},
                {"text":"请求北方大国支援","score":2,"effects":{"politics":8},"note":"外交"},
                {"text":"分兵阻击","score":-3,"effects":{"troop_power":-15},"note":"必败"},
             ]},
            {"title":"决策2/6 · 敌方核威胁","text":"敌方发出核威胁。",
             "choices":[
                {"text":"亮明核底牌","score":3,"effects":{"politics":10,"command":8},"note":"核平衡"},
                {"text":"公开核力量部署","score":3,"effects":{"politics":10,"reputation":8},"note":"透明威慑"},
                {"text":"请求国际斡旋","score":2,"effects":{"politics":8},"note":"外交"},
                {"text":"加速进攻","score":-1,"effects":{"tactics":5,"health":-10},"note":"冒险"},
             ]},
            {"title":"决策3/6 · 敌国求和","text":"敌国传递求和信号。",
             "choices":[
                {"text":"要求完全投降","score":3,"effects":{"command":8,"politics":5},"note":"强硬"},
                {"text":"边打边谈","score":3,"effects":{"tactics":10,"politics":8},"note":"正确"},
                {"text":"就地停战","score":2,"effects":{"politics":8},"note":"见好就收"},
                {"text":"拒绝继续进攻","score":1,"effects":{"tactics":5},"note":"彻底胜利"},
             ]},
            {"title":"决策4/6 · 盟国态度","text":"盟国要求战后利益分成。",
             "choices":[
                {"text":"接受条件共同出兵","score":3,"effects":{"politics":10,"command":8},"note":"现实"},
                {"text":"谈判降低条件","score":2,"effects":{"politics":8},"note":"讨价"},
                {"text":"婉拒独立作战","score":0,"effects":{"troop_power":-10},"note":"兵力不足"},
                {"text":"完全依赖盟国","score":-3,"effects":{"reputation":-10},"note":"丧失自主"},
             ]},
            {"title":"决策5/6 · 全球舆论","text":"国际舆论对我方不利。",
             "choices":[
                {"text":"开展公共外交","score":3,"effects":{"politics":12,"reputation":10},"note":"正确"},
                {"text":"公布敌方证据","score":3,"effects":{"politics":8,"reputation":8},"note":"以事实说话"},
                {"text":"加强网络宣传","score":1,"effects":{"politics":5},"note":"辅助"},
                {"text":"无视国际舆论","score":-2,"effects":{"reputation":-10},"note":"自绝"},
             ]},
            {"title":"决策6/6 · 联合指挥","text":"多国部队指挥权有争议。",
             "choices":[
                {"text":"建立联合指挥机构","score":3,"effects":{"command":10,"leadership":8},"note":"最佳"},
                {"text":"我方主导指挥","score":1,"effects":{"command":5},"note":"盟友不满"},
                {"text":"轮流指挥","score":0,"effects":{"discipline":-3},"note":"混乱"},
                {"text":"各自为战","score":-3,"effects":{"troop_power":-15},"note":"灾难"},
             ]},
        ],
    },
    # 第六层：军委副主席
    {
        "title":"第六层 · 军委副主席","role":"最高指挥 · 军委副主席",
        "intro":"军委联合作战指挥中心。你是最高指挥官。",
        "decisions":[
            {"title":"决策1/6 · 战争目标","text":"参谋部提出四个战争目标。",
             "choices":[
                {"text":"威慑目标：重创逼谈","score":3,"effects":{"politics":10,"command":5},"note":"政治"},
                {"text":"全面目标：占领全境","score":3,"effects":{"command":10,"tactics":8},"note":"彻底"},
                {"text":"有限目标：摧毁军力","score":2,"effects":{"tactics":8},"note":"稳妥"},
                {"text":"区域目标：缓冲区","score":1,"effects":{"politics":8},"note":"折中"},
             ]},
            {"title":"决策2/6 · 核武器","text":"敌方核力量最高戒备。",
             "choices":[
                {"text":"提升至同等戒备","score":3,"effects":{"command":8,"politics":5},"note":"对等"},
                {"text":"公开核力量部署","score":3,"effects":{"politics":10,"reputation":8},"note":"透明"},
                {"text":"秘密提升戒备","score":2,"effects":{"tactics":5},"note":"低调"},
                {"text":"不提升避免刺激","score":-3,"effects":{"politics":-5},"note":"示弱"},
             ]},
            {"title":"决策3/6 · 战后秩序","text":"战争即将结束。",
             "choices":[
                {"text":"推动多国和谈","score":3,"effects":{"politics":15,"reputation":10},"note":"大国担当"},
                {"text":"不干涉内政撤军","score":3,"effects":{"reputation":15},"note":"道义"},
                {"text":"扶持新政权","score":1,"effects":{"politics":8},"note":"现实"},
                {"text":"长期驻军","score":-1,"effects":{"reputation":-10},"note":"霸权"},
             ]},
            {"title":"决策4/6 · 盟友关系","text":"盟国要求共享技术。",
             "choices":[
                {"text":"部分共享核心","score":3,"effects":{"politics":10,"tactics":5},"note":"平衡"},
                {"text":"完全共享","score":1,"effects":{"politics":5,"tech":-5},"note":"代价大"},
                {"text":"拒绝共享","score":-1,"effects":{"politics":-5,"reputation":5},"note":"影响"},
                {"text":"谈判交换条件","score":3,"effects":{"politics":8,"command":5},"note":"务实"},
             ]},
            {"title":"决策5/6 · 军队改革","text":"战后军队面临改革。",
             "choices":[
                {"text":"推动编制体制改革","score":3,"effects":{"command":10,"politics":8},"note":"长远"},
                {"text":"加强科技强军","score":3,"effects":{"tactics":10,"tech":8},"note":"未来"},
                {"text":"维持现状","score":0,"effects":{"discipline":3},"note":"保守"},
                {"text":"大规模裁军","score":-3,"effects":{"troop_power":-15},"note":"自削"},
             ]},
            {"title":"决策6/6 · 历史定位","text":"你将被历史如何评价？",
             "choices":[
                {"text":"接受欢呼","score":2,"effects":{"reputation":8},"note":"常情"},
                {"text":"归功于全体将士","score":3,"effects":{"reputation":15,"leadership":8},"note":"大将"},
                {"text":"告慰先烈","score":3,"effects":{"politics":12,"reputation":12},"note":"不忘本"},
                {"text":"保持低调","score":1,"effects":{"discipline":5},"note":"谦虚"},
             ]},
        ],
    },
]

SUNSET_NATIONS = {
    "我国":{"role":"我方","desc":"祖国"},
    "敌国A":{"role":"主要敌国","desc":"岛国，主要攻击目标"},
    "域外大国B":{"role":"域外干预大国","desc":"远洋强国，航母战斗群"},
    "盟友C":{"role":"B国盟友","desc":"地区中等强国"},
    "邻国D":{"role":"邻近中立国","desc":"态度暧昧"},
    "北方大国E":{"role":"北方大国","desc":"与我方战略协作"},
}

EVENTS = [
    {"title":"抗洪抢险","text":"驻地洪水，部队紧急出动。",
     "choices":[
        {"text":"冲在最前面","effects":{"reputation":10,"leadership":5,"health":-15,"morale":5,"reward_score":8}},
        {"text":"服从安排","effects":{"reputation":3,"health":-8,"reward_score":3}},
        {"text":"留在后方","effects":{"reputation":-6,"reward_score":-2}}]},
    {"title":"五公里比武","text":"团里组织五公里比武。",
     "choices":[
        {"text":"拼尽全力","effects":{"fitness":8,"reputation":5,"health":-12,"morale":3,"reward_score":6}},
        {"text":"保存体力","effects":{"fitness":2,"reward_score":1}},
        {"text":"称病不去","effects":{"reputation":-5,"reward_score":-3}}]},
    {"title":"见义勇为","text":"休假途中遇到歹徒抢劫。",
     "choices":[
        {"text":"挺身而出","effects":{"reputation":8,"morale":5,"health":-10,"reward_score":10}},
        {"text":"报警后离开","effects":{"reputation":3,"reward_score":2}}]},
    {"title":"军事演习","text":"年度大演习，你部担任主攻。",
     "choices":[
        {"text":"主动请缨当尖刀","effects":{"tactics":8,"reputation":8,"health":-15,"reward_score":12}},
        {"text":"稳扎稳打","effects":{"tactics":5,"reputation":5,"health":-5,"reward_score":5}},
        {"text":"保守执行","effects":{"tactics":2,"reward_score":1}}]},
]

def clamp(v,lo=0,hi=100): return max(lo,min(hi,v))

def apply_effects(state,effects):
    if not effects: return
    for k,v in effects.items():
        if k=="relations":
            for n,val in v.items():
                state.setdefault("relations",{}).setdefault(n,50)
                state["relations"][n]=clamp(state["relations"][n]+val)
        elif k=="money": state["money"]+=v
        elif k=="medal":
            state.setdefault("medals",{})
            state["medals"][v]=state["medals"].get(v,0)+1
            state["promo_points"]=state.get("promo_points",0)+MEDAL_POINTS.get(v,0)
        elif k=="reward_score":
            state["reward_score"]=state.get("reward_score",0)+v
        else:
            state[k]=clamp(state.get(k,0)+v,0,200)

def promotion_score(s):
    route=s.get("route") or "指挥路线"
    if route=="技术路线":
        base=s.get("tech",0)*0.3+s["tactics"]*0.2+s["reputation"]*0.2+s.get("tech_points",0)*0.1
    elif route=="政工路线":
        base=s.get("pol_work",0)*0.3+s["politics"]*0.2+s["reputation"]*0.2+s.get("thought",50)*0.1
    else:
        base=s.get("command",0)*0.25+s["tactics"]*0.2+s["leadership"]*0.2+s.get("troop_power",0)*0.15
    return base+s.get("promo_points",0)*3

def promotion_threshold(idx):
    base=35+idx*8
    t=RANK_TYPE[idx]
    if t=="军士": base+=5
    elif t=="尉官": base+=10
    elif t=="校官": base+=15
    elif t=="将官": base+=25
    return base

def get_rank_image(idx, at_war=False):
    if idx<=8: base="soldier"
    elif idx<=11: base="officer"
    elif idx<=14: base="field_officer"
    elif idx<=17: base="general"
    else: base="supreme"
    if at_war:
        war_file=f"{base}_war.png"
        if os.path.exists(os.path.join(IMG_DIR,war_file)):
            return war_file
    return f"{base}.png"

def img_exists(name):
    return os.path.exists(os.path.join(IMG_DIR,name))

def relation_desc(value):
    if value>=85: return "亲密"
    elif value>=70: return "良好"
    elif value>=50: return "一般"
    elif value>=30: return "淡薄"
    else: return "紧张"

def get_hospital(rank_idx,health):
    if rank_idx>=15: return "总医院"
    elif rank_idx>=12: return "军队中心医院"
    elif rank_idx>=9: return "旅（团）医院"
    elif rank_idx>=4: return "营卫生所"
    else: return "连卫生队"

def calc_bmi(height_cm,weight_kg):
    h=height_cm/100
    return round(weight_kg/(h*h),1)

def check_recruitment_time():
    month=datetime.now().month
    if month in (12,1,2): return "上半年征兵季"
    elif month in (7,8): return "下半年征兵季"
    else: return "征兵宣传期"


class MusicManager:
    def __init__(self):
        self.current = None
        self.current_name = None

    def play(self, name):
        if self.current_name == name:
            return
        if self.current:
            try:
                self.current.stop()
            except:
                pass
        path = os.path.join(MUSIC_DIR, name)
        print(f"[音乐] 尝试加载: {path}")
        if not os.path.exists(path):
            print(f"[音乐] 文件不存在")
            self.current = None
            self.current_name = None
            return
        try:
            sound = SoundLoader.load(path)
            print(f"[音乐] 加载结果: {sound}")
            if sound:
                sound.loop = True
                sound.play()
                self.current = sound
                self.current_name = name
                print(f"[音乐] 播放成功: {name}")
            else:
                print(f"[音乐] 加载返回 None（格式可能不兼容）")
        except Exception as e:
            print(f"[音乐] 异常: {e}")

class GameScreen(FloatLayout):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.state=None
        self.name_input=None
        self.war_round=0
        self.music=MusicManager()
        self.build_ui()
        self.show_start()

    def build_ui(self):
        if img_exists("background.png"):
            bg=Image(source=os.path.join(IMG_DIR,"background.png"),
                     allow_stretch=True,keep_ratio=False,
                     size_hint=(1,1),pos_hint={"x":0,"y":0})
            self.add_widget(bg)
        container=BoxLayout(orientation='vertical',padding=15,spacing=10,size_hint=(1,1))
        self.add_widget(container)
        top=BoxLayout(orientation='horizontal',size_hint=(1,0.08),spacing=10)
        if img_exists("logo.png"):
            logo=Image(source=os.path.join(IMG_DIR,"logo.png"),
                       size_hint=(None,1),width=60,allow_stretch=True,keep_ratio=True)
            top.add_widget(logo)
        self.status=Label(text="",font_name='Chinese',font_size='13sp',
                          color=(0.9,0.9,0.9,1),halign='left',valign='middle',size_hint=(1,1))
        self.status.bind(size=lambda *x:setattr(self.status,'text_size',(self.status.width,None)))
        top.add_widget(self.status)
        container.add_widget(top)

        mid=BoxLayout(orientation='horizontal',size_hint=(1,0.7),spacing=15)
        with mid.canvas.before:
            Color(0.05,0.08,0.12,0.85)
            self._mid_bg=Rectangle(pos=mid.pos,size=mid.size)
        mid.bind(pos=lambda *x:setattr(self._mid_bg,'pos',mid.pos),
                 size=lambda *x:setattr(self._mid_bg,'size',mid.size))
        self.portrait=Image(source="",size_hint=(None,1),width=380,allow_stretch=True,keep_ratio=True)
        mid.add_widget(self.portrait)
        scroll=ScrollView(size_hint=(1,1))
        self.text=Label(text="",font_name='Chinese',font_size='15sp',
                        color=(0.95,0.95,0.95,1),size_hint_y=None,size_hint_x=1,
                        halign='left',valign='top',padding=(20,20))
        self.text.bind(width=lambda *x:setattr(self.text,'text_size',(self.text.width,None)),
                       texture_size=lambda *x:setattr(self.text,'height',self.text.texture_size[1]))
        scroll.add_widget(self.text)
        mid.add_widget(scroll)
        container.add_widget(mid)

        choices_wrap=BoxLayout(orientation='vertical',size_hint=(1,0.22))
        with choices_wrap.canvas.before:
            Color(0.05,0.08,0.12,0.85)
            self._choice_bg=Rectangle(pos=choices_wrap.pos,size=choices_wrap.size)
        choices_wrap.bind(pos=lambda *x:setattr(self._choice_bg,'pos',choices_wrap.pos),
                          size=lambda *x:setattr(self._choice_bg,'size',choices_wrap.size))
        self.choices_scroll=ScrollView(size_hint=(1,1))
        self.choices=BoxLayout(orientation='vertical',size_hint_y=None,spacing=5)
        self.choices.bind(minimum_height=self.choices.setter('height'))
        self.choices_scroll.add_widget(self.choices)
        choices_wrap.add_widget(self.choices_scroll)
        container.add_widget(choices_wrap)

    def set_portrait(self,name):
        if name and img_exists(name):
            self.portrait.source=os.path.join(IMG_DIR,name)
        else: self.portrait.source=""

    def update_status(self):
        s=self.state
        if not s: self.status.text=""; return
        rank=RANKS[s["rank_index"]]
        route=s.get("route") or "未定"
        army=s.get("army") or "未定"
        province=s.get("province") or "未定"
        medals=s.get("medals",{})
        medal_str=" ".join([f"{k}×{v}" for k,v in medals.items() if v]) or "无"
        extra=""
        if s.get("in_hospital"): extra=f" | 【住院：{s.get('hospital_name','未知')}】"
        if s.get("at_war"): extra+=f" | 【战时】"
        self.status.text=(
            f"【{s['name']}】{rank} | {province}·{army} | {s['age']}岁 {s['years']}年兵 | {route}{extra}\n"
            f"体能{s['fitness']} 战术{s['tactics']} 领导{s['leadership']} 声望{s['reputation']} "
            f"健康{s['health']} | 表现分{s.get('reward_score',0)} | 勋章:{medal_str}" +
            (f"\n恋人：{s['lover']['name']}（好感{s.get('lover_affection',0)}）" if s.get("lover") else "") +
            (" 已婚" if s.get("married") else "") +
            (f" 子女{s['children']}人" if s.get("children",0)>0 else "") +
            (f" | 成就{len(s.get('achievements',{}))}/{len(ACHIEVEMENTS)}"))
        at_war=s.get("at_war",False)
        self.set_portrait(get_rank_image(s["rank_index"], at_war))

    def clear_choices(self): self.choices.clear_widgets()

    def add_choice(self,text,callback):
        btn=Button(text=text,font_name='Chinese',font_size='14sp',
                   background_color=(0.15,0.2,0.3,0.9),background_normal='',
                   size_hint_y=None,height=75)
        btn.bind(on_press=lambda *x:callback())
        self.choices.add_widget(btn)

    # ========== 开场 ==========
    def show_start(self):
        self.music.play("enlist.wav")
        season=check_recruitment_time()
        self.text.text=(
            "荣勋之路\n\n"
            "【免责声明】\n"
            "本游戏为虚拟世界设定，与现实无关。\n\n"
            f"【当前：{season}】\n"
            f"时间：{datetime.now().strftime('%Y年%m月')}\n\n"
            "请输入姓名，选择学历：")
        self.set_portrait("uniform.png")
        self.clear_choices()
        self.name_input=TextInput(text="张伟",font_name='Chinese',font_size='15sp',
                                  multiline=False,size_hint_y=None,height=45,
                                  background_color=(0.15,0.2,0.3,0.9),
                                  foreground_color=(1,1,1,1),cursor_color=(1,1,1,1),
                                  padding=(10,10))
        self.choices.add_widget(self.name_input)
        for edu,min_age,max_age in EDUCATION_LEVELS:
            self.add_choice(f"{edu}（{min_age}-{max_age}岁）",
                            lambda e=edu,ma=min_age,xa=max_age: self.step1_register(e,ma,xa))

    def step1_register(self,education,min_age,max_age):
        name="张伟"
        if self.name_input: name=self.name_input.text.strip() or "张伟"
        age=random.randint(min_age,min(max_age,min_age+2))
        self.state={
            "name":name,"age":age,"years":0,"quarter":1,"rank_index":0,
            "fitness":50,"tactics":50,"leadership":50,"politics":50,"discipline":50,
            "morale":70,"reputation":20,"health":100,"money":1000,
            "tech":0,"pol_work":0,"command":0,"thought":50,"org":50,
            "troop_power":0,"tech_points":0,
            "relations":{"班长":50,"连长":50,"政委":50,"战友":50},
            "medals":{},"promo_points":0,"reward_score":0,
            "route":None,"army":None,"province":None,
            "education":education,
            "in_hospital":False,"hospital_name":None,"hospital_days":0,
            "review_score":0,"enlisted":False,"retry_count":0,
            "at_war":False,"war_done":False,"sacrifice":False,
        }
        self.text.text=(
            f"【征兵流程 · 第1步：兵役登记】\n\n"
            f"━━━━━━━━━━━━━━━━━\n"
            f"姓名：{name}\n学历：{education}\n年龄：{age}周岁\n"
            f"━━━━━━━━━━━━━━━━━\n\n"
            f"兵役登记已完成。")
        self.update_status()
        self.clear_choices()
        self.add_choice("下一步：网上报名",self.step2_online)

    def step2_online(self):
        self.text.text=(
            f"【征兵流程 · 第2步：网上报名】\n\n"
            f"登录全国征兵网（www.gfbzb.gov.cn）。\n\n"
            f"报名时间：\n  · 上半年：1月10日 - 2月10日\n  · 下半年：8月10日 - 9月10日\n\n"
            f"━━━━━━━━━━━━━━━━━\n报名信息已提交。")
        self.clear_choices()
        self.add_choice("下一步：初审初检",self.step3_initial_check)

    def step3_initial_check(self):
        s=self.state
        height=random.randint(162,185)
        base_weight=height-105+random.randint(-10,15)
        bmi=calc_bmi(height,base_weight)
        left_eye=round(random.uniform(4.3,5.2),1)
        right_eye=round(random.uniform(4.3,5.2),1)
        s["physical"]={"height":height,"weight":base_weight,"bmi":bmi,
                       "left_eye":left_eye,"right_eye":right_eye}
        problems=[]
        if height<160: problems.append(f"身高{height}cm＜160cm")
        if bmi<17.5: problems.append(f"BMI{bmi}＜17.5（偏瘦）")
        if bmi>=30: problems.append(f"BMI{bmi}≥30（超重）")
        if min(left_eye,right_eye)<4.5: problems.append(f"裸眼视力低于4.5")
        text=(
            f"【征兵流程 · 第3步：初审初检】\n\n"
            f"━━━━━━━━━━━━━━━━━\n"
            f"  身高：{height} cm\n  体重：{base_weight} kg\n"
            f"  BMI：{bmi}\n  左眼：{left_eye}\n  右眼：{right_eye}\n"
            f"━━━━━━━━━━━━━━━━━\n\n"
            f"【标准】身高≥160cm，17.5≤BMI＜30，视力≥4.5\n\n")
        if problems:
            text+="【初检结果】❌ 不合格\n\n"
            for p in problems: text+=f"  ✗ {p}\n"
            self.text.text=text
            self.clear_choices()
            self.add_choice("加强锻炼，1个月后复检",self.retry_physical)
            self.add_choice("走特批渠道（需声望≥25）",self.special_channel)
            self.add_choice("放弃从军",self.give_up)
        else:
            text+="【初检结果】✅ 合格"
            self.text.text=text
            self.clear_choices()
            self.add_choice("下一步：体格检查",self.step4_medical)

    def retry_physical(self):
        s=self.state
        s["retry_count"]=s.get("retry_count",0)+1
        if s["retry_count"]>3:
            self.text.text="【复检失败】\n\n已经复检3次，本年度不再受理。"
            self.clear_choices()
            self.add_choice("明年再来",self.show_start)
            self.add_choice("放弃从军",self.give_up); return
        s["fitness"]=clamp(s["fitness"]+5,0,200)
        s["health"]=clamp(s["health"]-3,0,200)
        if random.random()<0.6:
            self.text.text="【复检结果】✅ 合格\n\n经过锻炼，你通过了复检。"
            self.update_status()
            self.clear_choices()
            self.add_choice("下一步：体格检查",self.step4_medical)
        else:
            self.text.text=f"【复检结果】❌ 仍不合格（第 {s['retry_count']} 次）"
            self.clear_choices()
            self.add_choice("再锻炼一次",self.retry_physical)
            self.add_choice("走特批渠道",self.special_channel)
            self.add_choice("放弃从军",self.give_up)

    def special_channel(self):
        s=self.state
        if s["reputation"]>=25:
            self.text.text="【特批渠道】\n\n✅ 组织批准了你的特批申请。"
            self.update_status()
            self.clear_choices()
            self.add_choice("继续体格检查",self.step4_medical)
        else:
            self.text.text=f"【特批被拒】\n\n声望不足（{s['reputation']}/25）"
            self.clear_choices()
            self.add_choice("加强锻炼再试",self.retry_physical)
            self.add_choice("放弃从军",self.give_up)

    def step4_medical(self):
        s=self.state
        p=s["physical"]
        final_height=p["height"]+random.randint(-2,2)
        final_bmi=p["bmi"]+random.uniform(-0.5,0.5)
        final_eye=min(p["left_eye"],p["right_eye"])+random.uniform(-0.2,0.1)
        problems=[]
        if final_height<160: problems.append("身高不足")
        if final_bmi<17.5 or final_bmi>=30: problems.append("BMI不合格")
        if final_eye<4.5: problems.append("视力不合格")
        hidden_issue=None
        if random.random()<0.2:
            hidden_issue=random.choice(["心电图轻微异常","血压偏高","肝功指标偏高","扁平足"])
        text=(
            f"【征兵流程 · 第4步：体格检查】\n\n"
            f"━━━━━━━━━━━━━━━━━\n"
            f"  身高：{final_height} cm\n  BMI：{final_bmi:.1f}\n  视力：{final_eye:.1f}\n"
            f"  内科/外科/五官科：正常\n"
            f"  心电图：{'轻微异常' if hidden_issue=='心电图轻微异常' else '正常'}\n"
            f"  B超/血液：正常\n"
            f"━━━━━━━━━━━━━━━━━\n\n")
        if problems or hidden_issue:
            text+="【体检结论】❌ 不合格\n\n"
            for p2 in problems: text+=f"  ✗ {p2}\n"
            if hidden_issue: text+=f"  ⚠ {hidden_issue}\n"
            self.text.text=text
            self.clear_choices()
            self.add_choice("申请复检（50%通过）",self.retry_medical)
            self.add_choice("上级医院复查（声望≥30）",self.upper_hospital_check)
            self.add_choice("放弃从军",self.give_up)
        else:
            text+="【体检结论】✅ 合格"
            self.text.text=text
            self.clear_choices()
            self.add_choice("下一步：政治考核",self.step5_political)

    def retry_medical(self):
        if random.random()<0.5:
            self.text.text="【复检】✅ 合格"
            self.clear_choices()
            self.add_choice("下一步：政治考核",self.step5_political)
        else:
            self.text.text="【复检】❌ 仍不合格"
            self.clear_choices()
            self.add_choice("上级医院复查",self.upper_hospital_check)
            self.add_choice("放弃从军",self.give_up)

    def upper_hospital_check(self):
        s=self.state
        if s["reputation"]>=30:
            self.text.text="【上级医院复查】\n\n✅ 专家会诊通过。"
            self.clear_choices()
            self.add_choice("下一步：政治考核",self.step5_political)
        else:
            self.text.text=f"【复查被拒】\n\n声望不足（{s['reputation']}/30）"
            self.clear_choices()
            self.add_choice("放弃从军",self.give_up)

    def step5_political(self):
        s=self.state
        base_score=60
        if s["education"] in ("大专","本科","研究生"): base_score+=10
        score=base_score+random.randint(-25,25)
        text=(f"【征兵流程 · 第5步：政治考核】\n\n"
              f"考核内容：政治思想、道德品质、社会关系。\n\n"
              f"━━━━━━━━━━━━━━━━━\n")
        if score>=60:
            text+=f"  政治考核：✅ 通过\n  综合评分：{score}分"
            self.text.text=text
            self.clear_choices()
            self.add_choice("下一步：役前教育",self.step6_training)
        else:
            text+=f"  政治考核：❌ 需要进一步审查\n  综合评分：{score}分"
            self.text.text=text
            self.clear_choices()
            self.add_choice("补充材料（政工+3）",self.retry_political)
            self.add_choice("请村/居委会出具证明",self.retry_with_proof)
            self.add_choice("放弃从军",self.give_up)

    def retry_political(self):
        s=self.state
        s["politics"]=clamp(s["politics"]+3,0,200)
        if random.random()<0.7:
            self.text.text="【补充材料后】✅ 通过"
            self.clear_choices()
            self.add_choice("下一步：役前教育",self.step6_training)
        else:
            self.text.text="【补充材料后】❌ 仍有疑点"
            self.clear_choices()
            self.add_choice("村/居委会证明",self.retry_with_proof)
            self.add_choice("放弃从军",self.give_up)

    def retry_with_proof(self):
        if random.random()<0.85:
            self.text.text="【证明材料提交后】✅ 通过"
            self.clear_choices()
            self.add_choice("下一步：役前教育",self.step6_training)
        else:
            self.text.text="【仍不通过】"
            self.clear_choices()
            self.add_choice("放弃从军",self.give_up)

    def step6_training(self):
        s=self.state
        self.text.text=(
            f"【征兵流程 · 第6步：役前教育】\n\n"
            f"时间不少于7天。\n\n"
            f"教育内容：思想教育、军事训练、法规学习、国防教育。\n\n"
            f"你的表现：")
        self.clear_choices()
        roll=random.random()
        if roll<0.6:
            name,desc,effects="优秀","队列标兵，班长点名表扬",{"fitness":5,"discipline":5,"morale":5}
        elif roll<0.9:
            name,desc,effects="良好","训练认真，表现稳定",{"fitness":3,"discipline":3}
        else:
            name,desc,effects="不合格","训练消极，被点名批评",{"fitness":1,"discipline":-3,"morale":-3}
        apply_effects(self.state,effects)
        self.text.text+=f"\n  {name} —— {desc}\n\n"
        if name=="不合格":
            self.text.text+="【役前教育淘汰】\n\n被列入淘汰名单，可申诉一次。"
            self.clear_choices()
            self.add_choice("申诉（写检讨）",self.appeal_training)
            self.add_choice("接受淘汰",self.give_up)
        else:
            self.text.text+="役前教育结束。"
            self.clear_choices()
            self.add_choice("下一步：审批定兵",self.step7_approval)

    def appeal_training(self):
        if random.random()<0.6:
            self.text.text="【申诉成功】\n\n✅ 继续参加审批定兵。"
            self.clear_choices()
            self.add_choice("下一步：审批定兵",self.step7_approval)
        else:
            self.text.text="【申诉失败】"
            self.clear_choices()
            self.add_choice("放弃从军",self.give_up)

    def step7_approval(self):
        s=self.state
        self.text.text=(
            f"【征兵流程 · 第7步：审批定兵】\n\n"
            f"县征兵办集体研究，择优批准入伍对象。\n\n"
            f"【定兵原则】\n"
            f"  1. 优先批准学历高的青年\n"
            f"  2. 优先批准应届毕业生\n"
            f"  3. 优先批准表现突出者\n\n"
            f"━━━━━━━━━━━━━━━━━\n审批结果：")
        self.clear_choices()
        if s["education"] in ("本科","研究生","大专"):
            if random.random()<0.95:
                self.approve_enlist(s,"优先批准","你是大学生，优先批准对象。")
            else:
                self.reject_approval(s)
        elif s["reward_score"]>=5:
            if random.random()<0.9:
                self.approve_enlist(s,"批准入伍","你在役前教育表现突出。")
            else:
                self.reject_approval(s)
        else:
            if random.random()<0.75:
                self.approve_enlist(s,"批准入伍","你被批准入伍。")
            else:
                self.reject_approval(s)

    def approve_enlist(self,s,result,desc):
        self.text.text+=f"\n  ✅ {result}\n\n  {desc}\n\n"
        self.text.text+=(
            f"━━━━━━━━━━━━━━━━━\n"
            f"【批准入伍】\n  · {s['name']}\n  · {s['education']}\n  · {s['age']}周岁\n"
            f"━━━━━━━━━━━━━━━━━\n\n"
            f"你正式成为一名光荣的中国人民解放军军人！")
        s["enlisted"]=True
        self.clear_choices()
        self.add_choice("公示后前往部队",self.step8_enlist)

    def reject_approval(self,s):
        self.text.text+="\n  ❌ 未获批准\n\n因名额限制，未被批准入伍。"
        self.clear_choices()
        self.add_choice("申请纳入候补名单",self.waiting_list)
        self.add_choice("明年再试",self.show_start)
        self.add_choice("放弃从军",self.give_up)

    def waiting_list(self):
        if random.random()<0.4:
            self.text.text="【候补成功】\n\n✅ 被递补为正式入伍对象！"
            self.state["enlisted"]=True
            self.clear_choices()
            self.add_choice("前往部队",self.step8_enlist)
        else:
            self.text.text="【候补未果】\n\n名额已满。"
            self.clear_choices()
            self.add_choice("明年再试",self.show_start)
            self.add_choice("放弃从军",self.give_up)

    def step8_enlist(self):
        self.text.text=(
            f"【征兵流程 · 第8步：公开公示】\n\n"
            f"公示期不少于5天，未收到异议。\n\n"
            f"━━━━━━━━━━━━━━━━━\n"
            f"【起运新兵】\n"
            f"你戴上大红花，登上开往部队的列车。\n\n"
            f"【选择入伍省份】")
        self.update_status()
        self.clear_choices()
        for name,attrs in PROVINCES:
            attr_str=" ".join([f"{k}+{v}" for k,v in attrs.items()])
            self.add_choice(f"{name}  [{attr_str}]",
                            lambda n=name,a=attrs: self.pick_province(n,a))

    def pick_province(self,province,attrs):
        self.state["province"]=province
        apply_effects(self.state,attrs)
        self.text.text=f"籍贯登记：{province}\n\n籍贯加成已应用。\n\n【选择兵种】"
        self.update_status()
        self.show_army_select()

    def show_army_select(self):
        self.clear_choices()
        for name in ARMIES:
            self.add_choice(f"{name}",lambda n=name: self.pick_army(n))

    def pick_army(self,army):
        self.state["army"]=army
        apply_effects(self.state,ARMIES[army])
        self.text.text=f"兵种确定：{army}\n\n【选择发展路线】"
        self.update_status()
        self.show_route_select()

    def show_route_select(self):
        self.clear_choices()
        for name,info in ROUTES.items():
            self.add_choice(f"{name} — {info['desc']}",lambda n=name: self.pick_route(n))

    def pick_route(self,route):
        self.state["route"]=route
        self.text.text=f"路线确定：{route}\n\n新兵连结束了。"
        self.update_status()
        Clock.schedule_once(lambda dt: self.advance_time(),0.5)

    def give_up(self):
        self.text.text=(
            f"【无缘军旅】\n\n"
            f"你最终没能通过征兵选拔。\n\n"
            f"【结局：平民英雄】\n\n"
            f"报效祖国的方式不止一种。")
        self.clear_choices()
        self.add_choice("重新开始",self.show_start)

    # ========== 行动菜单 ==========
    def show_actions(self):
        s=self.state
        if s.get("in_hospital"):
            self.show_hospital(); return
        self.music.play("daily.wav")
        self.text.text=(f"第{s['years']}年 第{s['quarter']}季度 · {RANKS[s['rank_index']]}\n\n选择行动：")
        self.update_status()
        self.clear_choices()
        tasks=BASE_TASKS.get(s["rank_index"],[])
        route=s.get("route")
        if s["rank_index"]>=4 and route in ROUTE_TASKS:
            for lvl in range(s["rank_index"],3,-1):
                if lvl in ROUTE_TASKS[route]:
                    tasks=ROUTE_TASKS[route][lvl]; break
        if not tasks: tasks=BASE_TASKS[3]
        for t in tasks:
            self.add_choice(f"{t['name']}：{t['desc']}",lambda task=t: self.do_task(task))
        self.add_choice("休息调整（健康+8 士气+6）",
                        lambda: self.do_task({"name":"休息调整","desc":"好好睡一觉。",
                                              "effects":{"health":8,"morale":6}}))
        self.add_choice("【个人】成就",self.show_achievements)
        self.add_choice("【个人】感情生活",self.show_love_menu)
        self.add_choice("【个人】遗书管理",self.show_letter_menu)
        self.add_choice("【人际】联络感情",self.show_contact_menu)
        if s["rank_index"]>=9:
            self.add_choice("【主官】批复下级荣誉",self.show_subordinate_review)
        # 战争触发
        if not s.get("war_done"):
            self.add_choice("【重大】主动请战（前往边境）",self.trigger_war)
        # 落日行动
        if self.check_sunset_trigger():
            self.add_choice("【决战】落日行动 · 马踏东京赏樱花",self.trigger_sunset)
        self.add_choice("申请退伍",self.retire)

    def show_contact_menu(self):
        self.text.text="【联络感情】\n\n选择你想联络的对象："
        self.clear_choices()
        for name,info in RELATION_TARGETS.items():
            cur=self.state["relations"].get(name,50)
            self.add_choice(f"{name}（{relation_desc(cur)}，{cur}）",lambda n=name: self.contact(n))
        self.add_choice("返回",self.show_actions)

    def contact(self,target):
        s=self.state
        cur=s["relations"].get(target,50)
        gain=random.randint(3,8)
        s["relations"][target]=clamp(cur+gain,0,200)
        s["morale"]=clamp(s["morale"]+3,0,200)
        s["reward_score"]=s.get("reward_score",0)+1
        self.text.text=(f"【联络感情 · {target}】\n\n关系 +{gain}，当前 {s['relations'][target]}\n士气 +3")
        self.update_status()
        self.clear_choices()
        self.add_choice("继续",self.show_actions)

    def do_task(self,task):
        apply_effects(self.state,task["effects"])
        self.state["reward_score"]=self.state.get("reward_score",0)+2
        self.text.text=f"【{task['name']}】\n\n{task['desc']}"
        if self.state["health"]<50 and not self.state.get("in_hospital"):
            Clock.schedule_once(lambda dt: self.go_to_hospital(),0.3); return
        if random.random()<0.4:
            Clock.schedule_once(lambda dt: self.trigger_event(random.choice(EVENTS)),0.3)
        else:
            Clock.schedule_once(lambda dt: self.advance_time(),0.3)

    def trigger_event(self,ev):
        if "抗洪" in ev["title"] or "抢险" in ev["title"]:
            self.music.play("war.wav")
        else:
            self.music.play("daily.wav")
        self.text.text=f"【事件】{ev['title']}\n\n{ev['text']}"
        self.clear_choices()
        for c in ev["choices"]:
            self.add_choice(c["text"],lambda ch=c: self.resolve_event(ev,ch))

    def resolve_event(self,ev,choice):
        apply_effects(self.state,choice["effects"])
        self.text.text=f"【{ev['title']}】\n\n你选择了：{choice['text']}"
        self.update_status()
        if self.state["health"]<50 and not self.state.get("in_hospital"):
            Clock.schedule_once(lambda dt: self.go_to_hospital(),0.5); return
        Clock.schedule_once(lambda dt: self.advance_time(),0.5)

    # ========== 战争系统 ==========
    def trigger_war(self):
        s=self.state
        s["at_war"]=True
        self.war_round=0
        self.music.play("war.wav")
        self.update_status()
        self.text.text=(
            f"【战争爆发！】\n\n"
            f"边境突发武装冲突，上级下达紧急作战命令。\n"
            f"全军进入一级战备！\n\n"
            f"身为军人，你义无反顾，随部队开赴前线。\n\n"
            f"━━━━━━━━━━━━━━━━━\n"
            f"你部将经历 5 个阶段的战斗。")
        self.clear_choices()
        self.add_choice("义无反顾，奔赴前线",self.war_next_step)

    def war_next_step(self):
        s=self.state
        if self.war_round>=len(WAR_EVENTS):
            self.finish_war(); return
        ev=WAR_EVENTS[self.war_round]
        self.music.play("war.wav")
        self.text.text=(
            f"【战争 · {ev['title']}】\n\n"
            f"{ev['text']}\n\n"
            f"━━━━━━━━━━━━━━━━━\n"
            f"第 {self.war_round+1}/{len(WAR_EVENTS)} 阶段\n"
            f"当前健康：{s['health']}  部队战力：{s['troop_power']}")
        self.clear_choices()
        for c in ev["choices"]:
            self.add_choice(c["text"],lambda ch=c: self.resolve_war(ch))

    def resolve_war(self,choice):
        s=self.state
        apply_effects(s,choice["effects"])
        self.text.text=f"【战争决策】\n\n你选择了：{choice['text']}"
        self.update_status()
        # 牺牲判定
        if s["health"]<=0 or random.random()<0.05:
            s["sacrifice"]=True
            s["at_war"]=False
            Clock.schedule_once(lambda dt: self.war_sacrifice(),0.5)
            return
        self.war_round+=1
        self.clear_choices()
        self.add_choice("继续推进",self.war_next_step)

    def finish_war(self):
        s=self.state
        s["at_war"]=False
        s["war_done"]=True
        # 战争奖励
        s["medals"]["一等功"]=s["medals"].get("一等功",0)+1
        s["promo_points"]=s.get("promo_points",0)+MEDAL_POINTS["一等功"]
        s["reward_score"]=s.get("reward_score",0)+30
        s["reputation"]=clamp(s["reputation"]+20,0,200)
        self.music.play("promote.wav")
        self.update_status()
        self.text.text=(
            f"【战争结束】\n\n"
            f"你部圆满完成作战任务，击退敌军。\n\n"
            f"━━━━━━━━━━━━━━━━━\n"
            f"【战争奖励】\n"
            f"  荣立：一等功\n"
            f"  表现分 +30\n"
            f"  声望 +20\n"
            f"━━━━━━━━━━━━━━━━━\n\n"
            f"你带着荣誉返回部队。")
        self.clear_choices()
        self.add_choice("返回部队",self.show_actions)

    def war_sacrifice(self):
        s=self.state
        self.music.play("sacrifice.wav")
        rank=RANKS[s["rank_index"]]
        medals_str=" ".join([f"{k}×{v}" for k,v in s.get("medals",{}).items() if v]) or "无"
        self.update_status()
        self.text.text=(
            f"【光荣牺牲】\n\n"
            f"━━━━━━━━━━━━━━━━━\n"
            f"  青山处处埋忠骨\n"
            f"  何须马革裹尸还\n"
            f"━━━━━━━━━━━━━━━━━\n\n"
            f"你以【{rank}】的身份，倒在保卫祖国的前线。\n\n"
            f"战友们擦干眼泪，继续冲锋。\n"
            f"你的名字，将永远刻在连队的荣誉墙上。\n\n"
            f"━━━━━━━━━━━━━━━━━\n"
            f"军龄：{s['years']}年\n"
            f"最终军衔：{rank}\n"
            f"勋章：{medals_str}\n"
            f"━━━━━━━━━━━━━━━━━\n\n"
            f"【追授】荣誉称号（一等功/烈士）")
        self.clear_choices()
        self.add_choice("重新开始",self.show_start)

    # ========== 医院 ==========
    def go_to_hospital(self):
        s=self.state
        s["in_hospital"]=True
        hospital=get_hospital(s["rank_index"],s["health"])
        s["hospital_name"]=hospital
        s["hospital_days"]=0
        info=HOSPITALS[hospital]
        self.music.play("daily.wav")
        self.text.text=(f"【住院治疗】\n\n你因健康恶化（健康 {s['health']}），被送往【{hospital}】。\n\n"
                        f"医院条件：{info['desc']}\n每日恢复：+{info['recover']} 健康")
        self.update_status()
        self.clear_choices()
        self.add_choice("开始住院",self.hospital_next_day)

    def show_hospital(self):
        s=self.state
        info=HOSPITALS.get(s.get("hospital_name"),HOSPITALS["连卫生队"])
        self.text.text=(f"【住院中 · {s.get('hospital_name')}】\n\n"
                        f"当前健康：{s['health']}\n住院天数：{s.get('hospital_days',0)} 天\n"
                        f"每日恢复：+{info['recover']}\n\n健康恢复到 80 才能出院。")
        self.update_status()
        self.clear_choices()
        self.add_choice("休养一天",self.hospital_next_day)
        self.add_choice("申请转院",self.transfer_hospital)

    def hospital_next_day(self):
        s=self.state
        hospital=s.get("hospital_name","连卫生队")
        info=HOSPITALS[hospital]
        s["health"]=clamp(s["health"]+info["recover"],0,200)
        s["hospital_days"]=s.get("hospital_days",0)+1
        s["morale"]=clamp(s["morale"]-1,0,200)
        if s["health"]>=80:
            s["in_hospital"]=False
            s["hospital_done"]=True
            days=s["hospital_days"]
            s["hospital_days"]=0
            s["hospital_name"]=None
            self.text.text=(f"【出院】\n\n经过 {days} 天治疗，你康复出院。\n\n健康：{s['health']}")
            self.update_status()
            self.clear_choices()
            self.add_choice("返回部队",self.advance_time)
        else:
            self.show_hospital()

    def transfer_hospital(self):
        s=self.state
        current=s.get("hospital_name","连卫生队")
        keys=list(HOSPITALS.keys())
        idx=keys.index(current)
        if idx>=len(keys)-1:
            self.text.text="已经是最高等级的医院了。"
            self.clear_choices(); self.add_choice("返回",self.show_hospital); return
        next_hospital=keys[idx+1]
        needed_rank=HOSPITALS[next_hospital]["level"]*2
        if s["rank_index"]<needed_rank:
            self.text.text=(f"【转院被拒】\n\n需要至少 {RANKS[needed_rank]} 军衔。")
            self.clear_choices(); self.add_choice("返回",self.show_hospital); return
        s["hospital_name"]=next_hospital
        info=HOSPITALS[next_hospital]
        self.text.text=(f"【转院成功】\n\n你转到了【{next_hospital}】。\n每日恢复：+{info['recover']}")
        self.update_status()
        self.clear_choices()
        self.add_choice("继续住院",self.hospital_next_day)

    # ========== 民主评议 ==========
    def show_democratic_review(self):
        s=self.state
        self.music.play("promote.wav")
        base=(s["relations"].get("战友",50)*0.4+s["relations"].get("班长",50)*0.2+
              s["relations"].get("连长",50)*0.2+s["reputation"]*0.2)
        score=base+random.randint(-15,15)
        if score>=85:
            level="优秀"; desc="战士们一致认为你德才兼备。"
            rep_gain=8; rel_gain=5
        elif score>=65:
            level="良好"; desc="战士们对你评价不错。"
            rep_gain=4; rel_gain=2
        elif score>=40:
            level="合格"; desc="评价中规中矩。"
            rep_gain=0; rel_gain=0
        else:
            level="不合格"; desc="战士们对你意见很大。"
            rep_gain=-8; rel_gain=-8
        s["reputation"]=clamp(s["reputation"]+rep_gain,0,200)
        for k in s["relations"]:
            s["relations"][k]=clamp(s["relations"][k]+rel_gain,0,200)
        s["review_score"]=score
        self.text.text=(f"【民主评议会】\n\n━━━━━━━━━━━━━━━\n【评议结果】{level}\n━━━━━━━━━━━━━━━\n\n"
                        f"{desc}\n\n综合得分：{score:.1f}\n声望 {rep_gain:+d}\n所有关系 {rel_gain:+d}")
        self.update_status()
        self.clear_choices()
        self.add_choice("继续 · 年度考核",self.annual_review_body)

    # ========== 主官批复 ==========
    def show_subordinate_review(self):
        sub_name=random.choice(SUBORDINATE_NAMES)
        self.text.text=(f"【主官批复下级荣誉】\n\n你的部下 {sub_name} 表现突出，请批复：")
        self.clear_choices()
        self.add_choice(f"批准嘉奖 {sub_name}",lambda: self.approve_reward(sub_name,"嘉奖",-2,3,2))
        self.add_choice(f"批准三等功 {sub_name}",lambda: self.approve_reward(sub_name,"三等功",-5,5,3))
        self.add_choice(f"暂不批准 {sub_name}",lambda: self.reject_reward(sub_name))

    def approve_reward(self,name,medal,rep_cost,morale_gain,leadership_gain):
        s=self.state
        s["reputation"]=clamp(s["reputation"]+rep_cost,0,200)
        s["morale"]=clamp(s["morale"]+morale_gain,0,200)
        s["leadership"]=clamp(s["leadership"]+leadership_gain,0,200)
        s["relations"]["战友"]=clamp(s["relations"].get("战友",50)+3,0,200)
        self.text.text=(f"【批复】✅ 批准了 {name} 的【{medal}】。\n\n"
                        f"声望 {rep_cost:+d}，士气 {morale_gain:+d}，领导 {leadership_gain:+d}，战友 +3")
        self.update_status()
        Clock.schedule_once(lambda dt: self.advance_time(),0.5)

    def reject_reward(self,name):
        s=self.state
        s["relations"]["战友"]=clamp(s["relations"].get("战友",50)-5,0,200)
        self.text.text=(f"【批复】❌ 驳回了 {name} 的评功请求。\n\n战友关系 -5")
        self.update_status()
        Clock.schedule_once(lambda dt: self.advance_time(),0.5)

    # ========== 时间推进 ==========
    def advance_time(self):
        s=self.state
        s["quarter"]+=1
        if s["quarter"]>4:
            s["quarter"]=1; s["years"]+=1; s["age"]+=1
            # 每年触发一次感情事件
            if self.trigger_love_event():
                return
            self.show_democratic_review()
        else:
            # 战争自动触发检查
            if not s.get("war_done") and not s.get("at_war") and s["years"]>=1:
                if random.random()<0.25:
                    self.trigger_war(); return
            self.show_actions()

    def annual_review_body(self):
        s=self.state
        # 检查成就
        new_ach=self.check_achievements()
        ach_text=""
        if new_ach:
            ach_text=self.show_achievement_popup(new_ach)
            self.music.play("medal.wav")
        self.text.text=f"年度考核 — {s['years']}年\n\n"
        s["health"]=clamp(s["health"]+5,0,200)
        score=s.get("reward_score",0)
        medal=None
        for threshold,name in REWARD_THRESHOLDS:
            if score>=threshold: medal=name; break
        if medal:
            if medal=="嘉奖":
                self.text.text+=f"【年度评功】获得嘉奖。\n"
                s["reputation"]=clamp(s["reputation"]+3,0,200)
            else:
                s["medals"][medal]=s["medals"].get(medal,0)+1
                s["promo_points"]=s.get("promo_points",0)+MEDAL_POINTS[medal]
                self.text.text+=f"【年度评功】荣立【{medal}】！\n"
                self.music.play("medal.wav")
            s["reward_score"]=0
        else:
            self.text.text+=f"本年度未获评功。\n"
        pscore=promotion_score(s)
        threshold=promotion_threshold(s["rank_index"])
        if pscore>=threshold and s["rank_index"]<len(RANKS)-1:
            s["rank_index"]+=1
            self.text.text+=f"\n恭喜晋升为【{RANKS[s['rank_index']]}】！\n"
        else:
            self.text.text+=f"\n未获晋升。当前：{RANKS[s['rank_index']]}\n"
        self.text.text+=(f"\n综合评分：{pscore:.1f} / 晋升线：{threshold}")
        self.update_status()
        self.clear_choices()
        self.add_choice("继续",self.show_actions)
        self.add_choice("申请退伍",self.retire)

    # ========== 成就系统 ==========
    def check_achievements(self):
        """检查并解锁新成就"""
        s=self.state
        unlocked=s.setdefault("achievements",{})
        new_ones=[]
        for key,ach in ACHIEVEMENTS.items():
            if key in unlocked:
                continue
            try:
                if ach["check"](s):
                    unlocked[key]={"name":ach["name"],"desc":ach["desc"],
                                   "year":s["years"]}
                    # 应用奖励
                    if "reward" in ach:
                        for k,v in ach["reward"].items():
                            s[k]=clamp(s.get(k,0)+v,0,200)
                    new_ones.append(ach)
            except:
                pass
        return new_ones

    def show_achievement_popup(self,achievements):
        """成就解锁弹窗（叠加到当前文本）"""
        text="\n\n━━━━━━━━━━━━━━━━━━━━\n"
        text+="★ 解锁成就 ★\n"
        for ach in achievements:
            text+=f"  【{ach['name']}】{ach['desc']}\n"
            if "reward" in ach:
                text+="   奖励："
                reward_map={"reputation":"声望","morale":"士气","leadership":"领导",
                            "fitness":"体能","tactics":"战术","politics":"政工"}
                text+="，".join([f"{reward_map.get(k,k)}+{v}" for k,v in ach["reward"].items()])
                text+="\n"
        text+="━━━━━━━━━━━━━━━━━━━━\n"
        return text

    def show_achievements(self):
        """查看所有成就"""
        s=self.state
        unlocked=s.get("achievements",{})
        total=len(ACHIEVEMENTS)
        done=len(unlocked)
        self.text.text=(
            f"【成就系统】\n\n"
            f"已解锁：{done} / {total}\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n")
        for key,ach in ACHIEVEMENTS.items():
            if key in unlocked:
                info=unlocked[key]
                self.text.text+=f"★ 【{info['name']}】\n"
                self.text.text+=f"  {info['desc']}\n"
                self.text.text+=f"  （第{info['year']}年解锁）\n\n"
            else:
                self.text.text+=f"☆ ？？？\n"
                self.text.text+=f"  {ach['desc']}\n\n"
        self.text.text+="━━━━━━━━━━━━━━━━━━━━"
        self.clear_choices()
        self.add_choice("返回",self.show_actions)

    # ========== 感情系统 ==========
    def love_mood(self):
        s=self.state
        aff=s.get("lover_affection",0)
        if aff>=90: return "琴瑟和鸣"
        elif aff>=75: return "恩爱如初"
        elif aff>=60: return "和睦稳定"
        elif aff>=40: return "平淡如常"
        elif aff>=20: return "出现裂痕"
        else: return "濒临破裂"

    def show_love_menu(self):
        s=self.state
        lover=s.get("lover")
        self.text.text="【感情生活】\n\n"
        if not lover:
            self.text.text+="你目前还是单身。\n\n"
            if s["age"]>=20:
                self.text.text+="作为军人，找对象不容易。\n可以选择以下方式认识：\n"
                self.clear_choices()
                for m in MEET_METHODS:
                    self.add_choice(f"{m} — {MEET_METHODS[m]['desc']}",
                                    lambda x=m: self.try_meet(x))
                self.add_choice("返回",self.show_actions)
            else:
                self.text.text+="（你还太年轻，再过几年吧。）"
                self.clear_choices()
                self.add_choice("返回",self.show_actions)
            return
        # 已有恋人
        self.text.text+=(
            f"恋人：{lover['name']}\n"
            f"职业：{lover['work']}\n"
            f"性格：{lover['traits']}\n"
            f"状态：{self.love_mood()}\n"
            f"好感度：{s.get('lover_affection',0)}\n\n")
        if s.get("married"):
            self.text.text+="【已婚】\n"
            if s.get("children",0)>0:
                self.text.text+=f"子女：{s['children']}人\n"
        self.clear_choices()
        self.add_choice("【陪伴】回一趟家（好感+15 健康-5）",self.visit_family)
        self.add_choice("【礼物】送礼物",self.buy_gift)
        if not s.get("married") and s.get("lover_affection",0)>=70:
            self.add_choice("【求婚】打报告结婚",self.propose_marriage)
        self.add_choice("返回",self.show_actions)

    def try_meet(self,method):
        s=self.state
        info=MEET_METHODS[method]
        if random.random()>0.5+s["reputation"]/200:
            self.text.text=f"【{method}】\n\n这次没遇到合适的人。\n也许缘分还没到。"
            self.clear_choices()
            self.add_choice("再试试",self.show_love_menu)
            return
        name=random.choice(info["names"])
        trait=random.choice(info["traits"])
        work=random.choice(info["work"])
        s["lover"]={"name":name,"traits":trait,"work":work,
                    "method":method,"meet_year":s["years"]}
        s["lover_affection"]=info["initial_affection"]+random.randint(-5,10)
        self.music.play("family.wav")
        self.text.text=(
            f"【相识】\n\n"
            f"通过{method}，你认识了{name}。\n\n"
            f"她是一名{work}，性格{trait}。\n\n"
            f"初次见面，你们聊得还不错。\n\n"
            f"好感度：{s['lover_affection']}")
        self.update_status()
        self.clear_choices()
        self.add_choice("继续",self.show_actions)

    def visit_family(self):
        s=self.state
        apply_effects(s,{"lover_affection":15,"health":-5,"morale":8,"money":-500})
        self.music.play("family.wav")
        lover=s.get("lover")
        self.text.text=(
            f"【探亲】\n\n"
            f"你请了探亲假，回到家乡。\n"
            f"{lover['name']}早早地在车站等你。\n\n"
            f"你们一起度过了一周。\n\n"
            f"（好感+15，健康-5，花费500）")
        self.update_status()
        self.clear_choices()
        self.add_choice("返回",self.show_actions)

    def buy_gift(self):
        self.text.text="【送礼物】\n\n选择送什么礼物："
        self.clear_choices()
        self.add_choice("鲜花（300元，好感+5）",lambda: self.give_gift("鲜花",300,5,0))
        self.add_choice("首饰（1500元，好感+15）",lambda: self.give_gift("首饰",1500,15,0))
        self.add_choice("亲手做的礼物（好感+10 健康-3）",lambda: self.give_gift("手作",0,10,3))
        self.add_choice("返回",self.show_love_menu)

    def give_gift(self,name,money,aff,hc=0):
        s=self.state
        if s["money"]<money:
            self.text.text="钱不够。"
            self.clear_choices()
            self.add_choice("返回",self.show_love_menu)
            return
        apply_effects(s,{"lover_affection":aff,"money":-money,"health":-hc})
        self.music.play("family.wav")
        lover=s.get("lover")
        self.text.text=(
            f"【送礼物 · {name}】\n\n"
            f"你把{name}送给{lover['name']}。\n"
            f"她笑了，眼睛弯弯的。\n\n"
            f"好感+{aff}")
        self.update_status()
        self.clear_choices()
        self.add_choice("返回",self.show_love_menu)

    def propose_marriage(self):
        s=self.state
        lover=s.get("lover")
        s["married"]=True
        s["money"]-=3000
        apply_effects(s,{"lover_affection":15,"morale":15})
        self.music.play("promote.wav")
        self.text.text=(
            f"【结婚】\n\n"
            f"你向{lover['name']}求婚，她答应了。\n\n"
            f"你们举办了一场简单的军婚仪式。\n"
            f"战友们都来祝贺。\n\n"
            f"（花费3000，好感+15，士气+15）\n\n"
            f"军婚不易，请好好珍惜。")
        self.update_status()
        self.clear_choices()
        self.add_choice("继续",self.show_actions)

    def trigger_love_event(self):
        """每年触发一次感情事件"""
        s=self.state
        lover=s.get("lover")
        if not lover: return False
        aff=s.get("lover_affection",0)
        # 感情危机
        if aff<25 and random.random()<0.5:
            self.text.text=(
                f"【感情危机】\n\n"
                f"{lover['name']}在电话里说：\n"
                f"“我们离婚吧。这些年，我像个寡妇。”")
            self.clear_choices()
            self.add_choice("立刻请假回家挽回",lambda: self.resolve_crisis("回家"))
            self.add_choice("电话里苦苦挽留",lambda: self.resolve_crisis("电话"))
            self.add_choice("同意离婚",lambda: self.resolve_crisis("离婚"))
            return True
        # 正常感情事件
        if random.random()<0.4:
            event=random.choice(["探亲","结婚纪念日","孩子出生"])
            if event=="结婚纪念日" and s.get("married"):
                self.text.text=f"【结婚纪念日】\n\n你和{lover['name']}的结婚纪念日。"
                self.clear_choices()
                self.add_choice("请假回家庆祝（好感+15 健康-3）",
                                lambda: self.visit_family())
                self.add_choice("寄礼物回去（好感+8 花费500）",
                                lambda: self.give_gift("纪念礼物",500,8,0))
                return True
            if event=="孩子出生" and s.get("married") and s.get("children",0)==0:
                s["children"]=s.get("children",0)+1
                self.music.play("family.wav")
                self.text.text=(
                    f"【孩子出生】\n\n"
                    f"{lover['name']}给你打来电话，\n"
                    f"孩子的哭声透过听筒传来。\n\n"
                    f"你当爸爸了！")
                self.update_status()
                self.clear_choices()
                self.add_choice("继续",self.show_actions)
                return True
        return False

    def resolve_crisis(self,action):
        s=self.state
        lover=s.get("lover")
        if action=="离婚":
            s["divorced"]=True
            s["lover"]=None
            s["lover_affection"]=0
            apply_effects(s,{"morale":-20})
            self.music.play("sad.wav")
            self.text.text=f"【离婚】\n\n你和{lover['name']}离婚了。\n\n多年后，你仍会想起她。"
        elif action=="回家":
            apply_effects(s,{"lover_affection":20,"morale":-5,"relations":{"连长":-5}})
            self.text.text=f"【挽回】\n\n你立刻请假回家，\n{lover['name']}看到你，眼泪流了下来。\n\n你们和好了。"
        else:
            apply_effects(s,{"lover_affection":8})
            self.text.text=f"【电话挽留】\n\n你在电话里苦苦挽留，\n{lover['name']}的语气软了下来。"
        self.update_status()
        self.clear_choices()
        self.add_choice("继续",self.show_actions)

    # ========== 遗书系统 ==========
    def show_letter_menu(self):
        s=self.state
        letters=s.get("letters",[])
        self.text.text=(
            f"【我的遗书】\n\n"
            f"军人上战场前，大多会写下一封遗书。\n"
            f"你可以写多封，分别留给不同的人。\n\n")
        if letters:
            self.text.text+=f"已写：{len(letters)}封\n"
            for i,l in enumerate(letters):
                self.text.text+=f"  {i+1}. {l['title']}\n"
        else:
            self.text.text+="还没有写遗书。\n"
        self.clear_choices()
        self.add_choice("写一封遗书",self.show_letter_select)
        self.add_choice("查看已有遗书",self.show_letter_view)
        self.add_choice("返回",self.show_actions)

    def show_letter_select(self):
        self.text.text="【写遗书】\n\n选择把这封信留给谁："
        self.clear_choices()
        for key,tpl in LETTER_TEMPLATES.items():
            exists=any(l["key"]==key for l in self.state.get("letters",[]))
            mark="（已写）" if exists else ""
            self.add_choice(f"{tpl['title']} {mark}",lambda k=key: self.write_letter(k))
        self.add_choice("返回",self.show_letter_menu)

    def write_letter(self,key):
        s=self.state
        tpl=LETTER_TEMPLATES[key]
        content=tpl["content"].format(name=s["name"],date=f"军龄{s['years']}年")
        letter={"key":key,"title":tpl["title"],"content":content,
                "reply":tpl.get("reply",""),"reply_delay":tpl.get("reply_delay","多年后")}
        # 已写过就替换，否则新增
        letters=s.setdefault("letters",[])
        for i,l in enumerate(letters):
            if l["key"]==key:
                letters[i]=letter
                break
        else:
            letters.append(letter)
        self.music.play("family.wav")
        keeper=get_letter_keeper(s["rank_index"])
        self.text.text=(
            f"【遗书 · {tpl['title']}】\n\n"
            f"你拿起笔，在灯下写下：\n\n"
            f"{content}\n\n"
            f"（信写好了。{keeper}。）")
        self.update_status()
        self.clear_choices()
        self.add_choice("收好",self.show_letter_menu)

    def show_letter_view(self):
        s=self.state
        letters=s.get("letters",[])
        if not letters:
            self.text.text="还没有写遗书。"
            self.clear_choices()
            self.add_choice("返回",self.show_letter_menu)
            return
        self.text.text="【查看遗书】\n\n选择想查看的遗书："
        self.clear_choices()
        for i,l in enumerate(letters):
            self.add_choice(l["title"],lambda idx=i: self.view_one_letter(idx))
        self.add_choice("返回",self.show_letter_menu)

    def view_one_letter(self,idx):
        s=self.state
        letter=s["letters"][idx]
        keeper=get_letter_keeper(s["rank_index"])
        self.text.text=(
            f"【{letter['title']}】\n\n"
            f"{letter['content']}\n\n"
            f"（由{keeper}）")
        self.clear_choices()
        self.add_choice("返回",self.show_letter_view)

    def show_letter_at_sacrifice(self):
        s=self.state
        letters=s.get("letters",[])
        if not letters:
            return "【遗书】\n战友们翻遍遗物，没有发现遗书。\n你把所有的话，都留在了心里。\n\n"
        keeper=get_letter_keeper(s["rank_index"])
        text=f"【遗书】\n\n你的遗书由{keeper}。\n\n"
        for i,l in enumerate(letters):
            text+=f"━━━ 第{i+1}封 · {l['title']} ━━━\n\n"
            text+=l["content"]+"\n\n"
        text+="【家书回音】\n\n很久很久以后……\n\n"
        for l in letters:
            if l.get("reply"):
                delay=l.get("reply_delay","多年后")
                text+=f"═══════ {delay} ═══════\n\n"
                text+=l["reply"].format(name=s["name"])+"\n\n"
        bonus=len(letters)*5
        s["reputation"]=clamp(s["reputation"]+bonus,0,200)
        text+=f"【遗书影响】声望 +{bonus}\n\n"
        return text

    # ========== 落日行动 ==========
    def check_sunset_trigger(self):
        s=self.state
        if s["rank_index"]<12: return False
        if s["reputation"]<80: return False
        if not s.get("war_done"): return False
        if s.get("sunset_done"): return False
        if s.get("at_war") or s.get("in_hospital"): return False
        return True

    def trigger_sunset(self):
        s=self.state
        s["sunset_done"]=False
        s["sunset_layer"]=0
        s["sunset_decision"]=0
        s["sunset_score"]=0
        s["sunset_mistakes"]=0
        s["sunset_intel"]=0
        s["sunset_streak"]=0
        s["sunset_total"]=sum(len(l["decisions"]) for l in SUNSET_LAYERS)
        self.music.play("war.wav")
        self.update_status()
        text=(
            f"【落日行动】\n\n"
            f"军委联合作战指挥中心 · 绝密\n\n"
            f"经军委决策，代号「落日行动」的战略总攻即将展开。\n\n"
            f"此战目标：彻底摧毁敌对势力，直取敌国首都。\n\n"
            f"“马踏东京赏樱花”——这是全体指战员的共同心声。\n\n"
            f"你作为军委副主席，被任命为落日行动最高指挥官。\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"【参战国】\n")
        for name,info in SUNSET_NATIONS.items():
            text+=f"  {name}：{info['role']}\n"
        text+=(
            f"\n━━━━━━━━━━━━━━━━━━━━\n"
            f"【六层指挥体系】\n"
            f"  1.士兵  2.军士  3.尉官  4.校官  5.将官  6.军委副主席\n"
            f"  共 {s['sunset_total']} 个决策\n"
            f"━━━━━━━━━━━━━━━━━━━━")
        self.text.text=text
        self.clear_choices()
        self.add_choice("进入第一层 · 士兵",self.sunset_show_layer)

    def sunset_battle_state(self):
        s=self.state
        score=s.get("sunset_score",0)
        done=s.get("sunset_layer",0)*6+s.get("sunset_decision",0)
        if done==0: return "开战"
        ratio=score/max(done,1)
        if ratio>=2: return "大优"
        elif ratio>=1: return "优势"
        elif ratio>=0: return "均势"
        elif ratio>=-1: return "劣势"
        else: return "危机"

    def sunset_sacrifice_chance(self):
        s=self.state
        score=s.get("sunset_score",0)
        if score>=15: return 0.01
        elif score>=8: return 0.02
        elif score>=3: return 0.03
        elif score>=-3: return 0.05
        elif score>=-10: return 0.08
        else: return 0.12

    def sunset_fail_threshold(self):
        return max(5,int(sum(len(l["decisions"]) for l in SUNSET_LAYERS)*0.25))

    def sunset_show_layer(self):
        s=self.state
        li=s.get("sunset_layer",0)
        if li>=len(SUNSET_LAYERS):
            self.finish_sunset(); return
        layer=SUNSET_LAYERS[li]
        self.music.play("war.wav")
        self.update_status()
        self.text.text=(
            f"【{layer['title']}】\n\n"
            f"身份：{layer['role']}\n\n"
            f"{layer['intro']}\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"战局状态：{self.sunset_battle_state()}\n"
            f"当前评分：{s.get('sunset_score',0)}  失误：{s.get('sunset_mistakes',0)}\n"
            f"━━━━━━━━━━━━━━━━━━━━")
        self.clear_choices()
        self.add_choice("开始决策",self.sunset_show_decision)

    def sunset_show_decision(self):
        s=self.state
        li=s.get("sunset_layer",0)
        di=s.get("sunset_decision",0)
        layer=SUNSET_LAYERS[li]
        decisions=layer["decisions"]
        if di>=len(decisions):
            s["sunset_layer"]=li+1
            s["sunset_decision"]=0
            self.sunset_show_layer(); return
        d=decisions[di]
        self.update_status()
        self.text.text=(
            f"【{layer['title']}】\n\n"
            f"{d['title']}\n\n"
            f"{d['text']}\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"战局：{self.sunset_battle_state()}  评分：{s.get('sunset_score',0)}  失误：{s.get('sunset_mistakes',0)}\n"
            f"━━━━━━━━━━━━━━━━━━━━")
        self.clear_choices()
        for c in d["choices"]:
            self.add_choice(f"{c['text']}（{c['note']}）",
                            lambda ch=c: self.sunset_resolve(ch))

    def sunset_resolve(self,choice):
        s=self.state
        li=s.get("sunset_layer",0)
        di=s.get("sunset_decision",0)
        layer=SUNSET_LAYERS[li]
        d=layer["decisions"][di]
        effects=dict(choice.get("effects",{}))
        intel_gain=effects.pop("intel",0)
        if intel_gain:
            s["sunset_intel"]=s.get("sunset_intel",0)+intel_gain
        apply_effects(s,effects)
        score=choice.get("score",0)
        s["sunset_score"]=s.get("sunset_score",0)+score
        if score<1:
            s["sunset_mistakes"]=s.get("sunset_mistakes",0)+1
            s["sunset_streak"]=0
        elif score>=3:
            s["sunset_streak"]=s.get("sunset_streak",0)+1

        text=(
            f"【决策结果】\n\n"
            f"你的决策：{choice['text']}\n\n")
        if score>=3:
            text+="★★★ 完美决策！战局大优！\n"
        elif score>=2:
            text+="★★ 优秀决策，战局向好。\n"
        elif score==1:
            text+="★ 稳妥决策。\n"
        elif score==0:
            text+="○ 平庸决策。\n"
        elif score==-1:
            text+="⚠ 决策失误，战局不利。\n"
        elif score==-2:
            text+="⚠⚠ 严重失误，战局恶化。\n"
        else:
            text+="⚠⚠⚠ 灾难性失误！\n"
        if s.get("sunset_streak",0)>=3:
            text+="\n★ 连续完美决策，士气高涨！\n"
        self.text.text=text
        self.update_status()

        if s["health"]<=0 or random.random()<self.sunset_sacrifice_chance():
            s["sacrifice"]=True
            s["sunset_done"]=True
            Clock.schedule_once(lambda dt: self.sunset_sacrifice(),0.5)
            return
        if s.get("sunset_mistakes",0)>=self.sunset_fail_threshold():
            self.sunset_defeat(); return
        s["sunset_decision"]=di+1
        self.clear_choices()
        self.add_choice("继续",self.sunset_show_decision)

    def finish_sunset(self):
        s=self.state
        s["sunset_done"]=True
        s["war_done"]=True
        score=s.get("sunset_score",0)
        mistakes=s.get("sunset_mistakes",0)
        if mistakes==0 and score>=60: rank="战神"
        elif mistakes<=2 and score>=45: rank="名将"
        elif score>=30: rank="合格"
        elif score>=15: rank="平庸"
        else: rank="惨胜"
        bonus_rep={"战神":50,"名将":40,"合格":30,"平庸":20,"惨胜":10}[rank]
        s["reputation"]=clamp(s["reputation"]+bonus_rep,0,200)
        s["medals"]["荣誉称号"]=s["medals"].get("荣誉称号",0)+1
        s["promo_points"]=s.get("promo_points",0)+MEDAL_POINTS["荣誉称号"]
        s["reward_score"]=s.get("reward_score",0)+50
        self.music.play("promote.wav")
        self.update_status()
        text=(
            f"【落日行动 · 全线胜利】\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"  【战役评价】{rank}\n"
            f"  【最终评分】{score}\n"
            f"  【失误次数】{mistakes}\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"【胜利词】\n\n"
            f"自甲午以来，我中华受尽屈辱，\n"
            f"列强环伺，山河破碎，\n"
            f"多少先辈，含恨而去。\n\n"
            f"今日，人民军队跨海出征，\n"
            f"铁流所向，敌寇披靡，\n"
            f"东京城下，红旗高扬。\n\n"
            f"这不是复仇，这是正义。\n"
            f"这不是侵略，这是雪耻。\n\n"
            f"你们未竟的事业，我们完成了。\n"
            f"你们未见的盛世，我们看到了。\n"
            f"山河无恙，国泰民安。\n"
            f"这盛世，如你所愿。\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"  声望 +{bonus_rep}   表现分 +50\n"
            f"  勋章：荣誉称号\n"
            f"━━━━━━━━━━━━━━━━━━━━")
        self.text.text=text
        new_ach=self.check_achievements()
        if new_ach:
            self.text.text+=self.show_achievement_popup(new_ach)
        self.update_status()
        self.clear_choices()
        self.add_choice("继续军旅生涯",self.show_actions)

    def sunset_defeat(self):
        s=self.state
        s["sunset_done"]=True
        self.music.play("sad.wav")
        self.update_status()
        self.text.text=(
            f"【落日行动 · 受挫】\n\n"
            f"一着不慎，满盘皆输\n\n"
            f"由于多次决策失误，战局急转直下。\n\n"
            f"上级命令：全线撤退。落日行动被迫中止。\n\n"
            f"最终评分：{s.get('sunset_score',0)}\n"
            f"失误次数：{s.get('sunset_mistakes',0)}")
        self.clear_choices()
        self.add_choice("返回部队",self.show_actions)

    def sunset_sacrifice(self):
        s=self.state
        self.music.play("sacrifice.wav")
        rank=RANKS[s["rank_index"]]
        medals_str=" ".join([f"{k}×{v}" for k,v in s.get("medals",{}).items() if v]) or "无"
        self.update_status()
        self.text.text=(
            f"【落日行动 · 牺牲】\n\n"
            f"马革裹尸，青山埋骨\n\n"
            f"你倒在了前线。\n\n"
            f"临终前，你望向远方。\n"
            f"朝阳从地平线升起，照亮了整个战场。\n\n"
            f"你轻声说：\n"
            f"“后面的同志……继续前进……”\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"最终评分：{s.get('sunset_score',0)}\n"
            f"最终军衔：{rank}\n"
            f"军龄：{s['years']}年\n"
            f"勋章：{medals_str}\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"【追授】荣誉称号（一等功/烈士）")
        self.clear_choices()
        self.add_choice("重新开始",self.show_start)

    def retire(self):
        self.music.play("retire.wav")
        s=self.state
        rank=RANKS[s["rank_index"]]
        if s["rank_index"]>=15: ending="将军"
        elif s["rank_index"]>=9: ending="优秀军官"
        elif s["rank_index"]>=6: ending="高级军士"
        else: ending="退伍老兵"
        medals_str=" ".join([f"{k}×{v}" for k,v in s.get("medals",{}).items() if v]) or "无"
        self.text.text=(f"退伍结局\n\n你以【{rank}】军衔退伍。\n\n"
                        f"军龄：{s['years']} 年\n最终军衔：{rank}\n声望：{s['reputation']}\n"
                        f"勋章：{medals_str}\n\n【结局】{ending}\n\n感谢你为国家所做的一切。")
        self.update_status()
        self.clear_choices()
        self.add_choice("重新开始",self.show_start)


class RongxunApp(App):
    def build(self):
        self.title="荣勋之路"
        return GameScreen()

if __name__=="__main__":
    RongxunApp().run()
