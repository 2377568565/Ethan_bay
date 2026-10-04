# 问题彩蛋：每篇问答一条。正文在 qa/<src>（PDF 与网页共用同一份）
import os
_HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(_HERE, 'qa') if os.path.isdir(os.path.join(_HERE, 'qa')) else os.path.join(_HERE, '..', 'qa')
ITEMS = [
    dict(id='qa1', no=1, src='q1.html', q='罪孽为何使人与上帝隔绝？', sub='以赛亚书 59:2 深度解析',
         lesson=1, day='wed', dayname='星期三《被逐出园外》',
         teaser='不是上帝不愿意听，也不是祂听不到，而是罪本身就是“离开上帝”。',
         pdf='研经问答01-罪孽为何使人与上帝隔绝.pdf'),
    dict(id='qa2', no=2, src='q2.html', q='罪从哪里来？', sub='上帝创造了一切，难道罪也是上帝造的吗？',
         lesson=1, day='mon', dayname='星期一《躲避上帝》',
         teaser='不是。上帝造了“自由”，受造者用这份自由造出了“罪”。',
         pdf='研经问答02-罪从哪里来.pdf'),
    # url：内容多、图表多，单独做成一个网页（tools/q4/history.py 生成），卡片和学课里的入口直接打开它
    dict(id='qa3', no=3, url='history.html', q='基督教两千年家谱', sub='复临安息日会从哪里来？各大教派怎样分出来、有什么不同？',
         lesson=12, day='wed', dayname='星期三《末时的余民》',
         teaser='像家谱一样从耶稣一直画到今天：各教派的来历、核心信仰、与复临信仰的异同，还有路德和怀爱伦的人物特写；每个说法都附出处。'),
    dict(id='qa4', no=4, url='jesus.html', q='耶稣是人还是神？', sub='祂既有神性，对抗试探岂不是比我们容易？祂还能作我们的榜样吗？',
         lesson=4, day='sun', dayname='星期日《作为先知的耶稣》',
         teaser='祂拥有神性，却不拿来帮自己；旷野的第一个试探，正是试探祂动用神性。用圣经一步一步讲清楚，祂为什么既是榜样，又是救主。'),
    # nochip：不在学课那一天再加入口（第4课星期日已有原文的入口），只在问题彩蛋里放卡片
    dict(id='qa5', no=5, url='jesus-qa.html', q='耶稣是人还是神？补充问答', sub='“犯罪的倾向”是什么？耶稣为什么没有？公平吗？重生以后呢？',
         lesson=4, day='sun', dayname='星期日《作为先知的耶稣》', nochip=True,
         teaser='读完上一篇后的十六个追问：倾向与试探、亚当的堕落与遗传、几种说法的客观对照与评估、重生以后的倾向，以及客西马尼园的祷告。'),
]
