#!/usr/bin/env python3
"""《基督教两千年家谱》页面引用的资料：编号 → (说明, 网址, 用来核对的关键词)。
python3 tools/q4/history_sources.py --check 会逐个打开网址，核对页面里确实有这些关键词（GitHub 上的 history-check.yml 用它）。"""
import json, re, sys, urllib.parse, urllib.request

B = 'https://www.britannica.com/'
SRC = {
 # 早期教会
 'justin':    ('殉道者游斯丁《第一护教书》第67章（约公元155年，描述基督徒在“称为太阳日的那天”聚会）', 'https://www.newadvent.org/fathers/0126.htm', ['Sunday']),
 'pliny':     ('小普林尼致图拉真皇帝的信（约公元112年，罗马官员对基督徒聚会的记录）', 'https://www.britannica.com/biography/Pliny-the-Younger', ['Christian']),
 'laodicea':  ('老底嘉会议教规第29条（约公元363—364年）', 'https://www.newadvent.org/fathers/3806.htm', ['Laodicea', 'Sabbath']),
 'milan':     ('《米兰敕令》（313年）', B + 'topic/Edict-of-Milan', ['313']),
 'sunday321': ('君士坦丁的星期日法令（321年）', B + 'topic/Sunday-day-of-week', ['Constantine']),
 'nicaea':    ('第一次尼西亚会议（325年）', B + 'event/First-Council-of-Nicaea-325', ['Arius']),
 'theodosius':('狄奥多西一世：尼西亚信仰定为国教（380年）', B + 'biography/Theodosius-I', ['380']),
 'ephesus':   ('以弗所会议（431年）', B + 'event/Council-of-Ephesus-431', ['Nestorius']),
 'chalcedon': ('迦克墩会议（451年）', B + 'event/Council-of-Chalcedon', ['451']),
 'east':      ('东方教会（亚述教会、唐代“景教”）', B + 'topic/Church-of-the-East', ['China']),
 'oriental':  ('东方正统教会（科普特、亚美尼亚等）', B + 'topic/Oriental-Orthodox-church', ['Chalcedon']),
 'augustine': ('奥古斯丁', B + 'biography/Saint-Augustine', ['Hippo']),
 'tertullian':('特土良（最早用拉丁文“三位一体”一词）', B + 'biography/Tertullian', ['Trinity']),
 'gregory':   ('大格列高利（590—604年任教宗）', B + 'biography/Saint-Gregory-I', ['590']),
 'schism':    ('1054年东西教会大分裂', B + 'event/Schism-of-1054', ['1054']),
 'waldenses': ('瓦典西人（彼得·瓦勒度）', B + 'topic/Waldenses', ['Waldo']),
 'wycliffe':  ('约翰·威克里夫', B + 'biography/John-Wycliffe', ['Bible']),
 'hus':       ('扬·胡斯（1415年被烧死）', B + 'biography/Jan-Hus', ['1415']),
 'gutenberg': ('古腾堡与印刷术', B + 'biography/Johannes-Gutenberg', ['Bible']),
 # 宗教改革
 'theses':    ('马丁·路德《九十五条论纲》（1517年）', B + 'event/Ninety-five-Theses', ['1517']),
 'luther':    ('马丁·路德', B + 'biography/Martin-Luther', ['Worms']),
 'augsburg':  ('《奥格斯堡信条》（1530年，路德宗）', 'https://bookofconcord.org/augsburg-confession/', ['Augsburg']),
 'zwingli':   ('慈运理（苏黎世改革）', B + 'biography/Huldrych-Zwingli', ['Zürich']),
 'anabapt':   ('重洗派（1525年）', B + 'topic/Anabaptists', ['1525']),
 'menno':     ('门诺·西门斯与门诺会', B + 'biography/Menno-Simons', ['Mennonite']),
 'calvin':    ('约翰·加尔文', B + 'biography/John-Calvin', ['Geneva']),
 'presby':    ('长老会（改革宗）', B + 'topic/Presbyterian-church', ['Knox']),
 'westminster':('《威斯敏斯特信条》（1646年）', B + 'topic/Westminster-Confession', ['1646']),
 'anglican':  ('圣公会', B + 'topic/Anglicanism', ['Henry VIII']),
 'trent':     ('天特会议（1545—1563年）', B + 'event/Council-of-Trent', ['1545']),
 'baptist':   ('浸信会（1609年约翰·史密斯）', B + 'topic/Baptist', ['Smyth']),
 'williams':  ('罗杰·威廉斯（美洲第一间浸信会、政教分离）', B + 'biography/Roger-Williams', ['Rhode Island']),
 'sdb':       ('安息日浸信会', B + 'topic/Seventh-Day-Baptists', ['Saturday']),
 'quaker':    ('贵格会（公谊会）', B + 'topic/Friends', ['Fox']),
 'methodism': ('卫理公会（循道宗）', B + 'topic/Methodism', ['Wesley']),
 'wesley':    ('约翰·卫斯理（1738年阿德门街）', B + 'biography/John-Wesley', ['Aldersgate']),
 'awakening': ('第一次大觉醒', B + 'event/Great-Awakening', ['Edwards']),
 'awakening2':('第二次大觉醒', B + 'topic/Second-Great-Awakening', ['revival']),
 'disciples': ('基督门徒会（复原运动）', B + 'topic/Christian-Church-Disciples-of-Christ', ['Campbell']),
 'pentecost': ('五旬节运动（1901、1906年）', B + 'topic/Pentecostalism', ['Azusa']),
 'vatican2':  ('第二次梵蒂冈大公会议（1962—1965年）', B + 'event/Second-Vatican-Council', ['1962']),
 # 复临运动
 'miller':    ('威廉·米勒耳', B + 'biography/William-Miller', ['1844']),
 'adventist': ('复临运动（各复临教会）', B + 'topic/Adventist', ['Miller']),
 'sda_brit':  ('基督复临安息日会（大英百科）', B + 'topic/Seventh-day-Adventist-church', ['1863']),
 'egw_brit':  ('怀爱伦（大英百科）', B + 'biography/Ellen-Gould-White', ['Harmon']),
 'sda_hist':  ('基督复临安息日会官方网站：教会历史', 'https://www.adventist.org/who-are-seventh-day-adventists/history-of-seventh-day-adventists/', ['1863']),
 'sda_beliefs':('基督复临安息日会官方网站：28条基本信仰', 'https://www.adventist.org/beliefs/', ['Fundamental']),
 'sda_sabbath':('官方信仰第20条：安息日', 'https://www.adventist.org/the-sabbath/', ['Sabbath']),
 'sda_dead':  ('官方信仰第26条：死亡与复活', 'https://www.adventist.org/death-and-resurrection/', ['resurrection']),
 'sda_sanct': ('官方信仰第24条：基督在天上圣所的服务', 'https://www.adventist.org/christs-ministry-in-the-heavenly-sanctuary/', ['1844']),
 'sda_egw':   ('官方信仰第18条：预言的恩赐', 'https://www.adventist.org/gift-of-prophecy/', ['Ellen']),
 'sda_coming':('官方信仰第25条：基督复临', 'https://www.adventist.org/the-second-coming-of-christ/', ['coming']),
 'sda_trinity':('官方信仰第2条：三位一体', 'https://www.adventist.org/trinity/', ['Trinity']),
 'sda_supper':('官方信仰第16条：圣餐（含洗脚礼）', 'https://www.adventist.org/the-lords-supper/', ['foot']),
 'sda_stats': ('基督复临安息日会世界统计', 'https://www.adventist.org/statistics/', ['members']),
 'sda_china': ('复临信徒在中国（复临百科全书）', 'https://encyclopedia.adventist.org/article?id=8BFH', ['China']),
 # 统计
 'pew':       ('皮尤研究中心《全球基督教》报告（2011年）', 'https://www.pewresearch.org/religion/2011/12/19/global-christianity-exec/', ['Catholic']),
 'lwf':       ('信义宗世界联会（路德宗）', 'https://lutheranworld.org/who-we-are', ['million']),
 'wcrc':      ('世界归正教会联盟（改革宗/长老会）', 'https://wcrc.ch/about-us', ['million']),
 'wmc':       ('世界卫理公会协会', 'https://worldmethodistcouncil.org/about/', ['million']),
 'anglicancomm':('普世圣公宗', 'https://www.anglicancommunion.org/structures/member-churches.aspx', ['million']),
 'bwa':       ('世界浸信会联盟', 'https://baptistworld.org/about/', ['million']),
 # 中国
 'ricci':     ('利玛窦', B + 'biography/Matteo-Ricci', ['China']),
 'morrison':  ('马礼逊（第一位来华的新教宣教士，1807年）', B + 'biography/Robert-Morrison', ['1807']),
 'taylor':    ('戴德生与中国内地会（1865年）', B + 'biography/Hudson-Taylor', ['China Inland Mission']),
 'tjc':       ('真耶稣教会（1917年创立）', 'https://tjc.org/', ['True Jesus']),
}

NA = 'https://www.newadvent.org/'
MORE = {   # 同一条资料的备选网址（第一个核对通过的就用它）
 'pliny':     ['https://sourcebooks.fordham.edu/source/pliny1.asp'],
 'ignatius':  ('伊格那丢《致马内夏人书》第9章（约公元110年）', NA + 'fathers/0105.htm', ['Magnesians']),
 'nicaea_ce': ('天主教百科全书：第一次尼西亚会议', NA + 'cathen/11044a.htm', ['Nicaea']),
 'creed_ce':  ('天主教百科全书：尼西亚信经', NA + 'cathen/11049a.htm', ['Creed']),
 'ephesus_ce':('天主教百科全书：以弗所会议', NA + 'cathen/05491a.htm', ['Nestorius']),
 'chalc_ce':  ('天主教百科全书：迦克墩会议', NA + 'cathen/03555a.htm', ['Chalcedon']),
 'schism_ce': ('天主教百科全书：东方分裂', NA + 'cathen/13535a.htm', ['Cerularius']),
 'wald_ce':   ('天主教百科全书：瓦典西人', NA + 'cathen/15527b.htm', ['Waldo']),
 'wyc_ce':    ('天主教百科全书：威克里夫', NA + 'cathen/15722a.htm', ['Wyclif']),
 'hus_ce':    ('天主教百科全书：胡斯', NA + 'cathen/07584b.htm', ['Huss']),
 'luther_ce': ('天主教百科全书：马丁·路德', NA + 'cathen/09438b.htm', ['Luther']),
 'theses_txt':('《九十五条论纲》全文（英译）', 'https://www.luther.de/en/95thesen.html', ['indulgence']),
 'schleitheim':('《施莱特海姆信条》（1527年，重洗派）', 'https://gameo.org/index.php?title=Schleitheim_Confession_(Anabaptist,_1527)', ['Schleitheim']),
 'lbc1689':   ('《1689年伦敦浸信会信条》', 'https://www.the1689confession.com/', ['Baptist']),
 'sdb_org':   ('安息日浸信会总会', 'https://seventhdaybaptist.org/', ['Sabbath']),
 'ag_hist':   ('神召会历史（1914年）', 'https://ag.org/About/About-the-AG/History', ['1914']),
 'egw_est':   ('怀爱伦著作托管会：怀爱伦生平', 'https://whiteestate.org/about/egwbio/', ['Ellen']),
 'wcrc2':     ('世界归正教会联盟', 'https://wcrc.eu/', ['Reformed']),
 'bwa2':      ('世界浸信会联盟', 'https://baptistworld.org/', ['Baptist']),
 # 第二轮：大英百科拒绝程序访问、网页时光机里也没有的，换成其他可靠来源
 'ephesus':   [NA + 'cathen/05491a.htm'],
 'east':      [NA + 'cathen/10755a.htm', 'https://en.wikipedia.org/wiki/Xi%27an_Stele'],
 'augustine': [NA + 'cathen/02084a.htm'],
 'tertullian':[NA + 'cathen/15047a.htm', NA + 'cathen/14520c.htm'],
 'presby':    [B + 'topic/Presbyterianism', B + 'biography/John-Knox', 'https://en.wikipedia.org/wiki/Presbyterianism'],
 'baptist':   [B + 'biography/John-Smyth', 'https://en.wikipedia.org/wiki/John_Smyth_(Baptist_minister)'],
 'williams':  ['https://en.wikipedia.org/wiki/First_Baptist_Church_in_America', 'https://www.firstbaptistchurchinamerica.org/'],
 'sdb':       ['https://en.wikipedia.org/wiki/Seventh_Day_Baptists'],
 'disciples': [B + 'topic/Disciples-of-Christ', 'https://en.wikipedia.org/wiki/Restoration_Movement'],
 'adventist': ['https://en.wikipedia.org/wiki/Millerites'],
 'sda_china': ['https://en.wikipedia.org/wiki/Abram_La_Rue', 'https://en.wikipedia.org/wiki/Seventh-day_Adventist_Church_in_China'],
 'wmc':       ['https://worldmethodistcouncil.org/', 'https://en.wikipedia.org/wiki/World_Methodist_Council'],
 'taylor':    ['https://omf.org/about/our-history/', 'https://en.wikipedia.org/wiki/Hudson_Taylor'],
 'pliny_txt': ('小普林尼致图拉真的信（英译全文，福特汉姆大学古代史资料集）', 'https://sourcebooks.fordham.edu/source/pliny1.asp', ['Christ']),
 'socrates':  ('苏格拉底（教会史家）《教会史》第5卷第22章（约公元440年）', NA + 'fathers/26015.htm', ['sabbath']),
 'sozomen':   ('索宗曼《教会史》第7卷第19章（约公元445年）', NA + 'fathers/26027.htm', ['Sabbath']),
 'fraser':    ('Fraser GE, Shavlik DJ. Ten years of life: Is it a matter of choice? Arch Intern Med 2001;161:1645-52（PubMed 11434797）', 'https://doi.org/10.1001/archinte.161.13.1645', ['Adventists']),
 'sda_coming2':('官方信仰第25条：基督复临（英文版信仰全文）', 'https://www.adventist.org/beliefs/fundamental-beliefs/restoration/second-coming-of-christ/', ['coming']),
 # 第三轮：路德、怀爱伦人物特写，弟兄会
 'luther_pref':('路德《拉丁文著作全集序言》（1545年，回忆自己怎样明白罗马书1:17）', ['https://christianhistoryinstitute.org/magazine/article/luthers-breakthrough', 'https://www.checkluther.com/wp-content/uploads/1545-Preface-to-the-Complete-Edition-of-Luther%E2%80%99s-Latin-Works.pdf'], ['paradise']),
 'luther_worms':('路德在沃尔姆斯帝国会议上的答辩（1521年4月18日）', ['https://christianhistoryinstitute.org/magazine/article/diet-of-worms', 'https://en.wikipedia.org/wiki/Diet_of_Worms'], ['conscience']),
 'luther_name':('路德《真诚劝勉众基督徒谨防叛乱》（1522年），《路德文集》（Luther’s Works）英文版第45卷第70—71页', None, []),
 'brethren':  ('普利茅斯弟兄会（达秘、时代论）', [B + 'topic/Plymouth-Brethren', 'https://en.wikipedia.org/wiki/Plymouth_Brethren'], ['Darby']),
 'nee':       ('倪柝声与聚会处（地方教会）', [B + 'biography/Watchman-Nee', 'https://en.wikipedia.org/wiki/Watchman_Nee'], ['Brethren']),
 'egw_wiki':  ('怀爱伦（维基百科英文版，作为补充核对）', 'https://en.wikipedia.org/wiki/Ellen_G._White', ['Gorham']),
 # 第五轮：补充核对具体说法
 'sdb2':      ('安息日浸信会《安息日记录者》：北美第一间安息日浸信会（1671年纽波特）', ['https://www.sabbathrecorder.com/2013/10/22/a-thumbnail-sketch-of-seventh-day-baptists/', 'https://en.wikipedia.org/wiki/United_Baptist_Church_(Newport,_Rhode_Island)'], ['1671']),
 'sda_wiki':  ('基督复临安息日会（维基百科英文版）', 'https://en.wikipedia.org/wiki/Seventh-day_Adventist_Church', ['1863']),
 'sda_hist_wiki':('复临安息日会的历史（维基百科英文版）', 'https://en.wikipedia.org/wiki/History_of_the_Seventh-day_Adventist_Church', ['Edson']),
 'disappoint':('1844年“大失望”（维基百科英文版）', 'https://en.wikipedia.org/wiki/Great_Disappointment', ['1844']),
 'worms_wiki':('沃尔姆斯帝国会议（维基百科英文版）', 'https://en.wikipedia.org/wiki/Diet_of_Worms', ['Luther']),
 'luther_jews':('路德与犹太人（维基百科英文版）', 'https://en.wikipedia.org/wiki/Martin_Luther_and_antisemitism', ['Jews']),
 'luther_bible':('路德的德文圣经（维基百科英文版）', 'https://en.wikipedia.org/wiki/Luther_Bible', ['Wartburg']),
 'lutheranism':('路德宗（维基百科英文版）', 'https://en.wikipedia.org/wiki/Lutheranism', ['Luther']),
 'dispens':   ('时代论与“被提”说（维基百科英文版）', 'https://en.wikipedia.org/wiki/Dispensationalism', ['Darby']),
 'nee_wiki':  ('倪柝声（维基百科英文版）', 'https://en.wikipedia.org/wiki/Watchman_Nee', ['Brethren']),
 'ethiopia':  ('埃塞俄比亚正教会（维基百科英文版）', 'https://en.wikipedia.org/wiki/Ethiopian_Orthodox_Tewahedo_Church', ['Ethiopia']),
 'supremacy': ('英国《至尊法案》（维基百科英文版）', 'https://en.wikipedia.org/wiki/Acts_of_Supremacy', ['1534']),
 'thessalonica':('《帖撒罗尼迦敕令》（380年，维基百科英文版）', 'https://en.wikipedia.org/wiki/Edict_of_Thessalonica', ['380']),
 'scot_ref':  ('苏格兰宗教改革（维基百科英文版）', 'https://en.wikipedia.org/wiki/Scottish_Reformation', ['1560']),
 'restoration':('复原运动（维基百科英文版）', 'https://en.wikipedia.org/wiki/Restoration_Movement', ['Campbell']),
 'tjc_wiki':  ('真耶稣教会（维基百科英文版）', 'https://en.wikipedia.org/wiki/True_Jesus_Church', ['1917']),
 'stele':     ('大秦景教流行中国碑（维基百科英文版）', 'https://en.wikipedia.org/wiki/Xi%27an_Stele', ['781']),
 'trinity_ce':('天主教百科全书：三位一体（“trinitas”一词最早见于特土良）', NA + 'cathen/15047a.htm', ['Tertullian']),
 'pentecost_wiki':('五旬节运动（维基百科英文版）', 'https://en.wikipedia.org/wiki/Pentecostalism', ['Azusa']),
 'vatican2_wiki':('第二次梵蒂冈大公会议（维基百科英文版）', 'https://en.wikipedia.org/wiki/Second_Vatican_Council', ['1962']),
 'menno_wiki':('门诺·西门斯（维基百科英文版）', 'https://en.wikipedia.org/wiki/Menno_Simons', ['Mennonite']),
 # 第六轮
 'larue':     ('复临百科全书（ESDA）：拉鲁（Abram La Rue, 1822—1903）', ['https://encyclopedia.adventist.org/assets/pdf/article-7cjp.pdf', 'https://www.adventist.asia/news/how-did-one-mans-journey-start-a-global-movement-1/', 'https://sites.google.com/site/adventisminchina/individuals/1-expatriates/larue'], ['Hong']),
 'gc1863':    ('全球总会的成立（1863年5月21日，125间教会、3500名信徒）', ['https://adventistreview.org/magazine-article/a-pivotal-session/', 'https://www.rmcsda.org/the-annals-of-adventist-history-the-birth-of-a-denomination/', 'https://en.wikipedia.org/wiki/History_of_the_Seventh-day_Adventist_Church'], ['3,500']),
 'edson_wiki':('希兰·爱德森（维基百科英文版）', 'https://en.wikipedia.org/wiki/Hiram_Edson', ['Edson']),
 # 书籍（没有网址）：怀爱伦著作按英文原著页码引用
 'gc120':     ('怀爱伦《善恶之争》（The Great Controversy, 1911年版）英文原著第120页', None, []),
 'gc148':     ('怀爱伦《善恶之争》英文原著第148页', None, []),
 'gc595':     ('怀爱伦《善恶之争》英文原著第595页', None, []),
 'gc_intro':  ('怀爱伦《善恶之争》作者序言（英文原著第 xi—xii 页）', None, []),
 'cm125':     ('怀爱伦《书报员事工》（Colporteur Ministry）英文原著第125页（原载《评论与通讯》1903年1月20日）', None, []),
 'ls125':     ('怀爱伦《生平梗概》（Life Sketches of Ellen G. White）英文原著第125页', None, []),
 'ls196':     ('怀爱伦《生平梗概》英文原著第196页', None, []),
}

for k, v in MORE.items():
    if isinstance(v, list):
        d, u, w = SRC[k]; SRC[k] = (d, [u] + v, w)
    else:
        SRC[k] = v
SRC['sda_brit'] = (SRC['sda_brit'][0], SRC['sda_brit'][1], ['Adventist'])
SRC['disciples'] = (SRC['disciples'][0], SRC['disciples'][1], ['Stone'])
SRC['sdb'] = (SRC['sdb'][0], SRC['sdb'][1], ['1671'])
SRC['adventist'] = (SRC['adventist'][0], SRC['adventist'][1], ['Miller'])

# 页面里引用的具体说法：在原网页里找出对应的原句，打印出来人工核对（--facts）
FACTS = {
 'pew': [r'2\.18 billion', r'Catholics', r'Protestants', r'Orthodox', r'Pentecostal', r'other Christian'],
 'sda_stats': [r'[Mm]embers', r'[Cc]hurches', r'countries'],
 'lwf': [r'million'], 'wcrc2': [r'million'], 'wmc': [r'million'], 'anglicancomm': [r'million'], 'bwa2': [r'million'],
 'laodicea': [r'Canon XXIX', r'judaize'], 'justin': [r'day called Sunday', r'first day'], 'ignatius': [r"Lord's [Dd]ay"],
 'pliny_txt': [r'fixed day', r'before it was light'], 'socrates': [r'sabbath of every week'], 'sozomen': [r'assemble together on the Sabbath'],
 'sunday321': [r'321', r'Constantine'], 'sda_hist': [r'3,?500', r'Oakes|Preston', r'Edson', r'Bates', r'1863'],
 'tertullian': [r'[Tt]rinitas', r'Tertullian'], 'wesley': [r'Aldersgate', r'warmed'], 'egw_est': [r'1844', r'vision'],
 'miller': [r'1831', r'1844'], 'ag_hist': [r'1914'], 'tjc': [r'1917'], 'morrison': [r'1807'], 'schism': [r'1054'],
 'theodosius': [r'380'], 'east': [r'China', r'781|635'], 'sda_china': [r'1888', r'1902'], 'taylor': [r'1865'],
 'williams': [r'1638'], 'sdb': [r'1671', r'Newport'], 'baptist': [r'1609', r'Amsterdam'], 'presby': [r'Knox', r'1560'],
 'disciples': [r'1832'], 'gregory': [r'590'], 'waldenses': [r'Waldo', r'1532|Chanforan'], 'wycliffe': [r'1382|English'],
 'hus': [r'1415'], 'gutenberg': [r'145\d'], 'anglican': [r'1534'], 'calvin': [r'1536'], 'anabapt': [r'1525'],
 'trent': [r'1545', r'1563'], 'menno': [r'Mennonite'], 'westminster': [r'1646'], 'methodism': [r'1784'],
 'pentecost': [r'Topeka|1901', r'Azusa'], 'vatican2': [r'1962', r'1965'], 'milan': [r'313'], 'nicaea': [r'325'],
 'chalcedon': [r'451'], 'ephesus': [r'431'], 'oriental': [r'Ethiopia', r'Sabbath|Saturday'], 'ricci': [r'1583|1582'],
 'fraser': [r'7\.28', r'4\.42'], 'sda_trinity': [r'Trinity'], 'sda_coming2': [r'visible|literal'],
 'luther': [r'Eisleben', r'Erfurt', r'1505', r'Wartburg', r'Bora', r'Jews', r'[Pp]easants', r'Here I stand', r'1546'],
 'luther_pref': [r'paradise'], 'luther_worms': [r'captive to the Word', r'Here I stand'], 'luther_name': [r'call themselves'],
 'egw_est': [r'Gorham', r'twin', r'stone', r'nine', r'December', r'1846', r'5,000', r'40 books', r'translated', r'visions', r'Australia', r'1915', r'Elmshaven'],
 'egw_wiki': [r'Casco Bay|baptized', r'1843', r'most translated', r'Elmshaven'],
 'brethren': [r'Darby', r'Plymouth', r'1831|1827', r'[Rr]apture|dispensation'], 'nee': [r'192\d', r'Brethren'],
 'sdb2': [r'1671', r'Mumford'], 'sda_wiki': [r'3,500', r'125 churches|125 congregations'], 'sda_hist_wiki': [r'Oakes|Preston', r'Edson', r'Crosier', r'Preble', r'1848'],
 'disappoint': [r'wept'], 'worms_wiki': [r'Here I stand', r'later'], 'luther_jews': [r'On the Jews and Their Lies', r'1994|repudiat', r'Lutheran World Federation'],
 'luther_bible': [r'Wartburg', r'September', r'1534', r'eleven weeks|11 weeks'], 'lutheranism': [r'not Lutherans|make no reference to my name|call themselves'],
 'dispens': [r'[Rr]apture', r'Scofield'], 'nee_wiki': [r'1922', r'Fuzhou|Foochow'], 'ethiopia': [r'Sabbath|Saturday'],
 'supremacy': [r'1534'], 'thessalonica': [r'380', r'state religion|Nicene'], 'scot_ref': [r'1560', r'Knox'], 'restoration': [r'1832', r'Stone'],
 'tjc_wiki': [r'1917', r'Beijing|Peking', r'Sabbath|Saturday', r'foot'], 'stele': [r'635', r'781', r'Alopen|Aluoben'], 'trinity_ce': [r'[Tt]rinitas'],
 'socrates': [r'sabbath of every week'], 'pentecost_wiki': [r'Topeka', r'Azusa', r'1906'], 'vatican2_wiki': [r'separated brethren|vernacular'],
 'egw_wiki': [r'Casco Bay|baptized', r'[Dd]isfellowship|expelled|removed', r'Avondale', r'Europe'],
 'egw_est': [r'1858', r'1863|health reform', r'1848|little paper', r'Europe', r'1881'],
 'sda_china': [r'La ?Rue', r'190\d', r'Canton|Guangzhou|Shanghai'],
 'larue': [r'1888', r'Hong ?[Kk]ong', r'self-supporting|ship'], 'gc1863': [r'3,?500', r'125 churches|125 congregations|125'], 'edson_wiki': [r'wept', r'1844'],
}

UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36'


def fetch(url):
    r = urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': UA, 'Accept-Language': 'en'}), timeout=60)
    return r.status, r.geturl(), r.read().decode('utf-8', 'replace')


def wayback(url):
    """网站拒绝程序访问时，用网页时光机（archive.org）存的副本核对内容"""
    j = json.load(urllib.request.urlopen('https://archive.org/wayback/available?url=' + urllib.parse.quote(url, safe=''), timeout=60))
    snap = (j.get('archived_snapshots') or {}).get('closest') or {}
    if not snap.get('available'):
        raise RuntimeError('网页时光机里没有')
    return fetch(snap['url'])[2], snap.get('timestamp', '')


def plain(body):
    t = re.sub(r'<(script|style)[^>]*>.*?</\1>', ' ', body, flags=re.S | re.I)
    t = re.sub(r'<[^>]+>', ' ', t)
    t = t.replace('&nbsp;', ' ').replace('&#8217;', "'").replace('&rsquo;', "'").replace('&amp;', '&')
    return re.sub(r'\s+', ' ', t)


def check():
    import time
    out = {}
    only = next((a.split('=', 1)[1].split(',') for a in sys.argv if a.startswith('--only=')), None)
    for k, (desc, urls, keys) in SRC.items():
        if only and k not in only:
            continue
        if urls is None:
            continue
        urls = urls if isinstance(urls, list) else [urls]
        res = None
        for url in urls:
            host = urllib.parse.urlsplit(url).netloc
            for attempt in range(3):
                try:
                    if host.endswith('www.adventist.org'):
                        body, ts = wayback(url); st, final, how = 200, url, 'archive ' + ts
                        break
                    st, final, body = fetch(url); how = 'live'
                    break
                except Exception as e:
                    code = getattr(e, 'code', 0)
                    if code == 429 and attempt < 2:
                        time.sleep(15 * (attempt + 1)); continue
                    try:
                        body, ts = wayback(url); st, final, how = code, url, 'archive ' + ts
                    except Exception as e2:
                        st, final, body, how = code, url, '', 'fail: ' + str(e)[:60] + ' / ' + str(e2)[:60]
                    break
            title = re.sub(r'\s+', ' ', (re.search(r'<title[^>]*>(.*?)</title>', body, re.S | re.I) or [None, ''])[1]).strip()[:80]
            miss = [w for w in keys if w.lower() not in body.lower()]
            res = {'ok': bool(body) and not miss, 'url': url, 'final': final, 'how': how, 'status': st, 'title': title, 'missing': miss}
            res['body'] = body
            if res['ok']:
                break
        out[k] = res
        print(('OK  ' if res['ok'] else 'BAD ') + k.ljust(12), res['how'][:30].ljust(30), res['url'], '|', res['title'], ('缺' + str(res['missing'])) if res['missing'] and res['title'] else '', flush=True)
    print(sum(o['ok'] for o in out.values()), '/', len(out), '可用')
    if '--facts' in sys.argv:
        print('\n======== 原文核对 ========')
        for k, pats in FACTS.items():
            o = out.get(k)
            if not o or not o.get('body'):
                print('##', k, '（没有内容）'); continue
            t = plain(o['body'])
            print('##', k, o['url'])
            for pat in pats:
                ms = list(re.finditer(pat, t))[:2]
                if not ms:
                    print('   [' + pat + '] 没找到')
                for m in ms:
                    print('   [' + pat + ']', t[max(0, m.start() - 160):m.end() + 160])
    return out

if __name__ == '__main__':
    if '--check' in sys.argv:
        check()

# 《耶稣是人还是神？》用到的资料（书籍按原著页码引用，没有网址）
SRC.update({
 'gregnaz':   ('拿先斯的格列高利《致克勒多纽书》（第101封信，约公元382年，反驳阿波里拿留）', None, []),
 'chaldef':   ('迦克墩会议《信仰定义》（公元451年）', None, []),
 'qod':       ('《复临信徒对教义问题的回答》（Seventh-day Adventists Answer Questions on Doctrine，1957年）英文原著第59—62、383页，附录B第650页', None, []),
 'da24':      ('怀爱伦《历代愿望》（The Desire of Ages）英文原著第24页', None, []),
 'da49':      ('怀爱伦《历代愿望》英文原著第48—49页', None, []),
 'da70':      ('怀爱伦《历代愿望》英文原著第70页', None, []),
 'da117':     ('怀爱伦《历代愿望》英文原著第117页', None, []),
 'da664':     ('怀爱伦《历代愿望》英文原著第664页', None, []),
 'bc5':       ('怀爱伦1895年致贝克牧师的信（Letter 8），载《基督复临安息日会圣经注释》第5卷英文原著第1128—1129页', None, []),
 'sm1':       ('怀爱伦《信息选粹》（Selected Messages）第1册英文原著第244页', None, []),
 'lewis':     ('C. S. 路易斯《返璞归真》（Mere Christianity）第三部第11章', None, []),
})

# 《耶稣是人还是神？》第5章《1955—1957：〈教义问答〉的故事》用到的资料（2026-10-04 在 GitHub 上下载原文逐条核对）
AD = 'https://documents.adventistarchives.org/'
SRC.update({
 'valentine': ('瓦伦丁（Gilbert M. Valentine）《复临—福音派会谈，1955—1956》，载《复临安息日会百科全书》', 'https://encyclopedia.adventist.org/assets/pdf/article-6JJ3.pdf', ['Unruh']),
 'unruh77':   ('昂鲁（T. E. Unruh）《1955—1956年复临安息日会与福音派的会谈》，《复临传承》（Adventist Heritage）1977年冬季号第35—46页；附班豪斯《复临安息日会信徒是基督徒吗？》（《永恒》杂志1956年9月）原文', 'https://www.adventistlaymen.org/Selected%20Documents%20and%20Manuscripts/THE%20SEVENTH-DAY%20ADVENTIST%20EVANGELICAL%20CONFERENCES%20OF%201955-1956.pdf', ['Barnhouse']),
 'br1914':    ('《家庭圣经读本》（Bible Readings for the Home Circle）1914年版第174页（复临教会档案馆扫描本）', AD + 'Books/BR1914.pdf', ['sinful, fallen']),
 'br1949':    ('《家庭圣经读本》1949年修订版（复临教会档案馆扫描本）', AD + 'Books/BR1949.pdf', ['Bible Readings']),
 'min1956':   ('《事工》（Ministry）杂志1956年9月号：社论《是人性，不是属肉体的》（Human, Not Carnal）及怀爱伦语录汇编《基督在道成肉身时的性情》', 'https://cdn.ministerialassociation.org/cdn/ministrymagazine.org/issues/1956/issues/MIN1956-09.pdf', ['Human, Not Carnal']),
 'knight03':  ('奈特（George R. Knight）编注《复临信徒对教义问题的回答》注释版（安德鲁斯大学出版社，2003年），历史与神学导言', 'https://digitalcommons.andrews.edu/adventist-books/1', ['Questions on Doctrine']),
 'whidden03': ('惠登（Woodrow W. Whidden）《〈教义问答〉：当年与今天》，《事工》杂志2003年8月（介绍奈特注释版）', 'https://www.ministrymagazine.org/archive/2003/08/questions-on-doctrine-then-and-now.html', ['Knight']),
 'douglass04':('道格拉斯（Herbert E. Douglass）《对重印〈教义问答〉的一些思考》，《事工》杂志2004年8月（引《教义问答》原文并注页码）', 'https://www.ministrymagazine.org/archive/2004/08/thoughts-on-the-republished-questions-on-doctrine.html', ['vicariously']),
 'rh1896':    ('怀爱伦，《评论与通讯》（Review and Herald）1896年12月15日（复临教会档案馆扫描本）', AD + 'Periodicals/RH/RH18961215-V73-50.pdf', ['sinful nature']),
 'yi1900':    ('怀爱伦，《青年导报》（Youth’s Instructor）1900年12月20日（复临教会档案馆扫描本）', AD + 'Periodicals/YI/YI19001220-V48-50.pdf', ['fallen, suffering']),
 'qod2007':   ('安德鲁斯大学《教义问答》出版50周年研讨会（2007年10月）论文集', 'https://digitalcommons.andrews.edu/qod/', ['Questions on Doctrine']),
 'w_andreasen':('维基百科：M. L. Andreasen', 'https://en.wikipedia.org/wiki/M._L._Andreasen', ['1961']),
})

# 《耶稣是人还是神？》补充问答页（jesus-qa.html）用到的资料（2026-10-04 核对）
DA_CCEL = 'https://ccel.org/ccel/white/desire.'
FORTIN = '（据 Denis Fortin 编《怀爱伦论基督的人性》核对）'
MIN56 = '（据《事工》杂志 1956 年 9 月怀爱伦语录汇编核对）'
SRC.update({
 'da123':    ('怀爱伦《历代愿望》第12章，英文原著第123页', DA_CCEL + 'xv.html', ['nothing that responded']),
 'da671':    ('怀爱伦《历代愿望》第73章，英文原著第671页', DA_CCEL + 'lxxvi.html', ['hereditary and cultivated']),
 'da686':    ('怀爱伦《历代愿望》第74章“客西马尼园”，英文原著第686页', DA_CCEL + 'lxxvii.html', ['gulf was so broad']),
 'da688':    ('怀爱伦《历代愿望》第74章“客西马尼园”，英文原著第688页', DA_CCEL + 'lxxvii.html', ['Terrible was the temptation']),
 'da692':    ('怀爱伦《历代愿望》第74章“客西马尼园”，英文原著第692—693页', DA_CCEL + 'lxxvii.html', ['awful moment']),
 'da693':    ('怀爱伦《历代愿望》第74章“客西马尼园”，英文原著第693页', DA_CCEL + 'lxxvii.html', ['strengthen Him to drink']),
 'da25':     ('怀爱伦《历代愿望》英文原著第25页', None, []),
 'da210':    ('怀爱伦《历代愿望》英文原著第210页', None, []),
 'rh1887':   ('怀爱伦，《评论与通讯》（Review and Herald）1887年11月8日（复临教会档案馆扫描本）', 'https://documents.adventistarchives.org/Periodicals/RH/RH18871108-V64-44.pdf', ['refined sensibilities']),
 'rh1888':   ('怀爱伦，《评论与通讯》1888年3月27日（复临教会档案馆扫描本）', 'https://documents.adventistarchives.org/Periodicals/RH/RH18880327-V65-13.pdf', ['not cherished']),
 'st1888':   ('怀爱伦，《时兆》（Signs of the Times）1888年3月23日（复临教会档案馆扫描本）', 'https://documents.adventistarchives.org/Periodicals/ST/ST18880323-V14-12.pdf', ['I am sinless']),
 't5_422':   ('怀爱伦《教会证言》（Testimonies for the Church）卷5，英文原著第422页' + MIN56, None, []),
 't2_509':   ('怀爱伦《教会证言》卷2，英文原著第508—509页' + FORTIN, None, []),
 't2_202':   ('怀爱伦《教会证言》卷2，英文原著第202页' + FORTIN, None, []),
 'rh1888s':  ('怀爱伦，《评论与通讯》1888年9月11日' + FORTIN, None, []),
 'rh1893m':  ('怀爱伦，《评论与通讯》1893年3月28日' + FORTIN, None, []),
 'rh1893a':  ('怀爱伦，《评论与通讯》1893年4月25日' + FORTIN, None, []),
 'rh1874':   ('怀爱伦，《评论与通讯》1874年7月28日' + MIN56, None, []),
 'yi1898':   ('怀爱伦，《青年导报》（Youth’s Instructor）1898年6月2日' + MIN56, None, []),
 'lt97':     ('怀爱伦 1898 年第 97 封信' + MIN56, None, []),
 'bc5_1131': ('《基督复临安息日会圣经注释》第5卷英文原著第1131页所载怀爱伦语' + MIN56, None, []),
 'sc17':     ('怀爱伦《拾级就主》（Steps to Christ）第2章，英文原著第17—18页', 'https://ccel.org/ccel/white/steps.v.html', ['selfishness took the place']),
 'sc43':     ('怀爱伦《拾级就主》第5章，英文原著第43页', None, []),
 'sc58':     ('怀爱伦《拾级就主》第7章，英文原著第58页', None, []),
 'pp49':     ('怀爱伦《先祖与先知》（Patriarchs and Prophets）英文原著第49页', None, []),
 'pp306':    ('怀爱伦《先祖与先知》第27章，英文原著第306页', None, []),
 'gc493':    ('怀爱伦《善恶之争》（The Great Controversy）英文原著第493页', None, []),
 'aa560':    ('怀爱伦《使徒行述》（The Acts of the Apostles）英文原著第560页', None, []),
 'aa561':    ('怀爱伦《使徒行述》英文原著第561页', None, []),
 'irving':   ('《宗教百科全书》：爱德华·欧文（Edward Irving，1792—1834）', 'https://www.encyclopedia.com/people/philosophy-and-religion/protestant-christianity-biographies/edward-irving', ['Annan']),
 'tgc':      ('福音联盟（The Gospel Coalition）：《耶稣取了堕落的人性吗？》（介绍巴特、托伦斯的看法和福音派的讨论）', 'https://www.thegospelcoalition.org/article/you-asked-did-jesus-assume-a-fallen-human-nature/', ['Barth']),
 # 问题彩蛋16—25 用到的资料：2026-10 用临时任务一次读取怀著原版页面和百科核对；医学文献在 PubMed 核对摘要和 DOI
 'poe_w':    ('恶的问题（Problem of evil，维基百科英文版：通常归于伊壁鸠鲁的说法、拉克坦修的记载、自由意志的辩护）', 'https://en.wikipedia.org/wiki/Problem_of_evil', ['Lactantius']),
 'lisbon_w': ('1755年里斯本大地震（维基百科英文版：万圣节上午，约4万—5万人死亡；伏尔泰）', 'https://en.wikipedia.org/wiki/1755_Lisbon_earthquake', ['Voltaire']),
 'pain_w':   ('路易斯《痛苦的奥秘》（The Problem of Pain，1940，维基百科英文版）', 'https://en.wikipedia.org/wiki/The_Problem_of_Pain', ['megaphone']),
 'gc492':    ('怀爱伦《善恶之争》第29章“罪恶的起源”，英文原著第492—493页', None, []),
 'gc498':    ('怀爱伦《善恶之争》第29章“罪恶的起源”，英文原著第498—499页', None, []),
 'gc678':    ('怀爱伦《善恶之争》最后一章，英文原著第678页', None, []),
 'pp34':     ('怀爱伦《先祖与先知》第1章“上帝为何允许罪恶存在？”，英文原著第34页', None, []),
 'pp42':     ('怀爱伦《先祖与先知》第1章“上帝为何允许罪恶存在？”，英文原著第42—43页', None, []),
 'pp49':     ('怀爱伦《先祖与先知》第2章“创造”，英文原著第49页', None, []),
 'pp331':    ('怀爱伦《先祖与先知》英文原著第331—332页', None, []),
 'da224':    ('怀爱伦《历代愿望》“约翰被囚和被害”一章，英文原著第224页', None, []),
 'frankl_w': ('弗兰克尔《活出生命的意义》（Man’s Search for Meaning，1946，维基百科英文版）', "https://en.wikipedia.org/wiki/Man's_Search_for_Meaning", ['logotherapy']),
 'wsc_w':    ('《威斯敏斯德小要理问答》（1647，维基百科英文版：第1问“人生的首要目的”）', 'https://en.wikipedia.org/wiki/Westminster_Shorter_Catechism', ['chief end']),
 'conf_w':   ('奥古斯丁《忏悔录》（维基百科英文版：“我们的心若不安息在你怀中，便不得安宁”）', 'https://en.wikipedia.org/wiki/Confessions_(Augustine)', ['restless']),
 'alimujiang19':('Alimujiang A, et al. Association Between Life Purpose and Mortality Among US Adults Older Than 50 Years. JAMA Netw Open 2019;2(5):e194270（人生目标与死亡率：6,985人；PubMed 31125099）', 'https://doi.org/10.1001/jamanetworkopen.2019.4270', []),
 'cohen16':  ('Cohen R, Bavishi C, Rozanski A. Purpose in Life and Its Relationship to All-Cause Mortality and Cardiovascular Events: A Meta-Analysis. Psychosom Med 2016;78(2):122-33（人生目标：10项研究、136,265人的荟萃分析；PubMed 26630073）', 'https://doi.org/10.1097/PSY.0000000000000274', []),
 'ed13':     ('怀爱伦《教育论》第1章“真教育的来源和目的”，英文原著第13页', None, []),
 'da20':     ('怀爱伦《历代愿望》第1章“上帝与我们同在”，英文原著第20页', None, []),
 'dss_w':    ('死海古卷（Dead Sea Scrolls，维基百科英文版：1946—1947年发现；约40%是希伯来圣经的抄本）', 'https://en.wikipedia.org/wiki/Dead_Sea_Scrolls', ['Masoretic']),
 'greatisa_w':('以赛亚书大卷（1QIsaᵃ，维基百科英文版：约公元前125年，完整的以赛亚书）', 'https://en.wikipedia.org/wiki/Great_Isaiah_Scroll', ['1QIsa']),
 'teldan_w': ('但丘石碑（Tel Dan stele，维基百科英文版：1993—1994年发现，提到“大卫家”）', 'https://en.wikipedia.org/wiki/Tel_Dan_stele', ['House of David']),
 'merne_w':  ('麦伦普塔石碑（Merneptah Stele，维基百科英文版：约公元前1208年，提到“以色列”）', 'https://en.wikipedia.org/wiki/Merneptah_Stele', ['1208']),
 'siloam_w': ('西罗亚碑文（Siloam inscription，维基百科英文版：1880年在希西家水道中发现）', 'https://en.wikipedia.org/wiki/Siloam_inscription', ['Hezekiah']),
 'pilate_w': ('彼拉多石碑（Pilate stone，维基百科英文版：1961年在该撒利亚发现）', 'https://en.wikipedia.org/wiki/Pilate_stone', ['1961']),
 'textcrit_w':('新约经文鉴别学（Textual criticism of the New Testament，维基百科英文版：5,800多份希腊文抄本；约30万处异文，大多是词序等细节）', 'https://en.wikipedia.org/wiki/Textual_criticism_of_the_New_Testament', ['5,800']),
 'ntmss_w':  ('圣经抄本（Biblical manuscript，维基百科英文版：梅茨格对荷马《伊利亚特》抄本的统计；埃尔曼的提醒）', 'https://en.wikipedia.org/wiki/Biblical_manuscript', ['Homer']),
 'sm1_16':   ('怀爱伦《信息选粹》第1册，英文原著第16—17页', None, []),
 'sm1_21':   ('怀爱伦《信息选粹》第1册，英文原著第21—22页', None, []),
 'gcvii':    ('怀爱伦《善恶之争》序言，英文原著第vi—vii页', None, []),
 'creationism_w':('创造论（Creationism，维基百科英文版：年轻地球、古老地球、有神演化等各种看法；百科称创造论“常被视为伪科学”）', 'https://en.wikipedia.org/wiki/Creationism', ['theistic evolution']),
 'finetune_w':('宇宙的精细调节（Fine-tuned universe，维基百科英文版：约31个物理常数、霍伊尔的话，以及不同意见）', 'https://en.wikipedia.org/wiki/Fine-tuned_universe', ['Hoyle']),
 'sdafb_w':  ('基督复临安息日会28条基本信仰（维基百科英文版：第6条“创造”）', 'https://en.wikipedia.org/wiki/28_Fundamental_Beliefs', ['Creation']),
 'pp111':    ('怀爱伦《先祖与先知》第9章“字面的一周”，英文原著第111—112页', None, []),
 'ed128':    ('怀爱伦《教育论》第14章“科学与圣经”，英文原著第128—130页', None, []),
 'dunn08':   ('Dunn EW, Aknin LB, Norton MI. Spending money on others promotes happiness. Science 2008;319(5870):1687-8（为别人花钱更快乐；PubMed 18356530）', 'https://doi.org/10.1126/science.1150952', []),
 'kahneman10':('Kahneman D, Deaton A. High income improves evaluation of life but not emotional well-being. PNAS 2010;107(38):16489-93（收入与幸福：45万多份回答；PubMed 20823223）', 'https://doi.org/10.1073/pnas.1011492107', []),
 'killingsworth23':('Killingsworth MA, Kahneman D, Mellers B. Income and emotional well-being: A conflict resolved. PNAS 2023;120(10):e2208661120（两派学者合作重新分析；PubMed 36857342）', 'https://doi.org/10.1073/pnas.2208661120', []),
 'dittmar14':('Dittmar H, et al. The relationship between materialism and personal well-being: A meta-analysis. J Pers Soc Psychol 2014;107(5):879-924（物质主义与幸福感：259个样本的荟萃分析；PubMed 25347131）', 'https://doi.org/10.1037/a0037409', []),
 'tithe_w':  ('什一奉献（Tithe，维基百科英文版：古代近东、圣经、各教派的做法）', 'https://en.wikipedia.org/wiki/Tithe', ['Malachi']),
 'col351':   ('怀爱伦《基督比喻实训》“才干”一章，英文原著第351—352页', None, []),
 'cs138':    ('怀爱伦《论管家》英文原著第138—139页', None, []),
 'cs66':     ('怀爱伦《论管家》英文原著第66—67页', None, []),
 'cs157':    ('怀爱伦《论管家》第32章“错用财富”，英文原著第157页', None, []),
 'orlich13': ('Orlich MJ, et al. Vegetarian dietary patterns and mortality in Adventist Health Study 2. JAMA Intern Med 2013;173(13):1230-8（复临信徒健康研究2：73,308人；PubMed 23836264）', 'https://doi.org/10.1001/jamainternmed.2013.6473', []),
 'gbd18':    ('GBD 2016 Alcohol Collaborators. Alcohol use and burden for 195 countries and territories, 1990–2016. Lancet 2018;392:1015-35（全球疾病负担研究：饮酒；PubMed 30146330）', 'https://doi.org/10.1016/S0140-6736(18)31310-2', []),
 'doll04':   ('Doll R, Peto R, Boreham J, Sutherland I. Mortality in relation to smoking: 50 years’ observations on male British doctors. BMJ 2004;328:1519（英国医生吸烟50年追踪：34,439人；PubMed 15213107）', 'https://doi.org/10.1136/bmj.38142.554479.AE', []),
 'ahs_w':    ('复临信徒健康研究（Adventist Health Studies，维基百科英文版：1960年起的几项研究）', 'https://en.wikipedia.org/wiki/Adventist_Health_Studies', ['Loma Linda']),
 'mh127':    ('怀爱伦《服务真诠》“自然疗法”，英文原著第127页', None, []),
 'mh296':    ('怀爱伦《服务真诠》“饮食与健康”，英文原著第295—296页', None, []),
 'barnum_w': ('巴纳姆效应（Barnum effect，维基百科英文版：1947年斯塔格纳、1948年福勒的实验）', 'https://en.wikipedia.org/wiki/Barnum_effect', ['Forer']),
 'astro_w':  ('占星术与科学（Astrology and science，维基百科英文版：1985年卡尔森发表在《自然》的双盲实验）', 'https://en.wikipedia.org/wiki/Astrology_and_science', ['Carlson']),
 'fengshui_w':('风水（Feng shui，维基百科英文版：五位风水师对同一住宅意见各不相同；基督徒的批评）', 'https://en.wikipedia.org/wiki/Feng_shui', ['pseudoscience']),
 'pp679':    ('怀爱伦《先祖与先知》第66章“扫罗之死”，英文原著第679页', None, []),
 'gc551':    ('怀爱伦《善恶之争》第34章“死人能和我们说话吗？”，英文原著第551页', None, []),
 'ancestor_w':('祖先崇拜（Veneration of the dead，维基百科英文版：目的、社会功能、各宗教的看法；韩国新教徒不行祭祖礼）', 'https://en.wikipedia.org/wiki/Veneration_of_the_dead', ['filial piety']),
 'rites_w':  ('中国礼仪之争（Chinese Rites controversy，维基百科英文版：利玛窦、1704年禁令、1742年重申、1939年解禁）', 'https://en.wikipedia.org/wiki/Chinese_Rites_controversy', ['Ricci']),
 'qingming_w':('清明节（Qingming Festival，维基百科英文版：扫墓、献食物、烧香和纸钱；2008年起为法定假日）', 'https://en.wikipedia.org/wiki/Qingming_Festival', ['2008']),
 'gc552':    ('怀爱伦《善恶之争》第34章“死人能和我们说话吗？”，英文原著第551—552页', None, []),
 'robles14': ('Robles TF, et al. Marital quality and health: a meta-analytic review. Psychol Bull 2014;140(1):140-87（126篇研究、7.2万多人；PubMed 23527470）', 'https://doi.org/10.1037/a0031859', []),
 'holt10':   ('Holt-Lunstad J, Smith TB, Layton JB. Social relationships and mortality risk: a meta-analytic review. PLoS Med 2010;7(7):e1000316（148项研究、30.8万人；PubMed 20668659）', 'https://doi.org/10.1371/journal.pmed.1000316', []),
 'kg05':     ('Kiecolt-Glaser JK, et al. Hostile marital interactions, proinflammatory cytokine production, and wound healing. Arch Gen Psychiatry 2005;62(12):1377-84（42对夫妻；PubMed 16330726）', 'https://doi.org/10.1001/archpsyc.62.12.1377', []),
 'ah340':    ('怀爱伦《复临信徒家庭》第56章“离婚”，英文原著第340—341页', None, []),
 'ah341':    ('怀爱伦《复临信徒家庭》第56章“离婚”，英文原著第341—342页', None, []),
 'ah343':    ('怀爱伦《复临信徒家庭》第56章“离婚”，英文原著第343—344页', None, []),
 'gershoff16':('Gershoff ET, Grogan-Kaylor A. Spanking and child outcomes: old controversies and new meta-analyses. J Fam Psychol 2016;30(4):453-69（111个效应量、160,927名儿童；PubMed 27055181）', 'https://doi.org/10.1037/fam0000191', []),
 'larzelere05':('Larzelere RE, Kuhn BR. Comparing child outcomes of physical punishment and alternative disciplinary tactics: a meta-analysis. Clin Child Fam Psychol Rev 2005;8(1):1-37（26项研究；PubMed 15898303）', 'https://doi.org/10.1007/s10567-005-2340-z', []),
 'parstyle_w':('教养方式（Parenting styles，维基百科英文版：鲍姆林德的分类，回应与要求两个维度）', 'https://en.wikipedia.org/wiki/Parenting_styles', ['Baumrind']),
 'cg244':    ('怀爱伦《儿童教育指南》“施行纠正的管教”，英文原著第244页', None, []),
 'cg245':    ('怀爱伦《儿童教育指南》“施行纠正的管教”，英文原著第245—246页', None, []),
 'cg250':    ('怀爱伦《儿童教育指南》“施行纠正的管教”，英文原著第250—251页', None, []),
 'cg283':    ('怀爱伦《儿童教育指南》英文原著第283页', None, []),
 'cg225':    ('怀爱伦《儿童教育指南》英文原著第225—226页', None, []),
 # 《启示录的兽、印记、666》（beast.py）用到的资料：2026-10 用临时任务读取原文核对（怀著按原版逐页文字，标准页码）
 'number_w': ('666（Number of the beast，维基百科英文版：χξϛ/616、尼禄、爱任纽、梵蒂冈头衔、对印记的几派看法）', 'https://en.wikipedia.org/wiki/Number_of_the_beast', ['Nero']),
 'vfd_w': ('Vicarius Filii Dei（维基百科英文版：赫尔维希1612年、乌利亚·史密斯1866年、1948年《事工》杂志更正、天主教的回应）', 'https://en.wikipedia.org/wiki/Vicarius_Filii_Dei', ['Helwig']),
 'p115_w': ('第115号蒲草纸（Papyrus 115，维基百科英文版：约225—275年，数目作616）', 'https://en.wikipedia.org/wiki/Papyrus_115', ['616']),
 'hist_w': ('历史主义解经法（Historicism，维基百科英文版：宗教改革家的看法）', 'https://en.wikipedia.org/wiki/Historicism_(Christianity)', ['Luther']),
 'futur_w': ('未来主义解经法（Futurism，维基百科英文版：耶稣会士里贝拉、达秘）', 'https://en.wikipedia.org/wiki/Futurism_(Christianity)', ['Ribera']),
 'pret_w': ('过去主义解经法（Preterism，维基百科英文版：耶稣会士阿尔卡萨1614年）', 'https://en.wikipedia.org/wiki/Preterism', ['Alcazar']),
 'dayyear_w': ('一日顶一年的原则（Day-year principle，维基百科英文版）', 'https://en.wikipedia.org/wiki/Day-year_principle', ['Numbers 14']),
 'pius6_w': ('教皇庇护六世（Pope Pius VI，维基百科英文版：1798年被法军俘虏，1799年死于瓦朗斯）', 'https://en.wikipedia.org/wiki/Pope_Pius_VI', ['1798']),
 'sdaesch_w': ('复临信徒的末世论（Seventh-day Adventist eschatology，维基百科英文版）', 'https://en.wikipedia.org/wiki/Seventh-day_Adventist_eschatology', ['1798']),
 'antichrist_w': ('敌基督（Antichrist，维基百科英文版：约翰书信、施马加登信条、卫斯理）', 'https://en.wikipedia.org/wiki/Antichrist', ['Smalcald']),
 'wcf_w': ('《威斯敏斯德信条》（维基百科英文版：第25章第6节原文与后来的修改）', 'https://en.wikipedia.org/wiki/Westminster_Confession_of_Faith', ['Antichrist']),
 'siege538_w': ('罗马之围（537—538年，维基百科英文版：东哥特人于538年3月撤围）', 'https://en.wikipedia.org/wiki/Siege_of_Rome_(537%E2%80%93538)', ['538']),
 'vandal_w': ('汪达尔战争（533—534年，维基百科英文版）', 'https://en.wikipedia.org/wiki/Vandalic_War', ['534']),
 'odoacer_w': ('奥多亚克（Odoacer，维基百科英文版：率赫鲁利等族人，493年被杀）', 'https://en.wikipedia.org/wiki/Odoacer', ['493']),
 'irenaeus': ('爱任纽《驳异端》第5卷第30章（约180年，英译本）', 'https://www.newadvent.org/fathers/0103530.htm', ['Lateinos']),
 'ccc882': ('《天主教教理》第882条（梵蒂冈网站英文版）', 'https://www.vatican.va/archive/ENG0015/__P2A.HTM', ['Vicar of Christ']),
 'ccc1461': ('《天主教教理》第1461条（英文版）', 'https://www.scborromeo.org/ccc/para/1461.htm', ['forgive']),
 'gc266': ('怀爱伦《善恶之争》第15章“圣经与法国革命”，英文原著第266页', None, []),
 'gc438': ('怀爱伦《善恶之争》第25章“上帝的律法永不改变”，英文原著第438页', None, []),
 'gc439': ('怀爱伦《善恶之争》第25章“上帝的律法永不改变”，英文原著第439页', None, []),
 'gc440': ('怀爱伦《善恶之争》第25章“上帝的律法永不改变”，英文原著第440—441页', None, []),
 'gc442': ('怀爱伦《善恶之争》第25章“上帝的律法永不改变”，英文原著第442页', None, []),
 'gc445': ('怀爱伦《善恶之争》第25章“上帝的律法永不改变”，英文原著第445—446页', None, []),
 'gc449': ('怀爱伦《善恶之争》第25章“上帝的律法永不改变”，英文原著第449页', None, []),
 'gc452': ('怀爱伦《善恶之争》第26章“改革的工作”，英文原著第452页', None, []),
 'gc565': ('怀爱伦《善恶之争》第35章“信仰自由受到威胁”，英文原著第565页', None, []),
 'gc579': ('怀爱伦《善恶之争》第35章“信仰自由受到威胁”，英文原著第579页', None, []),
 'gc605': ('怀爱伦《善恶之争》第38章“最后的警告”，英文原著第604—605页', None, []),
 'ev234': ('怀爱伦《布道论》英文原著第234页（1899年手稿第51号）', None, []),
 'ev304': ('怀爱伦《布道论》英文原著第304页（1902年信函第190号）', None, []),
 'ev573': ('怀爱伦《布道论》“向天主教徒传道”，英文原著第573—574页（1887年手稿第14号）', None, []),
 'lde224': ('怀爱伦《末世大事记》英文原著第224页（引1897年《给巴特尔克里克教会的特别证言》第6—7页）', None, []),
 'tm117': ('怀爱伦《给传道人的证言》英文原著第117页', None, []),
 # 《1844年，天上发生了什么？》（judgment.py）用到的资料：2026-10 用临时任务读取原文核对（怀著按原版逐页文字，标准页码）
 'ij_w': ('查案审判（Investigative judgment，维基百科英文版：基本信仰第24条、1857年詹姆斯·怀特首用这个词、批评与回应）', 'https://en.wikipedia.org/wiki/Investigative_judgment', ['1857']),
 'edson_w': ('希兰·埃德森（Hiram Edson，维基百科英文版：1844年10月23日玉米地的领悟）', 'https://en.wikipedia.org/wiki/Hiram_Edson', ['cornfield']),
 'millerism_w': ('米勒耳运动（Millerism，维基百科英文版：“第七月信息”、卡拉派历法）', 'https://en.wikipedia.org/wiki/Millerism', ['Karaite']),
 'ford_w': ('德斯蒙德·福特（Desmond Ford，维基百科英文版：1980年冰川景观会议）', 'https://en.wikipedia.org/wiki/Desmond_Ford', ['Glacier View']),
 'seventy_w': ('七十个七的预言（Prophecy of Seventy Weeks，维基百科英文版：批判学者的读法）', 'https://en.wikipedia.org/wiki/Prophecy_of_Seventy_Weeks', ['Antiochus']),
 'dan8_w': ('但以理书第8章（Daniel 8，维基百科英文版：批判学者的读法）', 'https://en.wikipedia.org/wiki/Daniel_8', ['Antiochus']),
 'art1_w': ('亚达薛西一世（Artaxerxes I，维基百科英文版：公元前465—424年在位；以斯拉记7章）', 'https://en.wikipedia.org/wiki/Artaxerxes_I', ['465']),
 'antio_w': ('安提阿哥四世（Antiochus IV Epiphanes，维基百科英文版）', 'https://en.wikipedia.org/wiki/Antiochus_IV_Epiphanes', ['167']),
 'yk_w': ('赎罪日（Yom Kippur，维基百科英文版：犹太传统中的审判日）', 'https://en.wikipedia.org/wiki/Yom_Kippur', ['sealed']),
 'unet_w': ('《让我们述说》祷文（Unetanneh Tokef，维基百科英文版）', 'https://en.wikipedia.org/wiki/Unetanneh_Tokef', ['sealed']),
 'partj_w': ('私审判（Particular judgment，维基百科英文版）', 'https://en.wikipedia.org/wiki/Particular_judgment', ['general judgment']),
 'ccc1022': ('《天主教教理》第1022条（英文版）', 'https://www.scborromeo.org/ccc/para/1022.htm', ['particular judgment']),
 'ccc1038': ('《天主教教理》第1038条（英文版）', 'https://www.scborromeo.org/ccc/para/1038.htm', ['Last Judgment']),
 'mishnah_rh': ('《密释纳·新年篇》1:2（Sefaria 英译）', 'https://www.sefaria.org/Mishnah_Rosh_Hashanah.1.2', ['judged']),
 'talmud_rh': ('巴比伦塔木德《新年篇》16b（Sefaria 英译）', 'https://www.sefaria.org/Rosh_Hashanah.16b', ['three books']),
 'gc409': ('怀爱伦《善恶之争》第23章“圣所是什么？”，英文原著第409页', None, []),
 'gc416': ('怀爱伦《善恶之争》第23章“圣所是什么？”，英文原著第416页', None, []),
 'gc422': ('怀爱伦《善恶之争》第23章“圣所是什么？”，英文原著第422页', None, []),
 'gc423': ('怀爱伦《善恶之争》第24章“在至圣所里”，英文原著第423页', None, []),
 'gc424': ('怀爱伦《善恶之争》第24章“在至圣所里”，英文原著第424页', None, []),
 'gc426': ('怀爱伦《善恶之争》第24章“在至圣所里”，英文原著第426页', None, []),
 'gc428': ('怀爱伦《善恶之争》第24章“在至圣所里”，英文原著第428页', None, []),
 'gc482': ('怀爱伦《善恶之争》第28章“面对一生的记录”，英文原著第482—483页', None, []),
 'gc484': ('怀爱伦《善恶之争》第28章“面对一生的记录”，英文原著第484页', None, []),
 'gc485': ('怀爱伦《善恶之争》第28章“面对一生的记录”，英文原著第485页', None, []),
 'gc489': ('怀爱伦《善恶之争》第28章“面对一生的记录”，英文原著第489—490页', None, []),
 'ew55': ('怀爱伦《早期著作》英文原著第55页', None, []),
 'ev221': ('怀爱伦《布道论》英文原著第221—222页', None, []),
 'sc62b': ('怀爱伦《拾级就主》第7章“作门徒的考验”，英文原著第62页', None, []),
 'wlf12': ('怀爱伦《致小群的信》（1847年）英文原著第12页', None, []),
 'lde74': ('怀爱伦《末世大事记》英文原著第74页（引《天上的处所》227页）', None, []),
 'lde229': ('怀爱伦《末世大事记》英文原著第229页（引《复临信徒圣经注释》第7卷989页，1906年）', None, []),
 # 《家人总在念叨》（listen.py）用到的资料：医学文献 2026-10 在 PubMed 逐篇核对（摘要、DOI）；怀著和百科用临时任务读取原文核对
 'linton12': ('Linton SJ, et al. Painfully reassuring? The effects of validation on emotions and adherence in a pain test. Eur J Pain 2012;16(4):592-9（“认可感受”与“否定感受”的随机对照实验；PubMed 22396087）', 'https://doi.org/10.1016/j.ejpain.2011.07.011', []),
 'starr08':  ('Starr LR, Davila J. Excessive reassurance seeking, depression, and interpersonal rejection: a meta-analytic review. J Abnorm Psychol 2008;117(4):762-75（反复寻求安慰、抑郁与被人疏远：荟萃分析；PubMed 19025224）', 'https://doi.org/10.1037/a0013866', []),
 'rose02':   ('Rose AJ. Co-rumination in the friendships of girls and boys. Child Dev 2002;73(6):1830-43（“一起反刍”：608名学生；PubMed 12487497）', 'https://doi.org/10.1111/1467-8624.00509', []),
 'bolger00': ('Bolger N, Zuckerman A, Kessler RC. Invisible support and adjustment to stress. J Pers Soc Psychol 2000;79(6):953-61（“看不见的支持”；PubMed 11138764）', 'https://doi.org/10.1037/0022-3514.79.6.953', []),
 'butzlaff98':('Butzlaff RL, Hooley JM. Expressed emotion and psychiatric relapse: a meta-analysis. Arch Gen Psychiatry 1998;55(6):547-52（家庭“情绪表达”与复发：荟萃分析；PubMed 9633674）', 'https://doi.org/10.1001/archpsyc.55.6.547', []),
 'holt10':   ('Holt-Lunstad J, Smith TB, Layton JB. Social relationships and mortality risk: a meta-analytic review. PLoS Med 2010;7(7):e1000316（人际关系与死亡风险：148项研究、308,849人；PubMed 20668659）', 'https://doi.org/10.1371/journal.pmed.1000316', []),
 'klimecki14':('Klimecki OM, et al. Differential pattern of functional brain plasticity after compassion and empathy training. Soc Cogn Affect Neurosci 2014;9(6):873-9（“共情训练”与“慈悲训练”的对比；PubMed 23576808）', 'https://doi.org/10.1093/scan/nst060', []),
 'frase24':  ('Frase RT, et al. Worrying Across the Generations: The Impact of Adult Grandchildren\'s Problems on Grandparents\' Well-Being. J Gerontol B Psychol Sci Soc Sci 2024;79(11)（隔代的挂念；PubMed 39271131）', 'https://doi.org/10.1093/geronb/gbae154', []),
 'wang20':   ('Wang H, et al. Middle-aged adults\' daily sleep and worries about aging parents and adult children. J Fam Psychol 2020;34(5):621-629（为成年子女担心与当晚睡眠；PubMed 32052985）', 'https://doi.org/10.1037/fam0000642', []),
 'ee_w':     ('情绪表达（Expressed emotion，维基百科英文版：家人怎样谈论病人；批评、敌意、过度卷入）', 'https://en.wikipedia.org/wiki/Expressed_emotion', ['overinvolvement']),
 'contag_w': ('情绪传染（Emotional contagion，维基百科英文版：哈特菲尔德等人的“模仿—趋同”两步说）', 'https://en.wikipedia.org/wiki/Emotional_contagion', ['Hatfield']),
 'mh483':    ('怀爱伦《服务真诠》第41章“与人相处”，英文原著第483—484页', None, []),
 'mh486':    ('怀爱伦《服务真诠》第41章“与人相处”，英文原著第486页', None, []),
 'mh487':    ('怀爱伦《服务真诠》第41章“与人相处”，英文原著第487页', None, []),
 'da146':    ('怀爱伦《历代愿望》第15章“在婚筵上”，英文原著第146页', None, []),
 'da752':    ('怀爱伦《历代愿望》“髑髅地”一章，英文原著第752页', None, []),
 'ah360':    ('怀爱伦《复临信徒家庭》第59章“年老的父母”，英文原著第360页', None, []),
 'ah363':    ('怀爱伦《复临信徒家庭》第59章“年老的父母”，英文原著第363页', None, []),
 'ah438':    ('怀爱伦《复临信徒家庭》英文原著第438—439页', None, []),
 'ah441':    ('怀爱伦《复临信徒家庭》英文原著第441—442页', None, []),
 # 《喜乐的心乃是良药》（joy.py）用到的资料：医学文献 2026-10 在 PubMed 逐篇核对（摘要、DOI）；怀著和百科用临时任务读取原文核对
 'rozanski19':('Rozanski A, et al. Association of Optimism With Cardiovascular Events and All-Cause Mortality: A Systematic Review and Meta-analysis. JAMA Netw Open 2019;2(9):e1912200（乐观与心血管事件、全因死亡：15项研究、229,391人的荟萃分析；PubMed 31560385）', 'https://doi.org/10.1001/jamanetworkopen.2019.12200', []),
 'lee19':    ('Lee LO, et al. Optimism is associated with exceptional longevity in 2 epidemiologic cohorts of men and women. PNAS 2019;116(37):18357-62（乐观与长寿：护士健康研究的女性、退伍军人研究的男性；PubMed 31451635）', 'https://doi.org/10.1073/pnas.1900712116', []),
 'kim17':    ('Kim ES, et al. Optimism and Cause-Specific Mortality: A Prospective Cohort Study. Am J Epidemiol 2017;185(1):21-29（护士健康研究70,021名女性；PubMed 27927621）', 'https://doi.org/10.1093/aje/kww182', []),
 'li16':     ('Li S, et al. Association of Religious Service Attendance With Mortality Among Women. JAMA Intern Med 2016;176(6):777-85（74,534名女性，参加礼拜与死亡率；PubMed 27183175）', 'https://doi.org/10.1001/jamainternmed.2016.1615', []),
 'yirmiya09':('Yirmiya R, Bab I. Major depression is a risk factor for low bone mineral density: a meta-analysis. Biol Psychiatry 2009;66(5):423-32（抑郁与骨密度：23项研究的荟萃分析；PubMed 19446797）', 'https://doi.org/10.1016/j.biopsych.2009.03.016', []),
 'segerstrom04':('Segerstrom SC, Miller GE. Psychological stress and the human immune system: a meta-analytic study of 30 years of inquiry. Psychol Bull 2004;130(4):601-30（压力与免疫：300多篇研究的荟萃分析；PubMed 15250815）', 'https://doi.org/10.1037/0033-2909.130.4.601', []),
 'dowlati10':('Dowlati Y, et al. A meta-analysis of cytokines in major depression. Biol Psychiatry 2010;67(5):446-57（抑郁症患者的炎症因子：24项研究的荟萃分析；PubMed 20015486）', 'https://doi.org/10.1016/j.biopsych.2009.09.033', []),
 'brosschot06':('Brosschot JF, Gerin W, Thayer JF. The perseverative cognition hypothesis: a review of worry, prolonged stress-related physiological activation, and health. J Psychosom Res 2006;60(2):113-24（反复担忧会延长身体的压力反应；PubMed 16439263）', 'https://doi.org/10.1016/j.jpsychores.2005.06.074', []),
 'schoemaker16':('Schoemaker MJ, et al. Psychological stress, adverse life events and breast cancer incidence: a cohort investigation in 106,000 women in the United Kingdom. Breast Cancer Res 2016;18(1):72（压力与乳腺癌发病：英国10.6万名女性；PubMed 27418063）', 'https://doi.org/10.1186/s13058-016-0733-1', []),
 'heikkila13':('Heikkilä K, et al. Work stress and risk of cancer: meta-analysis of 5700 incident cancer events in 116,000 European men and women. BMJ 2013;346:f165（工作压力与癌症：欧洲11.6万人；PubMed 23393080）', 'https://doi.org/10.1136/bmj.f165', []),
 'chida08':  ('Chida Y, et al. Do stress-related psychosocial factors contribute to cancer incidence and survival? Nat Clin Pract Oncol 2008;5(8):466-75（压力相关心理因素与癌症的荟萃分析；PubMed 18493231）', 'https://doi.org/10.1038/ncponc1134', []),
 'guth09':   ('Guth S, et al. Very high prevalence of thyroid nodules detected by high frequency (13 MHz) ultrasound examination. Eur J Clin Invest 2009;39(8):699-706（体检人群甲状腺结节的检出率；PubMed 19601965）', 'https://doi.org/10.1111/j.1365-2362.2009.02162.x', []),
 'kuehner17':('Kuehner C. Why is depression more common among women than among men? Lancet Psychiatry 2017;4(2):146-158（为什么女性抑郁比男性多；PubMed 27856392）', 'https://doi.org/10.1016/S2215-0366(16)30263-2', []),
 'johnson13':('Johnson DP, Whisman MA. Gender differences in rumination: A meta-analysis. Pers Individ Dif 2013;55(4):367-374（反刍思维的性别差异：59项研究、14,321人；PubMed 24089583）', 'https://doi.org/10.1016/j.paid.2013.03.019', []),
 'vaish08':  ('Vaish A, Grossmann T, Woodward A. Not all emotions are created equal: the negativity bias in social-emotional development. Psychol Bull 2008;134(3):383-403（负面偏向；PubMed 18444702）', 'https://doi.org/10.1037/0033-2909.134.3.383', []),
 'emmons03': ('Emmons RA, McCullough ME. Counting blessings versus burdens: an experimental investigation of gratitude and subjective well-being in daily life. J Pers Soc Psychol 2003;84(2):377-89（“数算恩典”的随机对照实验；PubMed 12585811）', 'https://doi.org/10.1037/0022-3514.84.2.377', []),
 'diniz23':  ('Diniz G, et al. The effects of gratitude interventions: a systematic review and meta-analysis. Einstein (São Paulo) 2023;21:eRW0371（感恩练习：64项随机对照试验的荟萃分析；PubMed 37585888）', 'https://doi.org/10.31744/einstein_journal/2023RW0371', []),
 'negbias_w':('负面偏向（Negativity bias，维基百科英文版：鲍迈斯特等人的综述“坏比好更有力”）', 'https://en.wikipedia.org/wiki/Negativity_bias', ['Baumeister']),
 'rumin_w':  ('反刍思维（Rumination，维基百科英文版：诺伦-霍克西玛的反应风格理论、性别差异）', 'https://en.wikipedia.org/wiki/Rumination_(psychology)', ['Nolen-Hoeksema']),
 'mh241':    ('怀爱伦《服务真诠》（The Ministry of Healing）第18章“心灵的医治”，英文原著第241页', None, []),
 'mh229':    ('怀爱伦《服务真诠》“为病人祷告”一章，英文原著第229页', None, []),
 'mh251':    ('怀爱伦《服务真诠》第18章“心灵的医治”，英文原著第251—252页', None, []),
 'mh360':    ('怀爱伦《服务真诠》“婚姻”一章，英文原著第360—361页', None, []),
 'mh373':    ('怀爱伦《服务真诠》“母亲”一章，英文原著第373—374页', None, []),
 'mh481':    ('怀爱伦《服务真诠》“日常生活中的帮助”一章，英文原著第481页', None, []),
 'sc116':    ('怀爱伦《拾级就主》第13章“在主里欢喜”，英文原著第116—118页', None, []),
 # 《要“完全”才能见主吗？》（perfect.py）和《信了主，还会失去救恩吗？》（lose.py）用到的资料：2026-10 用临时任务读取原文核对
 'col69':    ('怀爱伦《基督比喻实训》第3章“先发苗，后长穗”，英文原著第68—69页', None, []),
 'sm1_382':  ('怀爱伦《信息选粹》第1册“耶稣接纳我们的心意”，英文原著第382页', None, []),
 'augs12':   ('《奥格斯堡信条》第12条“论悔改”', 'https://bookofconcord.org/augsburg-confession/article-xii/', ['once justified']),
 'perfection_w':('基督徒的完全（Christian perfection，维基百科英文版：加尔文主义、卫斯理《基督徒完全的清楚说明》1777年）', 'https://en.wikipedia.org/wiki/Christian_perfection', ['Plain Account']),
 'eternalsec_w':('永远的保障（Eternal security，维基百科英文版：各宗派的看法）', 'https://en.wikipedia.org/wiki/Eternal_security', ['Lutheran']),
 'unpard_w': ('不得赦免的罪（Eternal sin，维基百科英文版）', 'https://en.wikipedia.org/wiki/Eternal_sin', ['Matthew 12']),
 # 《“我必快来”，为什么还没来？》（soon.py）用到的资料：2026-10 用临时任务读取原文核对
 'ussher_w': ('乌雪年代学（Ussher chronology，维基百科英文版：创造之日推算为公元前4004年）', 'https://en.wikipedia.org/wiki/Ussher_chronology', ['4004']),
 'dating_w': ('推算创造的年代（Dating creation，维基百科英文版：马所拉本创造到洪水1656年；七十士译本推算约公元前5500年）', 'https://en.wikipedia.org/wiki/Dating_creation', ['1,656']),
 'hebcal_w': ('希伯来历（维基百科英文版：创世纪年5787年始于2026年9月11日日落）', 'https://en.wikipedia.org/wiki/Hebrew_calendar', ['5787']),
 'wycliffe_stat':('威克理夫全球联会（Wycliffe Global Alliance）：2025年圣经翻译统计', 'https://www.wycliffe.net/resources/statistics/', ['7,396']),
 'printing_w':('印刷机（维基百科英文版：路德约1520年成为欧洲作品印行最多的作者）', 'https://en.wikipedia.org/wiki/Printing_press', ['Luther']),
 'chatgpt_w':('ChatGPT（维基百科英文版：推出两个月月活跃用户达1亿）', 'https://en.wikipedia.org/wiki/ChatGPT', ['100 million']),
 't2_194':   ('怀爱伦《教会证言》第2卷，英文原著第194页', None, []),
 'sm1_188':  ('怀爱伦《信息选粹》（Selected Messages）第1册“警惕定时间”，英文原著第188页', None, []),
 'gc458':    ('怀爱伦《善恶之争》第26章“改革的工作”，英文原著第458页', None, []),
 'da633':    ('怀爱伦《历代愿望》第69章“在橄榄山上”，英文原著第633—634页', None, []),
 'gc518':    ('怀爱伦《善恶之争》第32章“撒但的罗网”，英文原著第518页', None, []),
 # 《上帝早就定好谁得救吗？》（elect.py）用到的资料：2026-10 用临时任务读取原文核对
 'calvin_inst21':('加尔文《基督教要义》第3卷第21章第5节（英译本，CCEL）', 'https://ccel.org/ccel/calvin/institutes/institutes.v.xxii.html', ['eternal decree']),
 'calvin_inst23':('加尔文《基督教要义》第3卷第23章第7节（英译本，CCEL）', 'https://ccel.org/ccel/calvin/institutes/institutes.v.xxiv.html', ['dreadful']),
 'wesley_fg':('卫斯理讲章《白白的恩典》（Free Grace，1739年；1872年版第128篇）', 'https://wesley.nnu.edu/john-wesley/the-sermons-of-john-wesley-1872-edition/sermon-128-free-grace/', ['FREE FOR ALL']),
 'foc11':    ('路德宗《协同信条》（1577年）摘要第11条“论拣选”', 'https://bookofconcord.org/formula-of-concord-epitome/article-xi/', ['foreknowledge']),
 'newcalv_w':('“新加尔文主义”（维基百科英文版：2009年《时代》周刊列为“正在改变世界的十个观念”之一）', 'https://en.wikipedia.org/wiki/New_Calvinism', ['2009']),
 'predest_w':('预定论（维基百科英文版：各宗派的看法）', 'https://en.wikipedia.org/wiki/Predestination', ['double predestination']),
 'pp207':    ('怀爱伦《先祖与先知》第19章“归回迦南”，英文原著第207—208页', None, []),
 # 《旧约的上帝和新约的上帝》（god.py）用到的资料：2026-10 用临时任务读取原文核对
 'marcion_w':('马吉安（Marcion of Sinope，约85—160年，维基百科英文版）', 'https://en.wikipedia.org/wiki/Marcion_of_Sinope', ['144']),
 'marcionism_w':('马吉安主义（维基百科英文版）', 'https://en.wikipedia.org/wiki/Marcionism', ['wrathful']),
 'sc10':     ('怀爱伦《拾级就主》第1章“上帝对人类的爱”，英文原著第10—11页', None, []),
 'pp366':    ('怀爱伦《先祖与先知》（Patriarchs and Prophets）第32章“律法与两约”，英文原著第366—367页', None, []),
 'gc36':     ('怀爱伦《善恶之争》第1章“耶路撒冷的毁灭”，英文原著第36页', None, []),
 # 《我还会犯罪，能得救吗？》（rom7.py）用到的资料：2026-10 用临时任务读取原文核对
 'luther_simul':('路德的神学：“同时是义人又是罪人”（simul justus et peccator，维基百科英文版）', 'https://en.wikipedia.org/wiki/Theology_of_Martin_Luther', ['simul']),
 'antinom_wiki':('反律主义（维基百科英文版：阿格里科拉、路德的批评、《协同信条》第5、6条）', 'https://en.wikipedia.org/wiki/Antinomianism', ['Agricola']),
 'wcf_text':('《威斯敏斯德信条》全文（美国正统长老会网站），第3章“论上帝永远的预旨”、第17章“论圣徒的坚忍”', 'https://www.opc.org/wcf.html', ['predestinated']),
 'dort_text':('《多特信经》全文（北美基督教改革宗教会网站），第五要点“圣徒的坚忍”第1—3条', 'https://www.crcna.org/welcome/beliefs/confessions/canons-dort', ['Perseverance']),
 'augs6':('《奥格斯堡信条》第6条“论新的顺从”', 'https://bookofconcord.org/augsburg-confession/article-vi/', ['obedience']),
 'dort_wiki':('多特会议（1618—1619年，维基百科英文版）', 'https://en.wikipedia.org/wiki/Synod_of_Dort', ['1618']),
 'armin_wiki':('阿民念主义（维基百科英文版：阿民念、1610年《抗辩书》）', 'https://en.wikipedia.org/wiki/Arminianism', ['Remonstrance']),
 'tulip_wiki':('加尔文主义五要点（维基百科英文版）', 'https://en.wikipedia.org/wiki/Five_Points_of_Calvinism', ['Perseverance']),
 'freegrace_wiki':('“自由恩典神学”（Free Grace theology，维基百科英文版）', 'https://en.wikipedia.org/wiki/Free_Grace_theology', ['eternal security']),
 'lgt_wiki':('“最后一代神学”（Last Generation Theology，维基百科英文版）', 'https://en.wikipedia.org/wiki/Last_Generation_Theology', ['perfection']),
 'sdatheo_wiki':('复临安息日会神学（维基百科英文版：基督人性之争与“最后一代”之争，两种看法在复临教会圣经研究所都有代表）', 'https://en.wikipedia.org/wiki/Seventh-day_Adventist_theology', ['Last Generation']),
 'calvin_r7':('加尔文《罗马书注释》第7章（英译本，BibleHub 网站）', 'https://biblehub.com/commentaries/calvin/romans/7.htm', ['regenerate']),
 'wesley_r7':('卫斯理《新约注释》（Explanatory Notes）罗马书第7章（BibleHub 网站）', 'https://biblehub.com/commentaries/wes/romans/7.htm', ['evangelical state']),
 'sc19':     ('怀爱伦《拾级就主》第2章“罪人需要基督”，英文原著第19页', None, []),
 'sc31':     ('怀爱伦《拾级就主》第3章“悔改”，英文原著第31页', None, []),
 'sc47':     ('怀爱伦《拾级就主》第5章“献身”，英文原著第47—48页', None, []),
 'sc51':     ('怀爱伦《拾级就主》第6章“信心与接纳”，英文原著第51页', None, []),
 'sc57':     ('怀爱伦《拾级就主》第7章“作门徒的考验”，英文原著第57—58页', None, []),
 'sc60':     ('怀爱伦《拾级就主》第7章“作门徒的考验”，英文原著第59—60页', None, []),
 'sc62':     ('怀爱伦《拾级就主》第7章“作门徒的考验”，英文原著第62—63页', None, []),
 'sc64':     ('怀爱伦《拾级就主》第7章“作门徒的考验”，英文原著第64页', None, []),
 'col155':   ('怀爱伦《基督比喻实训》（Christ’s Object Lessons）“两个祷告的人”，英文原著第155页', None, []),
 'da668':    ('怀爱伦《历代愿望》第73章“你们心里不要忧愁”，英文原著第668页', None, []),
 'da671b':   ('怀爱伦《历代愿望》第73章“你们心里不要忧愁”，英文原著第671页', None, []),
 'gc425':    ('怀爱伦《善恶之争》第24章“在至圣所里”，英文原著第425页', None, []),
 'gc471':    ('怀爱伦《善恶之争》第27章“现代的奋兴”，英文原著第471—472页', None, []),
 'mb76':     ('怀爱伦《福山宝训》（Thoughts from the Mount of Blessing），英文原著第76页', None, []),
 # 《安息日，到底能做什么？》（keep.py）用到的资料：2026-10 读取原文核对
 'bri_guide':('基督复临安息日会圣经研究所：《守安息日指引》（1981年设立的委员会所写，1985年全球总会代表大会表决接收；文件说明不作为教会法规）', 'https://adventistbiblicalresearch.org/articles/sabbath-observance-guidelines', ['Sabbath']),
 'kenya_sda':('肯尼亚《标准报》：法院下令公立中学允许复临信徒学生从星期五晚上到星期六不上课', 'https://www.standardmedia.co.ke/amp/article/2000084618/sda-students-now-get-their-sabbath-back', ['Sabbath']),
 'gaokao_zh':('普通高等学校招生全国统一考试（中文维基百科）', 'https://zh.wikipedia.org/wiki/%E6%99%AE%E9%80%9A%E9%AB%98%E7%AD%89%E5%AD%A6%E6%A0%A1%E6%8B%9B%E7%94%9F%E5%85%A8%E5%9B%BD%E7%BB%9F%E4%B8%80%E8%80%83%E8%AF%95', ['6月7']),
 'ielts_wiki':('雅思考试（维基百科英文版）', 'https://en.wikipedia.org/wiki/International_English_Language_Testing_System', ['month']),
 'toefl_wiki':('托福考试（维基百科英文版）', 'https://en.wikipedia.org/wiki/TOEFL', ['Home Edition']),
 'da207':    ('怀爱伦《历代愿望》第21章“毕士大和公会”，英文原著第207页', None, []),
 't6_354':   ('怀爱伦《教会证言》第6卷“守安息日”，英文原著第354页', None, []),
 't6_355':   ('怀爱伦《教会证言》第6卷“守安息日”，英文原著第355—356页', None, []),
 't6_357':   ('怀爱伦《教会证言》第6卷“守安息日”，英文原著第357页', None, []),
 't6_358':   ('怀爱伦《教会证言》第6卷“守安息日”，英文原著第358页', None, []),
 't6_361':   ('怀爱伦《教会证言》第6卷“守安息日”，英文原著第361页', None, []),
 't6_362':   ('怀爱伦《教会证言》第6卷“守安息日”，英文原著第361—362页', None, []),
 # 《谁改了安息日？》（sabbath.py）用到的资料：2026-10 用临时任务逐一读取原文核对
 'augsburg28':('《奥格斯堡信条》第28条“论教会的权柄”第33节（1530年，路德宗）', 'https://bookofconcord.org/augsburg-confession/', ['Sabbath']),
 'ccc2175':  ('《天主教教理》第2174—2175条（梵蒂冈网站英文版）', 'https://www.vatican.va/archive/ENG0015/__P7O.HTM', ['2175']),
 'cathen_sun':('天主教百科全书（1912年）：“星期日”条', 'https://www.newadvent.org/cathen/14335a.htm', ['Sabbath']),
 'gibbons':  ('吉本斯枢机主教《先贤的信仰》（The Faith of Our Fathers，古腾堡计划电子版，据1917年第93版）', 'https://www.gutenberg.org/cache/epub/27435/pg27435.txt', ['Sunday']),
 'wcf21':    ('《威斯敏斯德信条》第21章第7节（1646年，长老会）', 'https://bpc.org/wcf-ch-21', ['first day']),
 'greg_wiki':('格里高利历（维基百科英文版）', 'https://en.wikipedia.org/wiki/Gregorian_calendar', ['1582']),
 'days_wiki':('一周各天的名称（维基百科英文版）', 'https://en.wikipedia.org/wiki/Names_of_the_days_of_the_week', ['Sabbath']),
 'sunday_wiki':('星期日（维基百科英文版，载君士坦丁321年法令的英译）', 'https://en.wikipedia.org/wiki/Sunday', ['venerable']),
 'zh_week':  ('星期（中文维基百科）', 'https://zh.wikipedia.org/wiki/%E6%98%9F%E6%9C%9F', ['安息日']),
 'bates_wiki':('约瑟·贝茨（维基百科英文版）', 'https://en.wikipedia.org/wiki/Joseph_Bates_(Adventist)', ['1846']),
 'preston_wiki':('瑞秋·奥克斯·普雷斯顿（维基百科英文版）', 'https://en.wikipedia.org/wiki/Rachel_Oakes_Preston', ['1844']),
 'gc52':     ('怀爱伦《善恶之争》第3章“属灵黑暗的时代”，英文原著第52页', None, []),
 'gc53':     ('怀爱伦《善恶之争》第3章“属灵黑暗的时代”，英文原著第53页', None, []),
 'gc434':    ('怀爱伦《善恶之争》第25章“上帝的律法永不改变”，英文原著第434—435页', None, []),
 'da287':    ('怀爱伦《历代愿望》第29章“安息日”，英文原著第287页', None, []),
 'da288':    ('怀爱伦《历代愿望》第29章“安息日”，英文原著第288页', None, []),
 'pp48':     ('怀爱伦《先祖与先知》第2章“创造”，英文原著第48页', None, []),
 # 《根据圣经，人死了去哪里？》（death.py）用到的怀著：2026-10 据怀著托管会逐页原版文字核对（标准页码）
 'gc533':    ('怀爱伦《善恶之争》第33章“第一个大骗局”，英文原著第533页', None, []),
 'gc533b':   ('怀爱伦《善恶之争》第33章“第一个大骗局”，英文原著第533页', None, []),
 'gc534':    ('怀爱伦《善恶之争》第33章“第一个大骗局”，英文原著第534页', None, []),
 'gc545':    ('怀爱伦《善恶之争》第33章“第一个大骗局”，英文原著第545页', None, []),
 'gc549':    ('路德《所罗门传道书释义》第152页，转引自怀爱伦《善恶之争》英文原著第549页', None, []),
 'gc550':    ('怀爱伦《善恶之争》第33章“第一个大骗局”，英文原著第550页', None, []),
 'da787':    ('怀爱伦《历代愿望》第81章“主已经复活了”，英文原著第787页', None, []),
})
# 补充问答页里属于怀爱伦著作的资料（history.py 的 src_kind 用来归类）
EGW_KEYS = {'gc409', 'gc416', 'gc422', 'gc423', 'gc424', 'gc426', 'gc428', 'gc482', 'gc484', 'gc485', 'gc489', 'ew55', 'ev221', 'sc62b', 'wlf12', 'lde74', 'lde229', 'gc266', 'gc438', 'gc439', 'gc440', 'gc442', 'gc445', 'gc449', 'gc452', 'gc565', 'gc579', 'gc605', 'ev234', 'ev304', 'ev573', 'lde224', 'tm117', 'da123', 'da671', 'da686', 'da688', 'da692', 'da693', 'da25', 'da210', 'rh1887', 'rh1888', 'st1888', 't5_422', 't2_509',
            't2_202', 'rh1888s', 'rh1893m', 'rh1893a', 'rh1874', 'yi1898', 'lt97', 'bc5_1131', 'sc17', 'sc43', 'sc58', 'pp49', 'pp306',
            'gc493', 'aa560', 'aa561', 'pp48', 't6_354', 't6_355', 't6_357', 't6_358', 't6_361', 't6_362',
            'sc19', 'sc31', 'sc47', 'sc51', 'sc57', 'sc60', 'sc62', 'sc64', 'col155', 'da668', 'da671b', 'gc425', 'gc471', 'mb76', 'sc10', 'pp366', 'gc36', 'pp207', 't2_194', 'sm1_188', 'gc458', 'da633', 'gc518', 'col69', 'sm1_382',
            'pp679', 'gc551', 'gc552', 'ah340', 'ah341', 'ah343', 'cg244', 'cg245', 'cg250', 'cg283', 'cg225', 'mh127', 'mh296', 'col351', 'cs138', 'cs66', 'cs157', 'pp111', 'ed128', 'sm1_16', 'sm1_21', 'gcvii', 'ed13', 'da20', 'gc492', 'gc498', 'gc678', 'pp34', 'pp42', 'pp49', 'pp331', 'da224',
            'mh483', 'mh486', 'mh487', 'da146', 'da752', 'ah360', 'ah363', 'ah438', 'ah441',
            'mh229', 'mh241', 'mh251', 'mh360', 'mh373', 'mh481', 'sc116'}
