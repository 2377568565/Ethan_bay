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
