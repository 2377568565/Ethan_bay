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
]
