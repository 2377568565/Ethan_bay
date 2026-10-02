#!/usr/bin/env python3
"""《基督教两千年家谱》页面引用的资料：编号 → (说明, 网址, 用来核对的关键词)。
python3 tools/q4/history_sources.py --check 会逐个打开网址，核对页面里确实有这些关键词（GitHub 上的 history-check.yml 用它）。"""
import json, re, sys, urllib.request

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

def check():
    ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36'
    out = {}
    for k, (desc, url, keys) in SRC.items():
        try:
            r = urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': ua, 'Accept-Language': 'en'}), timeout=40)
            body = r.read().decode('utf-8', 'replace')
            title = re.sub(r'\s+', ' ', (re.search(r'<title[^>]*>(.*?)</title>', body, re.S | re.I) or [None, ''])[1]).strip()[:90]
            miss = [w for w in keys if w.lower() not in body.lower()]
            out[k] = {'ok': not miss, 'status': r.status, 'final': r.geturl(), 'title': title, 'missing': miss}
        except Exception as e:
            out[k] = {'ok': False, 'status': getattr(e, 'code', 0), 'error': str(e)[:120]}
        o = out[k]
        print(('OK  ' if o['ok'] else 'BAD ') + k, o.get('status'), o.get('final', url) if o.get('final') != url else '', o.get('title', o.get('error', '')), ('缺 ' + str(o['missing'])) if o.get('missing') else '', flush=True)
    print(sum(o['ok'] for o in out.values()), '/', len(out), '可用')
    return out

if __name__ == '__main__':
    if '--check' in sys.argv:
        check()
