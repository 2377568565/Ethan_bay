# 由 GitHub 上 history-check 的核对结果整理（2026-10-02）：资料键 → (核对通过的网址, 核对方式)
# 核对方式：live＝直接打开网页；archive 时间＝网站拒绝程序访问，改用网页时光机当时的存档核对；pubmed＝用 PubMed 接口核对；search＝网站拒绝程序读取，用搜索引擎的原文摘要核对
CHECKED = {
 'adventist': ('https://en.wikipedia.org/wiki/Millerites', 'live'),
 'ag_hist': ('https://ag.org/About/About-the-AG/History', 'archive 20260904170718'),
 'anabapt': ('https://www.britannica.com/topic/Anabaptists', 'archive 20260907042701'),
 'anglican': ('https://www.britannica.com/topic/Anglicanism', 'archive 20260927061008'),
 'anglicancomm': ('https://www.anglicancommunion.org/structures/member-churches.aspx', 'archive 20260228040703'),
 'augsburg': ('https://bookofconcord.org/augsburg-confession/', 'live'),
 'augustine': ('https://www.britannica.com/biography/Saint-Augustine', 'archive 20260930145916'),
 'awakening': ('https://www.britannica.com/event/Great-Awakening', 'archive 20260605172402'),
 'awakening2': ('https://www.britannica.com/topic/Second-Great-Awakening', 'archive 20260729091024'),
 'baptist': ('https://www.britannica.com/biography/John-Smyth', 'archive 20260210135437'),
 'brethren': ('https://www.britannica.com/topic/Plymouth-Brethren', 'archive 20260714093925'),
 'bwa2': ('https://baptistworld.org/', 'live'),
 'calvin': ('https://www.britannica.com/biography/John-Calvin', 'archive 20260906161140'),
 'chalc_ce': ('https://www.newadvent.org/cathen/03555a.htm', 'live'),
 'chalcedon': ('https://www.britannica.com/event/Council-of-Chalcedon', 'archive 20260905193009'),
 'creed_ce': ('https://www.newadvent.org/cathen/11049a.htm', 'live'),
 'disappoint': ('https://en.wikipedia.org/wiki/Great_Disappointment', 'live'),
 'disciples': ('https://www.britannica.com/topic/Disciples-of-Christ', 'archive 20260219170456'),
 'dispens': ('https://en.wikipedia.org/wiki/Dispensationalism', 'live'),
 'east': ('https://www.newadvent.org/cathen/10755a.htm', 'live'),
 'edson_wiki': ('https://en.wikipedia.org/wiki/Hiram_Edson', 'live'),
 'egw_est': ('https://whiteestate.org/about/egwbio/', 'live'),
 'egw_wiki': ('https://en.wikipedia.org/wiki/Ellen_G._White', 'live'),
 'ephesus': ('https://www.newadvent.org/cathen/05491a.htm', 'live'),
 'ephesus_ce': ('https://www.newadvent.org/cathen/05491a.htm', 'live'),
 'ethiopia': ('https://en.wikipedia.org/wiki/Ethiopian_Orthodox_Tewahedo_Church', 'live'),
 'fraser': ('https://pubmed.ncbi.nlm.nih.gov/11434797/', 'pubmed'),
 'gc1863': ('https://adventistreview.org/magazine-article/a-pivotal-session/', 'search'),
 'gregory': ('https://www.britannica.com/biography/Saint-Gregory-I', 'archive 20160804024316'),
 'gutenberg': ('https://www.britannica.com/biography/Johannes-Gutenberg', 'archive 20260921031836'),
 'hus': ('https://www.britannica.com/biography/Jan-Hus', 'archive 20260908082914'),
 'ignatius': ('https://www.newadvent.org/fathers/0105.htm', 'live'),
 'justin': ('https://www.newadvent.org/fathers/0126.htm', 'live'),
 'laodicea': ('https://www.newadvent.org/fathers/3806.htm', 'live'),
 'larue': ('https://www.adventist.asia/news/how-did-one-mans-journey-start-a-global-movement-1/', 'archive 20240815041948'),
 'lbc1689': ('https://www.the1689confession.com/', 'live'),
 'luther': ('https://www.britannica.com/biography/Martin-Luther', 'archive 20260927061152'),
 'luther_bible': ('https://en.wikipedia.org/wiki/Luther_Bible', 'live'),
 'luther_ce': ('https://www.newadvent.org/cathen/09438b.htm', 'live'),
 'luther_jews': ('https://en.wikipedia.org/wiki/Martin_Luther_and_antisemitism', 'live'),
 'luther_name': ('https://en.wikipedia.org/wiki/History_of_Lutheranism', 'live'),
 'luther_pref': ('https://christianhistoryinstitute.org/magazine/article/luthers-breakthrough', 'live'),
 'luther_worms': ('https://christianhistoryinstitute.org/magazine/article/diet-of-worms', 'live'),
 'lutheranism': ('https://en.wikipedia.org/wiki/Lutheranism', 'live'),
 'lwf': ('https://lutheranworld.org/who-we-are', 'live'),
 'menno': ('https://www.britannica.com/biography/Menno-Simons', 'archive 20260909183348'),
 'menno_wiki': ('https://en.wikipedia.org/wiki/Menno_Simons', 'live'),
 'methodism': ('https://www.britannica.com/topic/Methodism', 'archive 20260919094935'),
 'milan': ('https://www.britannica.com/topic/Edict-of-Milan', 'archive 20260914085548'),
 'miller': ('https://www.britannica.com/biography/William-Miller', 'archive 20260224035840'),
 'morrison': ('https://www.britannica.com/biography/Robert-Morrison', 'archive 20250913134533'),
 'nee': ('https://www.britannica.com/biography/Watchman-Nee', 'archive 20260704063253'),
 'nee_wiki': ('https://en.wikipedia.org/wiki/Watchman_Nee', 'live'),
 'nicaea': ('https://www.britannica.com/event/First-Council-of-Nicaea-325', 'archive 20260904104645'),
 'nicaea_ce': ('https://www.newadvent.org/cathen/11044a.htm', 'live'),
 'oriental': ('https://www.britannica.com/topic/Oriental-Orthodox-church', 'archive 20251111085744'),
 'pentecost': ('https://www.britannica.com/topic/Pentecostalism', 'archive 20260911043920'),
 'pentecost_wiki': ('https://en.wikipedia.org/wiki/Pentecostalism', 'live'),
 'pew': ('https://www.pewresearch.org/religion/2011/12/19/global-christianity-exec/', 'live'),
 'pliny': ('https://www.britannica.com/biography/Pliny-the-Younger', 'archive 20260831132437'),
 'pliny_txt': ('https://sourcebooks.fordham.edu/source/pliny1.asp', 'live'),
 'presby': ('https://www.britannica.com/biography/John-Knox', 'archive 20260220211248'),
 'quaker': ('https://www.britannica.com/topic/Friends', 'archive 20260427012503'),
 'restoration': ('https://en.wikipedia.org/wiki/Restoration_Movement', 'live'),
 'ricci': ('https://www.britannica.com/biography/Matteo-Ricci', 'archive 20260920050025'),
 'schism': ('https://www.britannica.com/event/Schism-of-1054', 'archive 20190401032957'),
 'scot_ref': ('https://en.wikipedia.org/wiki/Scottish_Reformation', 'live'),
 'sda_beliefs': ('https://www.adventist.org/beliefs/', 'archive 20260418102002'),
 'sda_brit': ('https://www.britannica.com/topic/Seventh-day-Adventist-church', 'archive 20251225170630'),
 'sda_china': ('https://en.wikipedia.org/wiki/Seventh-day_Adventist_Church_in_China', 'live'),
 'sda_dead': ('https://www.adventist.org/death-and-resurrection/', 'archive 20250613201700'),
 'sda_egw': ('https://www.adventist.org/gift-of-prophecy/', 'archive 20250501091554'),
 'sda_hist': ('https://www.adventist.org/who-are-seventh-day-adventists/history-of-seventh-day-adventists/', 'archive 20250613192659'),
 'sda_hist_wiki': ('https://en.wikipedia.org/wiki/History_of_the_Seventh-day_Adventist_Church', 'live'),
 'sda_sabbath': ('https://www.adventist.org/the-sabbath/', 'archive 20250609151646'),
 'sda_sanct': ('https://www.adventist.org/christs-ministry-in-the-heavenly-sanctuary/', 'archive 20250613193423'),
 'sda_stats': ('https://www.adventist.org/statistics/', 'archive 20250512212121'),
 'sda_supper': ('https://www.adventist.org/the-lords-supper/', 'archive 20250428093407'),
 'sda_trinity': ('https://www.adventist.org/trinity/', 'archive 20250621072731'),
 'sda_wiki': ('https://en.wikipedia.org/wiki/Seventh-day_Adventist_Church', 'live'),
 'sdb2': ('https://www.sabbathrecorder.com/2013/10/22/a-thumbnail-sketch-of-seventh-day-baptists/', 'live'),
 'sdb_org': ('https://seventhdaybaptist.org/', 'live'),
 'socrates': ('https://www.newadvent.org/fathers/26015.htm', 'live'),
 'sozomen': ('https://www.newadvent.org/fathers/26027.htm', 'live'),
 'stele': ('https://en.wikipedia.org/wiki/Xi%27an_Stele', 'live'),
 'sunday321': ('https://www.britannica.com/topic/Sunday-day-of-week', 'archive 20260826091336'),
 'supremacy': ('https://en.wikipedia.org/wiki/Acts_of_Supremacy', 'live'),
 'taylor': ('https://en.wikipedia.org/wiki/Hudson_Taylor', 'live'),
 'tertullian': ('https://www.britannica.com/biography/Tertullian', 'archive 20260908154128'),
 'theodosius': ('https://www.britannica.com/biography/Theodosius-I', 'archive 20260806185347'),
 'theses': ('https://www.britannica.com/event/Ninety-five-Theses', 'archive 20260927202118'),
 'theses_txt': ('https://www.luther.de/en/95thesen.html', 'live'),
 'thessalonica': ('https://en.wikipedia.org/wiki/Edict_of_Thessalonica', 'live'),
 'tjc': ('https://tjc.org/', 'live'),
 'tjc_wiki': ('https://en.wikipedia.org/wiki/True_Jesus_Church', 'live'),
 'trent': ('https://www.britannica.com/event/Council-of-Trent', 'archive 20260726195518'),
 'trinity_ce': ('https://www.newadvent.org/cathen/15047a.htm', 'live'),
 'vatican2': ('https://www.britannica.com/event/Second-Vatican-Council', 'archive 20260920092952'),
 'vatican2_wiki': ('https://en.wikipedia.org/wiki/Second_Vatican_Council', 'live'),
 'wald_ce': ('https://www.newadvent.org/cathen/15527b.htm', 'live'),
 'waldenses': ('https://www.britannica.com/topic/Waldenses', 'archive 20260912082459'),
 'wcrc': ('https://wcrc.ch/about-us', 'archive 20240803020209'),
 'wcrc2': ('https://wcrc.eu/', 'live'),
 'wesley': ('https://www.britannica.com/biography/John-Wesley', 'archive 20260902231556'),
 'westminster': ('https://www.britannica.com/topic/Westminster-Confession', 'archive 20260219152218'),
 'williams': ('https://en.wikipedia.org/wiki/First_Baptist_Church_in_America', 'live'),
 'wmc': ('https://worldmethodistcouncil.org/about/', 'live'),
 'worms_wiki': ('https://en.wikipedia.org/wiki/Diet_of_Worms', 'live'),
 'wyc_ce': ('https://www.newadvent.org/cathen/15722a.htm', 'live'),
 'wycliffe': ('https://www.britannica.com/biography/John-Wycliffe', 'archive 20260928021659'),
 'zwingli': ('https://www.britannica.com/biography/Huldrych-Zwingli', 'archive 20260713232550'),
 # 2026-10-04：《教义问答》一章的资料（GitHub 上直接下载原文核对）
 'valentine': ('https://encyclopedia.adventist.org/assets/pdf/article-6JJ3.pdf', 'live'),
 'unruh77': ('https://www.adventistlaymen.org/Selected%20Documents%20and%20Manuscripts/THE%20SEVENTH-DAY%20ADVENTIST%20EVANGELICAL%20CONFERENCES%20OF%201955-1956.pdf', 'live'),
 'br1914': ('https://documents.adventistarchives.org/Books/BR1914.pdf', 'live'),
 'br1949': ('https://documents.adventistarchives.org/Books/BR1949.pdf', 'live'),
 'min1956': ('https://cdn.ministerialassociation.org/cdn/ministrymagazine.org/issues/1956/issues/MIN1956-09.pdf', 'live'),
 'knight03': ('https://digitalcommons.andrews.edu/adventist-books/1', 'live'),
 'whidden03': ('https://www.ministrymagazine.org/archive/2003/08/questions-on-doctrine-then-and-now.html', 'live'),
 'douglass04': ('https://www.ministrymagazine.org/archive/2004/08/thoughts-on-the-republished-questions-on-doctrine.html', 'live'),
 'rh1896': ('https://documents.adventistarchives.org/Periodicals/RH/RH18961215-V73-50.pdf', 'live'),
 'yi1900': ('https://documents.adventistarchives.org/Periodicals/YI/YI19001220-V48-50.pdf', 'live'),
 'qod2007': ('https://digitalcommons.andrews.edu/qod/', 'live'),
 'w_andreasen': ('https://en.wikipedia.org/wiki/M._L._Andreasen', 'live'),
 # 2026-10-04：补充问答页的资料（GitHub 上直接打开原文核对）
 'da123': ('https://ccel.org/ccel/white/desire.xv.html', 'live'),
 'da671': ('https://ccel.org/ccel/white/desire.lxxvi.html', 'live'),
 'da686': ('https://ccel.org/ccel/white/desire.lxxvii.html', 'live'),
 'da688': ('https://ccel.org/ccel/white/desire.lxxvii.html', 'live'),
 'da692': ('https://ccel.org/ccel/white/desire.lxxvii.html', 'live'),
 'da693': ('https://ccel.org/ccel/white/desire.lxxvii.html', 'live'),
 'rh1887': ('https://documents.adventistarchives.org/Periodicals/RH/RH18871108-V64-44.pdf', 'live'),
 'rh1888': ('https://documents.adventistarchives.org/Periodicals/RH/RH18880327-V65-13.pdf', 'live'),
 'st1888': ('https://documents.adventistarchives.org/Periodicals/ST/ST18880323-V14-12.pdf', 'live'),
 'sc17': ('https://ccel.org/ccel/white/steps.v.html', 'live'),
 'irving': ('https://www.encyclopedia.com/people/philosophy-and-religion/protestant-christianity-biographies/edward-irving', 'live'),
 'tgc': ('https://www.thegospelcoalition.org/article/you-asked-did-jesus-assume-a-fallen-human-nature/', 'live'),
 'augsburg28': ('https://bookofconcord.org/augsburg-confession/', 'live'),
 'ccc2175': ('https://www.vatican.va/archive/ENG0015/__P7O.HTM', 'live'),
 'cathen_sun': ('https://www.newadvent.org/cathen/14335a.htm', 'live'),
 'gibbons': ('https://www.gutenberg.org/cache/epub/27435/pg27435.txt', 'live'),
 'wcf21': ('https://bpc.org/wcf-ch-21', 'live'),
 'greg_wiki': ('https://en.wikipedia.org/wiki/Gregorian_calendar', 'live'),
 'days_wiki': ('https://en.wikipedia.org/wiki/Names_of_the_days_of_the_week', 'live'),
 'sunday_wiki': ('https://en.wikipedia.org/wiki/Sunday', 'live'),
 'zh_week': ('https://zh.wikipedia.org/wiki/%E6%98%9F%E6%9C%9F', 'live'),
 'bates_wiki': ('https://en.wikipedia.org/wiki/Joseph_Bates_(Adventist)', 'live'),
 'preston_wiki': ('https://en.wikipedia.org/wiki/Rachel_Oakes_Preston', 'live'),
 'bri_guide': ('https://adventistbiblicalresearch.org/articles/sabbath-observance-guidelines', 'live'),
 'augs12': ('https://bookofconcord.org/augsburg-confession/article-xii/', 'live'),
 'perfection_w': ('https://en.wikipedia.org/wiki/Christian_perfection', 'live'),
 'eternalsec_w': ('https://en.wikipedia.org/wiki/Eternal_security', 'live'),
 'unpard_w': ('https://en.wikipedia.org/wiki/Eternal_sin', 'live'),
 'ussher_w': ('https://en.wikipedia.org/wiki/Ussher_chronology', 'live'),
 'dating_w': ('https://en.wikipedia.org/wiki/Dating_creation', 'live'),
 'hebcal_w': ('https://en.wikipedia.org/wiki/Hebrew_calendar', 'live'),
 'wycliffe_stat': ('https://www.wycliffe.net/resources/statistics/', 'live'),
 'printing_w': ('https://en.wikipedia.org/wiki/Printing_press', 'live'),
 'chatgpt_w': ('https://en.wikipedia.org/wiki/ChatGPT', 'live'),
 'calvin_inst21': ('https://ccel.org/ccel/calvin/institutes/institutes.v.xxii.html', 'live'),
 'calvin_inst23': ('https://ccel.org/ccel/calvin/institutes/institutes.v.xxiv.html', 'live'),
 'wesley_fg': ('https://wesley.nnu.edu/john-wesley/the-sermons-of-john-wesley-1872-edition/sermon-128-free-grace/', 'live'),
 'foc11': ('https://bookofconcord.org/formula-of-concord-epitome/article-xi/', 'live'),
 'newcalv_w': ('https://en.wikipedia.org/wiki/New_Calvinism', 'live'),
 'predest_w': ('https://en.wikipedia.org/wiki/Predestination', 'live'),
 'marcion_w': ('https://en.wikipedia.org/wiki/Marcion_of_Sinope', 'live'),
 'marcionism_w': ('https://en.wikipedia.org/wiki/Marcionism', 'live'),
 'calvin_r7': ('https://biblehub.com/commentaries/calvin/romans/7.htm', 'live'),
 'wesley_r7': ('https://biblehub.com/commentaries/wes/romans/7.htm', 'live'),
 'luther_simul': ('https://en.wikipedia.org/wiki/Theology_of_Martin_Luther', 'live'),
 'antinom_wiki': ('https://en.wikipedia.org/wiki/Antinomianism', 'live'),
 'wcf_text': ('https://www.opc.org/wcf.html', 'live'),
 'dort_text': ('https://www.crcna.org/welcome/beliefs/confessions/canons-dort', 'live'),
 'augs6': ('https://bookofconcord.org/augsburg-confession/article-vi/', 'live'),
 'dort_wiki': ('https://en.wikipedia.org/wiki/Synod_of_Dort', 'live'),
 'armin_wiki': ('https://en.wikipedia.org/wiki/Arminianism', 'live'),
 'tulip_wiki': ('https://en.wikipedia.org/wiki/Five_Points_of_Calvinism', 'live'),
 'freegrace_wiki': ('https://en.wikipedia.org/wiki/Free_Grace_theology', 'live'),
 'lgt_wiki': ('https://en.wikipedia.org/wiki/Last_Generation_Theology', 'live'),
 'sdatheo_wiki': ('https://en.wikipedia.org/wiki/Seventh-day_Adventist_theology', 'live'),
 'kenya_sda': ('https://www.standardmedia.co.ke/amp/article/2000084618/sda-students-now-get-their-sabbath-back', 'live'),
 'gaokao_zh': ('https://zh.wikipedia.org/wiki/%E6%99%AE%E9%80%9A%E9%AB%98%E7%AD%89%E5%AD%A6%E6%A0%A1%E6%8B%9B%E7%94%9F%E5%85%A8%E5%9B%BD%E7%BB%9F%E4%B8%80%E8%80%83%E8%AF%95', 'live'),
 'ielts_wiki': ('https://en.wikipedia.org/wiki/International_English_Language_Testing_System', 'live'),
 'toefl_wiki': ('https://en.wikipedia.org/wiki/TOEFL', 'live'),
 'rozanski19': ('https://doi.org/10.1001/jamanetworkopen.2019.12200', 'live'),
 'lee19': ('https://doi.org/10.1073/pnas.1900712116', 'live'),
 'kim17': ('https://doi.org/10.1093/aje/kww182', 'live'),
 'li16': ('https://doi.org/10.1001/jamainternmed.2016.1615', 'live'),
 'yirmiya09': ('https://doi.org/10.1016/j.biopsych.2009.03.016', 'live'),
 'segerstrom04': ('https://doi.org/10.1037/0033-2909.130.4.601', 'live'),
 'dowlati10': ('https://doi.org/10.1016/j.biopsych.2009.09.033', 'live'),
 'brosschot06': ('https://doi.org/10.1016/j.jpsychores.2005.06.074', 'live'),
 'schoemaker16': ('https://doi.org/10.1186/s13058-016-0733-1', 'live'),
 'heikkila13': ('https://doi.org/10.1136/bmj.f165', 'live'),
 'chida08': ('https://doi.org/10.1038/ncponc1134', 'live'),
 'guth09': ('https://doi.org/10.1111/j.1365-2362.2009.02162.x', 'live'),
 'kuehner17': ('https://doi.org/10.1016/S2215-0366(16)30263-2', 'live'),
 'johnson13': ('https://doi.org/10.1016/j.paid.2013.03.019', 'live'),
 'vaish08': ('https://doi.org/10.1037/0033-2909.134.3.383', 'live'),
 'emmons03': ('https://doi.org/10.1037/0022-3514.84.2.377', 'live'),
 'diniz23': ('https://doi.org/10.31744/einstein_journal/2023RW0371', 'live'),
 'negbias_w': ('https://en.wikipedia.org/wiki/Negativity_bias', 'live'),
 'rumin_w': ('https://en.wikipedia.org/wiki/Rumination_(psychology)', 'live'),
 'linton12': ('https://doi.org/10.1016/j.ejpain.2011.07.011', 'live'),
 'starr08': ('https://doi.org/10.1037/a0013866', 'live'),
 'rose02': ('https://doi.org/10.1111/1467-8624.00509', 'live'),
 'bolger00': ('https://doi.org/10.1037/0022-3514.79.6.953', 'live'),
 'butzlaff98': ('https://doi.org/10.1001/archpsyc.55.6.547', 'live'),
 'holt10': ('https://doi.org/10.1371/journal.pmed.1000316', 'live'),
 'klimecki14': ('https://doi.org/10.1093/scan/nst060', 'live'),
 'frase24': ('https://doi.org/10.1093/geronb/gbae154', 'live'),
 'wang20': ('https://doi.org/10.1037/fam0000642', 'live'),
 'ee_w': ('https://en.wikipedia.org/wiki/Expressed_emotion', 'live'),
 'contag_w': ('https://en.wikipedia.org/wiki/Emotional_contagion', 'live'),
 'poe_w': ('https://en.wikipedia.org/wiki/Problem_of_evil', 'live'),
 'lisbon_w': ('https://en.wikipedia.org/wiki/1755_Lisbon_earthquake', 'live'),
 'pain_w': ('https://en.wikipedia.org/wiki/The_Problem_of_Pain', 'live'),
 'frankl_w': ("https://en.wikipedia.org/wiki/Man's_Search_for_Meaning", 'live'),
 'wsc_w': ('https://en.wikipedia.org/wiki/Westminster_Shorter_Catechism', 'live'),
 'conf_w': ('https://en.wikipedia.org/wiki/Confessions_(Augustine)', 'live'),
 'alimujiang19': ('https://doi.org/10.1001/jamanetworkopen.2019.4270', 'live'),
 'cohen16': ('https://doi.org/10.1097/PSY.0000000000000274', 'live'),
 'dss_w': ('https://en.wikipedia.org/wiki/Dead_Sea_Scrolls', 'live'),
 'greatisa_w': ('https://en.wikipedia.org/wiki/Great_Isaiah_Scroll', 'live'),
 'teldan_w': ('https://en.wikipedia.org/wiki/Tel_Dan_stele', 'live'),
 'merne_w': ('https://en.wikipedia.org/wiki/Merneptah_Stele', 'live'),
 'siloam_w': ('https://en.wikipedia.org/wiki/Siloam_inscription', 'live'),
 'pilate_w': ('https://en.wikipedia.org/wiki/Pilate_stone', 'live'),
 'textcrit_w': ('https://en.wikipedia.org/wiki/Textual_criticism_of_the_New_Testament', 'live'),
 'ntmss_w': ('https://en.wikipedia.org/wiki/Biblical_manuscript', 'live'),
 'creationism_w': ('https://en.wikipedia.org/wiki/Creationism', 'live'),
 'finetune_w': ('https://en.wikipedia.org/wiki/Fine-tuned_universe', 'live'),
 'sdafb_w': ('https://en.wikipedia.org/wiki/28_Fundamental_Beliefs', 'live'),
 'dunn08': ('https://doi.org/10.1126/science.1150952', 'live'),
 'kahneman10': ('https://doi.org/10.1073/pnas.1011492107', 'live'),
 'killingsworth23': ('https://doi.org/10.1073/pnas.2208661120', 'live'),
 'dittmar14': ('https://doi.org/10.1037/a0037409', 'live'),
 'tithe_w': ('https://en.wikipedia.org/wiki/Tithe', 'live'),
 'orlich13': ('https://doi.org/10.1001/jamainternmed.2013.6473', 'live'),
 'gbd18': ('https://doi.org/10.1016/S0140-6736(18)31310-2', 'live'),
 'doll04': ('https://doi.org/10.1136/bmj.38142.554479.AE', 'live'),
 'ahs_w': ('https://en.wikipedia.org/wiki/Adventist_Health_Studies', 'live'),
 'barnum_w': ('https://en.wikipedia.org/wiki/Barnum_effect', 'live'),
 'robles14': ('https://doi.org/10.1037/a0031859', 'live'),
 'holt10': ('https://doi.org/10.1371/journal.pmed.1000316', 'live'),
 'kg05': ('https://doi.org/10.1001/archpsyc.62.12.1377', 'live'),
 'gershoff16': ('https://doi.org/10.1037/fam0000191', 'live'),
 'larzelere05': ('https://doi.org/10.1007/s10567-005-2340-z', 'live'),
 'parstyle_w': ('https://en.wikipedia.org/wiki/Parenting_styles', 'live'),
 'number_w': ('https://en.wikipedia.org/wiki/Number_of_the_beast', 'live'),
 'vfd_w': ('https://en.wikipedia.org/wiki/Vicarius_Filii_Dei', 'live'),
 'p115_w': ('https://en.wikipedia.org/wiki/Papyrus_115', 'live'),
 'hist_w': ('https://en.wikipedia.org/wiki/Historicism_(Christianity)', 'live'),
 'futur_w': ('https://en.wikipedia.org/wiki/Futurism_(Christianity)', 'live'),
 'pret_w': ('https://en.wikipedia.org/wiki/Preterism', 'live'),
 'dayyear_w': ('https://en.wikipedia.org/wiki/Day-year_principle', 'live'),
 'pius6_w': ('https://en.wikipedia.org/wiki/Pope_Pius_VI', 'live'),
 'sdaesch_w': ('https://en.wikipedia.org/wiki/Seventh-day_Adventist_eschatology', 'live'),
 'antichrist_w': ('https://en.wikipedia.org/wiki/Antichrist', 'live'),
 'wcf_w': ('https://en.wikipedia.org/wiki/Westminster_Confession_of_Faith', 'live'),
 'siege538_w': ('https://en.wikipedia.org/wiki/Siege_of_Rome_(537%E2%80%93538)', 'live'),
 'vandal_w': ('https://en.wikipedia.org/wiki/Vandalic_War', 'live'),
 'odoacer_w': ('https://en.wikipedia.org/wiki/Odoacer', 'live'),
 'irenaeus': ('https://www.newadvent.org/fathers/0103530.htm', 'live'),
 'ccc882': ('https://www.vatican.va/archive/ENG0015/__P2A.HTM', 'live'),
 'ccc1461': ('https://www.scborromeo.org/ccc/para/1461.htm', 'live'),
 'ij_w': ('https://en.wikipedia.org/wiki/Investigative_judgment', 'live'),
 'edson_w': ('https://en.wikipedia.org/wiki/Hiram_Edson', 'live'),
 'millerism_w': ('https://en.wikipedia.org/wiki/Millerism', 'live'),
 'ford_w': ('https://en.wikipedia.org/wiki/Desmond_Ford', 'live'),
 'seventy_w': ('https://en.wikipedia.org/wiki/Prophecy_of_Seventy_Weeks', 'live'),
 'dan8_w': ('https://en.wikipedia.org/wiki/Daniel_8', 'live'),
 'art1_w': ('https://en.wikipedia.org/wiki/Artaxerxes_I', 'live'),
 'antio_w': ('https://en.wikipedia.org/wiki/Antiochus_IV_Epiphanes', 'live'),
 'yk_w': ('https://en.wikipedia.org/wiki/Yom_Kippur', 'live'),
 'unet_w': ('https://en.wikipedia.org/wiki/Unetanneh_Tokef', 'live'),
 'partj_w': ('https://en.wikipedia.org/wiki/Particular_judgment', 'live'),
 'ccc1022': ('https://www.scborromeo.org/ccc/para/1022.htm', 'live'),
 'ccc1038': ('https://www.scborromeo.org/ccc/para/1038.htm', 'live'),
 'mishnah_rh': ('https://www.sefaria.org/Mishnah_Rosh_Hashanah.1.2', 'live'),
 'talmud_rh': ('https://www.sefaria.org/Rosh_Hashanah.16b', 'live'),
 'oldcov_w': ('https://en.wikipedia.org/wiki/Christian_views_on_the_Old_Covenant', 'live'),
 'nct_w': ('https://en.wikipedia.org/wiki/New_Covenant_theology', 'live'),
 'm613_w': ('https://en.wikipedia.org/wiki/613_commandments', 'live'),
 'council_w': ('https://en.wikipedia.org/wiki/Council_of_Jerusalem', 'live'),
 'decree_w': ('https://en.wikipedia.org/wiki/Apostolic_Decree', 'live'),
 'aquinas99': ('https://www.newadvent.org/summa/2099.htm', 'live'),
 'wcf19': ('https://www.opc.org/wcf.html', 'live'),
 'calvin420': ('https://www.ccel.org/ccel/calvin/institutes.vi.xxi.html', 'live'),
 'ccc2072': ('https://www.scborromeo.org/ccc/para/2072.htm', 'live'),
 'thorn_w': ('https://en.wikipedia.org/wiki/Thorn_in_the_flesh', 'live'),
 'lordp_w': ('https://en.wikipedia.org/wiki/Lord%27s_Prayer', 'live'),
 'ipstudy_w': ('https://en.wikipedia.org/wiki/Studies_on_intercessory_prayer', 'live'),
 'aquinas83': ('https://www.newadvent.org/summa/3083.htm', 'live'),
 'ccc2737': ('https://www.scborromeo.org/ccc/para/2737.htm', 'live'),
 'step06': ('https://doi.org/10.1016/j.ahj.2005.05.028', 'live'),
 'cochrane09': ('https://doi.org/10.1002/14651858.CD000368.pub3', 'live'),
 'judas_w': ('https://en.wikipedia.org/wiki/Judas_Iscariot', 'live'),
 'gjudas_w': ('https://en.wikipedia.org/wiki/Gospel_of_Judas', 'live'),
 'silver_w': ('https://en.wikipedia.org/wiki/Thirty_pieces_of_silver', 'live'),
 'sonperd_w': ('https://en.wikipedia.org/wiki/Son_of_perdition', 'live'),
 'judas_ce': ('https://www.newadvent.org/cathen/08539a.htm', 'live'),
 'ancestor_w': ('https://en.wikipedia.org/wiki/Veneration_of_the_dead', 'live'),
 'rites_w': ('https://en.wikipedia.org/wiki/Chinese_Rites_controversy', 'live'),
 'qingming_w': ('https://en.wikipedia.org/wiki/Qingming_Festival', 'live'),
 'astro_w': ('https://en.wikipedia.org/wiki/Astrology_and_science', 'live'),
 'fengshui_w': ('https://en.wikipedia.org/wiki/Feng_shui', 'live'),
 'atone_w': ('https://en.wikipedia.org/wiki/Atonement_in_Christianity', 'live'),
 'cv_w': ('https://en.wikipedia.org/wiki/Christus_Victor', 'live'),
 'satis_w': ('https://en.wikipedia.org/wiki/Satisfaction_theory_of_atonement', 'live'),
 'anselm': ('https://sourcebooks.fordham.edu/basis/anselm-curdeus.asp', 'live'),
 'moral_w': ('https://en.wikipedia.org/wiki/Moral_influence_theory_of_atonement', 'live'),
 'penal_w': ('https://en.wikipedia.org/wiki/Penal_substitution', 'live'),
 'gov_w': ('https://en.wikipedia.org/wiki/Governmental_theory_of_atonement', 'live'),
 'ransom_w': ('https://en.wikipedia.org/wiki/Ransom_theory_of_atonement', 'live'),
 'calvin216': ('https://www.ccel.org/ccel/calvin/institutes.iv.xvii.html', 'live'),
 'ccc613': ('https://www.scborromeo.org/ccc/para/613.htm', 'live'),
 'ccc614': ('https://www.scborromeo.org/ccc/para/614.htm', 'live'),
 'ccc615': ('https://www.scborromeo.org/ccc/para/615.htm', 'live'),
 'ccc616': ('https://www.scborromeo.org/ccc/para/616.htm', 'live'),
 'sdafb_w': ('https://en.wikipedia.org/wiki/28_Fundamental_Beliefs', 'live'),
 'ardn4': ("https://www.sefaria.org/Avot_D'Rabbi_Natan.4", 'live'),
 'yoma8': ('https://www.sefaria.org/Mishnah_Yoma.8', 'live'),
 'chalke_w': ('https://en.wikipedia.org/wiki/Steve_Chalke', 'live'),
 'korban_w': ('https://en.wikipedia.org/wiki/Korban', 'live'),
 'twain_q': ('https://en.wikiquote.org/wiki/Letters_from_the_Earth', 'live'),
 'twain_w': ('https://en.wikipedia.org/wiki/Letters_from_the_Earth', 'live'),
 'wcf32': ('https://www.opc.org/wcf.html', 'live'),
 'mortal_w': ('https://en.wikipedia.org/wiki/Christian_mortalism', 'live'),
 'wright_w': ('https://en.wikipedia.org/wiki/N._T._Wright', 'live'),
 'lewis_mc': ('https://en.wikiquote.org/wiki/Mere_Christianity', 'live'),
 'parad_w': ('https://en.wikipedia.org/wiki/Paradise', 'live'),
 'stadion_w': ('https://en.wikipedia.org/wiki/Stadion_(unit)', 'live'),
 'newjer_w': ('https://en.wikipedia.org/wiki/New_Jerusalem', 'live'),
 'mansion_w': ('https://en.wiktionary.org/wiki/mansio', 'live'),
 'ccc1042': ('https://www.scborromeo.org/ccc/para/1042.htm', 'live'),
 'ccc1045': ('https://www.scborromeo.org/ccc/para/1045.htm', 'live'),
 'iren532': ('https://www.newadvent.org/fathers/0103532.htm', 'live'),
 'aug2230': ('https://www.newadvent.org/fathers/120122.htm', 'live'),
 'chesterton': ('https://www.gutenberg.org/ebooks/130', 'live'),
 'sdafb28': ('https://www.adventist.org/the-new-earth/', 'archive 2024'),
 'brickman': ('https://pubmed.ncbi.nlm.nih.gov/690806/', 'pubmed'),
 'eastwood': ('https://pubmed.ncbi.nlm.nih.gov/26168505/', 'pubmed'),
 'fa_quran': ('https://alquran.cloud/', 'live'),
 'fa_majian': ('https://zh.wikipedia.org/wiki/马坚', 'live'),
 'fa_hadith_gabriel': ('https://github.com/fawazahmed0/hadith-api', 'live'),
 'fa_hadith': ('https://github.com/fawazahmed0/hadith-api', 'live'),
 'fa_islam': ('https://en.wikipedia.org/wiki/Islam', 'live'),
 'fa_muh': ('https://en.wikipedia.org/wiki/Muhammad', 'live'),
 'fa_quranw': ('https://en.wikipedia.org/wiki/Quran', 'live'),
 'fa_iman': ('https://en.wikipedia.org/wiki/Iman_(Islam)', 'live'),
 'fa_tawhid': ('https://en.wikipedia.org/wiki/Tawhid', 'live'),
 'fa_jesusislam': ('https://en.wikipedia.org/wiki/Jesus_in_Islam', 'live'),
 'fa_tahrif': ('https://en.wikipedia.org/wiki/Tahrif', 'live'),
 'fa_islamchina': ('https://en.wikipedia.org/wiki/Islam_in_China', 'live'),
 'fa_pew': ('https://en.wikipedia.org/wiki/Major_religious_groups', 'live'),
 'fa_tacitus': ('https://en.wikipedia.org/wiki/Tacitus_on_Jesus', 'live'),
 'fa_josephus': ('https://en.wikipedia.org/wiki/Josephus_on_Jesus', 'live'),
 'fa_ud64': ('https://suttacentral.net/ud6.4/en/sujato', 'live'),
 'fa_t0210': ('https://cbetaonline.dila.edu.tw/zh/T0210_002', 'live'),
 'fa_t0099': ('https://cbetaonline.dila.edu.tw/zh/T0099_015', 'live'),
 'fa_t0026': ('https://cbetaonline.dila.edu.tw/zh/T0026_060', 'live'),
 'fa_t0001': ('https://cbetaonline.dila.edu.tw/zh/T0001_002', 'live'),
 'fa_t0235': ('https://cbetaonline.dila.edu.tw/zh/T0235_001', 'live'),
 'fa_t0251': ('https://cbetaonline.dila.edu.tw/zh/T0251_001', 'live'),
 'fa_t0360': ('https://cbetaonline.dila.edu.tw/zh/T0360_001', 'live'),
 'fa_buddha': ('https://en.wikipedia.org/wiki/The_Buddha', 'live'),
 'fa_fnt': ('https://en.wikipedia.org/wiki/Four_Noble_Truths', 'live'),
 'fa_marks': ('https://en.wikipedia.org/wiki/Three_marks_of_existence', 'live'),
 'fa_anatta': ('https://en.wikipedia.org/wiki/Anattā', 'live'),
 'fa_nirvana': ('https://en.wikipedia.org/wiki/Nirvana_(Buddhism)', 'live'),
 'fa_karma': ('https://en.wikipedia.org/wiki/Karma_in_Buddhism', 'live'),
 'fa_samsara': ('https://en.wikipedia.org/wiki/Saṃsāra_(Buddhism)', 'live'),
 'fa_arrow': ('https://en.wikipedia.org/wiki/Parable_of_the_Poisoned_Arrow', 'live'),
 'fa_pureland': ('https://en.wikipedia.org/wiki/Pure_Land_Buddhism', 'live'),
 'fa_jodo': ('https://en.wikipedia.org/wiki/Jōdo_Shinshū', 'live'),
 'fa_tanni': ('https://ja.wikipedia.org/wiki/歎異抄', 'live'),
 'fa_bodhi': ('https://en.wikipedia.org/wiki/Bodhisattva', 'live'),
 'fa_hanbud': ('https://zh.wikipedia.org/wiki/汉传佛教', 'live'),
 'fa_baima': ('https://zh.wikipedia.org/wiki/白马寺', 'live'),
 'fa_ddj': ('https://zh.wikisource.org/wiki/道德經_(王弼本)', 'live'),
 'fa_ddjw': ('https://en.wikipedia.org/wiki/Tao_Te_Ching', 'live'),
 'fa_laozi': ('https://en.wikipedia.org/wiki/Laozi', 'live'),
 'fa_zhang': ('https://en.wikipedia.org/wiki/Zhang_Daoling', 'live'),
 'fa_taoism': ('https://en.wikipedia.org/wiki/Taoism', 'live'),
 'fa_elixir': ('https://en.wikipedia.org/wiki/Chinese_alchemical_elixir_poisoning', 'live'),
 'fa_cuv': ('https://en.wikipedia.org/wiki/Chinese_Union_Version', 'live'),
 'fa_lewis': ('https://en.wikiquote.org/wiki/Mere_Christianity', 'live'),
 'fa_hound': ('https://en.wikisource.org/wiki/The_Hound_of_Heaven', 'live'),
 'fa_hound_w': ('https://en.wikipedia.org/wiki/The_Hound_of_Heaven', 'live'),
 'un_radbod': ('https://en.wikipedia.org/wiki/Redbad,_King_of_the_Frisians', 'live'),
 'un_xavier': ('https://sourcebooks.fordham.edu/mod/1552xavier4.asp', 'live'),
 'un_xavier_w': ('https://en.wikipedia.org/wiki/Francis_Xavier', 'live'),
 'un_harrow': ('https://en.wikipedia.org/wiki/Harrowing_of_Hell', 'live'),
 'un_bftd': ('https://en.wikipedia.org/wiki/Baptism_for_the_dead', 'live'),
 'un_extra': ('https://en.wikipedia.org/wiki/Extra_Ecclesiam_nulla_salus', 'live'),
 'un_wcf10': ('https://www.opc.org/wcf.html', 'live'),
 'un_lg16': ('https://www.vatican.va/archive/hist_councils/ii_vatican_council/documents/vat-ii_const_19641121_lumen-gentium_en.html', 'live'),
 'un_ccc847': ('https://www.scborromeo.org/ccc/para/847.htm', 'live'),
 'un_ccc848': ('https://www.scborromeo.org/ccc/para/848.htm', 'live'),
 'un_ccc1261': ('https://www.scborromeo.org/ccc/para/1261.htm', 'live'),
 'un_wesley': ('https://wesley.nnu.edu/john-wesley/the-sermons-of-john-wesley-1872-edition/sermon-106-on-faith/', 'live'),
 'un_anon': ('https://en.wikipedia.org/wiki/Anonymous_Christian', 'live'),
 'un_univ': ('https://en.wikipedia.org/wiki/Universal_reconciliation', 'live'),
 'un_justin': ('https://www.newadvent.org/fathers/0126.htm', 'live'),
 'un_limbo': ('https://en.wikipedia.org/wiki/Limbo', 'live'),
 'un_dante': ('https://it.wikisource.org/wiki/Divina_Commedia/Inferno/Canto_IV', 'live'),
 'un_lewis_lb': ('https://en.wikiquote.org/wiki/The_Last_Battle', 'live'),
 'un_shangdi': ('https://en.wikipedia.org/wiki/Shangdi', 'live'),
 'un_huangyi': ('https://zh.wikisource.org/wiki/詩經/皇矣', 'live'),
 'un_daming': ('https://zh.wikisource.org/wiki/詩經/大明', 'live'),
 'un_shundian': ('https://zh.wikisource.org/wiki/尚書/舜典', 'live'),
 'un_budeyi': ('https://zh.wikisource.org/wiki/不得已/上卷', 'live'),
 'un_legge': ('https://en.wikipedia.org/wiki/James_Legge', 'live'),
 'un_sinim': ('https://en.wikipedia.org/wiki/Sinim', 'live'),
 'un_stele': ('https://zh.wikipedia.org/wiki/大秦景教流行中國碑', 'live'),
 'un_ricci': ('https://en.wikipedia.org/wiki/Matteo_Ricci', 'live'),
 'un_lunyu': ('https://zh.wikisource.org/wiki/論語/先進第十一', 'live'),
 'un_aug': ('https://www.newadvent.org/fathers/110103.htm', 'live'),
 'un_whittier': ('https://en.wikisource.org/wiki/The_Complete_Poetical_Works_of_John_Greenleaf_Whittier/The_Eternal_Goodness', 'live'),
 'un_faber': ('https://en.wikisource.org/wiki/The_Army_and_Navy_Hymnal/Hymns/There%27s_a_Wideness_in_God%27s_Mercy', 'live'),
 'dm_wang21': ('https://doi.org/10.1001/jama.2021.22208', 'live'),   # PubMed 核对摘要（2026-10-26）
 'dm_li20': ('https://doi.org/10.1136/bmj.m997', 'live'),   # PubMed 核对摘要（2026-10-26）
 'dm_ada24dx': ('https://doi.org/10.2337/dc24-S002', 'live'),   # PubMed 核对摘要（2026-10-26）
 'dm_ada24old': ('https://doi.org/10.2337/dc24-S013', 'live'),   # PubMed 核对摘要（2026-10-26）
 'dm_defronzo09': ('https://doi.org/10.2337/dc09-S302', 'live'),   # PubMed 核对摘要（2026-10-26）
 'dm_ukpds16': ('https://pubmed.ncbi.nlm.nih.gov/7589820/', 'live'),   # PubMed 核对摘要（2026-10-26）
 'dm_petersen03': ('https://doi.org/10.1126/science.1082889', 'live'),   # PubMed 核对摘要（2026-10-26）
 'dm_srikanthan10': ('https://doi.org/10.1371/journal.pone.0010805', 'live'),   # PubMed 核对摘要（2026-10-26）
 'dm_taylor08': ('https://doi.org/10.1007/s00125-008-1116-7', 'live'),   # PubMed 核对摘要（2026-10-26）
 'dm_pft15': ('https://doi.org/10.1042/CS20140553', 'live'),   # PubMed 核对摘要（2026-10-26）
 'dm_ma13': ('https://doi.org/10.1111/nyas.12098', 'live'),   # PubMed 核对摘要（2026-10-26）
 'dm_yoon06': ('https://doi.org/10.1016/S0140-6736(06)69703-1', 'live'),   # PubMed 核对摘要（2026-10-26）
 'dm_chang03': ('https://doi.org/10.1152/ajpendo.00366.2002', 'live'),   # PubMed 核对摘要（2026-10-26）
 'dm_butler03': ('https://doi.org/10.2337/diabetes.52.1.102', 'live'),   # PubMed 核对摘要（2026-10-26）
 'dm_spiegel99': ('https://doi.org/10.1016/S0140-6736(99)01376-8', 'live'),   # PubMed 核对摘要（2026-10-26）
 'dm_shan15': ('https://doi.org/10.2337/dc14-2073', 'live'),   # PubMed 核对摘要（2026-10-26）
 'dm_hall19': ('https://doi.org/10.1016/j.cmet.2019.05.008', 'live'),   # PubMed 核对摘要（2026-10-26）
 'dm_malik10': ('https://doi.org/10.2337/dc10-1079', 'live'),   # PubMed 核对摘要（2026-10-26）
 'dm_hu12': ('https://doi.org/10.1136/bmj.e1454', 'live'),   # PubMed 核对摘要（2026-10-26）
 'dm_pan15': ('https://doi.org/10.1016/S2213-8587(15)00316-2', 'live'),   # PubMed 核对摘要（2026-10-26）
 'dm_ravelli98': ('https://doi.org/10.1016/s0140-6736(97)07244-9', 'live'),   # PubMed 核对摘要（2026-10-26）
 'dm_neel62': ('https://pubmed.ncbi.nlm.nih.gov/13937884/', 'live'),   # PubMed 核对摘要（2026-10-26）
 'dm_ukpds80': ('https://doi.org/10.1056/NEJMoa0806470', 'live'),   # PubMed 核对摘要（2026-10-26）
 'dm_empa15': ('https://doi.org/10.1056/NEJMoa1504720', 'live'),   # PubMed 核对摘要（2026-10-26）
 'dm_leader16': ('https://doi.org/10.1056/NEJMoa1603827', 'live'),   # PubMed 核对摘要（2026-10-26）
 'dm_dejager10': ('https://doi.org/10.1136/bmj.c2181', 'live'),   # PubMed 核对摘要（2026-10-26）
 'dm_chalmers09': ('https://doi.org/10.1016/S0140-6736(09)60329-9', 'live'),   # PubMed 核对摘要（2026-10-26）
 'dm_riddle21': ('https://doi.org/10.2337/dci21-0034', 'live'),   # PubMed 核对摘要（2026-10-26）
 'dm_direct18': ('https://doi.org/10.1016/S0140-6736(17)33102-1', 'live'),   # PubMed 核对摘要（2026-10-26）
 'dm_direct19': ('https://doi.org/10.1016/S2213-8587(19)30068-3', 'live'),   # PubMed 核对摘要（2026-10-26）
 'dm_direct24': ('https://doi.org/10.1016/S2213-8587(23)00385-6', 'live'),   # PubMed 核对摘要（2026-10-26）
 'dm_taylor18': ('https://doi.org/10.1016/j.cmet.2018.07.003', 'live'),   # PubMed 核对摘要（2026-10-26）
 'dm_gregg12': ('https://doi.org/10.1001/jama.2012.67929', 'live'),   # PubMed 核对摘要（2026-10-26）
 'dm_tianqi14': ('https://doi.org/10.1210/jc.2013-3276', 'live'),   # PubMed 核对摘要（2026-10-26）
 'dm_ching12': ('https://doi.org/10.1111/j.1365-2125.2011.04135.x', 'live'),   # PubMed 核对摘要（2026-10-26）
 'dm_daqing97': ('https://doi.org/10.2337/diacare.20.4.537', 'live'),   # PubMed 核对摘要（2026-10-26）
 'dm_daqing19': ('https://doi.org/10.1016/S2213-8587(19)30093-2', 'live'),   # PubMed 核对摘要（2026-10-26）
 'dm_dpp02': ('https://doi.org/10.1056/NEJMoa012512', 'live'),   # PubMed 核对摘要（2026-10-26）
 'dm_dppos15': ('https://doi.org/10.1016/S2213-8587(15)00291-0', 'live'),   # PubMed 核对摘要（2026-10-26）
 'dm_dps01': ('https://doi.org/10.1056/NEJM200105033441801', 'live'),   # PubMed 核对摘要（2026-10-26）
 'dm_satija16': ('https://doi.org/10.1371/journal.pmed.1002039', 'live'),   # PubMed 核对摘要（2026-10-26）
 'dm_tonstad09': ('https://doi.org/10.2337/dc08-1886', 'live'),   # PubMed 核对摘要（2026-10-26）
 'dm_reynolds16': ('https://doi.org/10.1007/s00125-016-4085-2', 'live'),   # PubMed 核对摘要（2026-10-26）
 'dm_colberg16': ('https://doi.org/10.2337/dc16-1728', 'live'),   # PubMed 核对摘要（2026-10-26）
 'ht_wang18': ('https://doi.org/10.1161/CIRCULATIONAHA.117.032380', 'live'),   # PubMed 核对摘要（2026-10-26）
 'ht_lu17': ('https://doi.org/10.1016/S0140-6736(17)32478-9', 'live'),   # PubMed 核对摘要（2026-10-26）
 'ht_lewington02': ('https://doi.org/10.1016/s0140-6736(02)11911-8', 'live'),   # PubMed 核对摘要（2026-10-26）
 'ht_hall12': ('https://doi.org/10.1002/cphy.c110058', 'live'),   # PubMed 核对摘要（2026-10-26）
 'ht_franklin97': ('https://doi.org/10.1161/01.cir.96.1.308', 'live'),   # PubMed 核对摘要（2026-10-26）
 'ht_vasan02': ('https://doi.org/10.1001/jama.287.8.1003', 'live'),   # PubMed 核对摘要（2026-10-26）
 'ht_gurven12': ('https://doi.org/10.1161/HYPERTENSIONAHA.111.189100', 'live'),   # PubMed 核对摘要（2026-10-26）
 'ht_intersalt': ('https://doi.org/10.1136/bmj.297.6644.319', 'live'),   # PubMed 核对摘要（2026-10-26）
 'ht_zhang20': ('https://doi.org/10.2196/15933', 'live'),   # PubMed 核对摘要（2026-10-26）
 'ht_he22': ('https://doi.org/10.1136/bmj-2021-066982', 'live'),   # PubMed 核对摘要（2026-10-26）
 'ht_tan19': ('https://doi.org/10.1136/bmjopen-2018-025623', 'live'),   # PubMed 核对摘要（2026-10-26）
 'ht_he13': ('https://doi.org/10.1136/bmj.f1325', 'live'),   # PubMed 核对摘要（2026-10-26）
 'ht_he20': ('https://doi.org/10.1016/j.jacc.2019.11.055', 'live'),   # PubMed 核对摘要（2026-10-26）
 'ht_neter03': ('https://doi.org/10.1161/01.HYP.0000094221.86888.AE', 'live'),   # PubMed 核对摘要（2026-10-26）
 'ht_roerecke17': ('https://doi.org/10.1016/S2468-2667(17)30003-8', 'live'),   # PubMed 核对摘要（2026-10-26）
 'ht_peppard00': ('https://doi.org/10.1056/NEJM200005113421901', 'live'),   # PubMed 核对摘要（2026-10-26）
 'ht_brook13': ('https://doi.org/10.1161/HYP.0b013e318293645f', 'live'),   # PubMed 核对摘要（2026-10-26）
 'ht_brown20': ('https://doi.org/10.7326/M20-0065', 'live'),   # PubMed 核对摘要（2026-10-26）
 'ht_xu20': ('https://doi.org/10.1016/j.jacc.2020.02.052', 'live'),   # PubMed 核对摘要（2026-10-26）
 'ht_ettehad16': ('https://doi.org/10.1016/S0140-6736(15)01225-8', 'live'),   # PubMed 核对摘要（2026-10-26）
 'ht_bplttc21': ('https://doi.org/10.1016/S0140-6736(21)00590-0', 'live'),   # PubMed 核对摘要（2026-10-26）
 'ht_beckett08': ('https://doi.org/10.1056/NEJMoa0801369', 'live'),   # PubMed 核对摘要（2026-10-26）
 'ht_zhang21': ('https://doi.org/10.1056/NEJMoa2111437', 'live'),   # PubMed 核对摘要（2026-10-26）
 'ht_sprint15': ('https://doi.org/10.1056/NEJMoa1511939', 'live'),   # PubMed 核对摘要（2026-10-26）
 'ht_liu25': ('https://doi.org/10.1038/s41440-024-02070-2', 'live'),   # PubMed 核对摘要（2026-10-26）
 'ht_sheppard20': ('https://doi.org/10.1001/jama.2020.4871', 'live'),   # PubMed 核对摘要（2026-10-26）
 'ht_qiao22': ('https://doi.org/10.19540/j.cnki.cjcmm.202206024.501', 'live'),   # PubMed 核对摘要（2026-10-26）
 'ht_meng22': ('https://doi.org/10.1016/j.phymed.2022.154459', 'live'),   # PubMed 核对摘要（2026-10-26）
 'ht_fan21': ('https://doi.org/10.19540/j.cnki.cjcmm.20200712.501', 'live'),   # PubMed 核对摘要（2026-10-26）
 'ht_appel97': ('https://doi.org/10.1056/NEJM199704173361601', 'live'),   # PubMed 核对摘要（2026-10-26）
 'ht_sacks01': ('https://doi.org/10.1056/NEJM200101043440101', 'live'),   # PubMed 核对摘要（2026-10-26）
 'ht_aburto13': ('https://doi.org/10.1136/bmj.f1378', 'live'),   # PubMed 核对摘要（2026-10-26）
 'ht_cornelissen13': ('https://doi.org/10.1161/JAHA.112.004473', 'live'),   # PubMed 核对摘要（2026-10-26）
 'ht_edwards23': ('https://doi.org/10.1136/bjsports-2022-106503', 'live'),   # PubMed 核对摘要（2026-10-26）
 'ht_neal21': ('https://doi.org/10.1056/NEJMoa2105675', 'live'),   # PubMed 核对摘要（2026-10-26）
 'ht_whelton98': ('https://doi.org/10.1001/jama.279.11.839', 'live'),   # PubMed 核对摘要（2026-10-26）
 'ht_pettersen12': ('https://doi.org/10.1017/S1368980011003454', 'live'),   # PubMed 核对摘要（2026-10-26）
 'ht_yokoyama14': ('https://doi.org/10.1001/jamainternmed.2013.14547', 'live'),   # PubMed 核对摘要（2026-10-26）
 'ht_buettner25': ('https://doi.org/10.1177/15598276251334310', 'live'),   # PubMed 核对摘要（2026-10-26）
 'ht_candal25': ('https://doi.org/10.14336/AD.2025.0461', 'live'),   # PubMed 核对摘要（2026-10-26）
 'lp_lu21': ('https://doi.org/10.1001/jamanetworkopen.2021.27573', 'live'),   # PubMed 核对摘要（2026-10-27）
 'lp_lu17ms': ('https://doi.org/10.1210/jc.2016-2477', 'live'),   # PubMed 核对摘要（2026-10-27）
 'lp_li23': ('https://doi.org/10.26599/1671-5411.2023.09.008', 'live'),   # PubMed 核对摘要（2026-10-27）
 'lp_ference17': ('https://doi.org/10.1093/eurheartj/ehx144', 'live'),   # PubMed 核对摘要（2026-10-27）
 'lp_hu20fh': ('https://doi.org/10.1161/CIRCULATIONAHA.119.044795', 'live'),   # PubMed 核对摘要（2026-10-27）
 'lp_berenson98': ('https://doi.org/10.1056/NEJM199806043382302', 'live'),   # PubMed 核对摘要（2026-10-27）
 'lp_cohen06': ('https://doi.org/10.1056/NEJMoa054013', 'live'),   # PubMed 核对摘要（2026-10-27）
 'lp_ference12': ('https://doi.org/10.1016/j.jacc.2012.09.017', 'live'),   # PubMed 核对摘要（2026-10-27）
 'lp_adiels06': ('https://doi.org/10.1007/s00125-005-0125-z', 'live'),   # PubMed 核对摘要（2026-10-27）
 'lp_alberti09': ('https://doi.org/10.1161/CIRCULATIONAHA.109.192644', 'live'),   # PubMed 核对摘要（2026-10-27）
 'lp_kodama07': ('https://doi.org/10.1001/archinte.167.10.999', 'live'),   # PubMed 核对摘要（2026-10-27）
 'lp_reaven88': ('https://doi.org/10.2337/diab.37.12.1595', 'live'),   # PubMed 核对摘要（2026-10-27）
 'lp_petersen18': ('https://doi.org/10.1152/physrev.00063.2017', 'live'),   # PubMed 核对摘要（2026-10-27）
 'lp_hall15': ('https://doi.org/10.1161/CIRCRESAHA.116.305697', 'live'),   # PubMed 核对摘要（2026-10-27）
 'lp_zhou20': ('https://doi.org/10.1002/hep.31150', 'live'),   # PubMed 核对摘要（2026-10-27）
 'lp_kaplan17': ('https://doi.org/10.1016/S0140-6736(17)30752-3', 'live'),   # PubMed 核对摘要（2026-10-27）
 'lp_ctt10': ('https://doi.org/10.1016/S0140-6736(10)61350-5', 'live'),   # PubMed 核对摘要（2026-10-27）
 'lp_ctt19old': ('https://doi.org/10.1016/S0140-6736(18)31942-1', 'live'),   # PubMed 核对摘要（2026-10-27）
 'lp_ctt22': ('https://doi.org/10.1016/S0140-6736(22)01545-8', 'live'),   # PubMed 核对摘要（2026-10-27）
 'lp_sattar10': ('https://doi.org/10.1016/S0140-6736(09)61965-6', 'live'),   # PubMed 核对摘要（2026-10-27）
 'lp_lu08': ('https://doi.org/10.1016/j.amjcard.2008.02.056', 'live'),   # PubMed 核对摘要（2026-10-27）
 'lp_gordon10': ('https://doi.org/10.1001/archinternmed.2010.382', 'live'),   # PubMed 核对摘要（2026-10-27）
 'lp_abdelhamid20': ('https://doi.org/10.1002/14651858.CD003177.pub5', 'live'),   # PubMed 核对摘要（2026-10-27）
 'lp_sacks17': ('https://doi.org/10.1161/CIR.0000000000000510', 'live'),   # PubMed 核对摘要（2026-10-27）
 'lp_carson20': ('https://doi.org/10.1161/CIR.0000000000000743', 'live'),   # PubMed 核对摘要（2026-10-27）
 'lp_zhong19': ('https://doi.org/10.1001/jama.2019.1572', 'live'),   # PubMed 核对摘要（2026-10-27）
 'lp_qin18': ('https://doi.org/10.1136/heartjnl-2017-312651', 'live'),   # PubMed 核对摘要（2026-10-27）
 'lp_jenkins03': ('https://doi.org/10.1001/jama.290.4.502', 'live'),   # PubMed 核对摘要（2026-10-27）
 'lp_orchard05': ('https://doi.org/10.7326/0003-4819-142-8-200504190-00009', 'live'),   # PubMed 核对摘要（2026-10-27）
 'lp_wang15veg': ('https://doi.org/10.1161/JAHA.115.002408', 'live'),   # PubMed 核对摘要（2026-10-27）
 'lp_orlich13': ('https://doi.org/10.1001/jamainternmed.2013.6473', 'live'),   # PubMed 核对摘要（2026-10-27）
 'lp_ericsson91': ('https://doi.org/10.1172/JCI115034', 'live'),   # PubMed 核对摘要（2026-10-27）
 'lp_matthews09': ('https://doi.org/10.1016/j.jacc.2009.10.009', 'live'),   # PubMed 核对摘要（2026-10-27）
 'lp_ncdrisc20': ('https://doi.org/10.1038/s41586-020-2338-1', 'live'),   # PubMed 核对摘要（2026-10-27）
 'lp_kronenberg22': ('https://doi.org/10.1093/eurheartj/ehac361', 'live'),   # PubMed 核对摘要（2026-10-27）
 'lp_cannon15': ('https://doi.org/10.1056/NEJMoa1410489', 'live'),   # PubMed 核对摘要（2026-10-27）
 'lp_sabatine17': ('https://doi.org/10.1056/NEJMoa1615664', 'live'),   # PubMed 核对摘要（2026-10-27）
 'lp_bhatt19': ('https://doi.org/10.1056/NEJMoa1812792', 'live'),   # PubMed 核对摘要（2026-10-27）
 'lp_nicholls20': ('https://doi.org/10.1001/jama.2020.22258', 'live'),   # PubMed 核对摘要（2026-10-27）
 'lp_4s94': ('https://pubmed.ncbi.nlm.nih.gov/7968073/', 'live'),   # PubMed 核对摘要（2026-10-27）
 'lp_endo10': ('https://doi.org/10.2183/pjab.86.484', 'live'),   # PubMed 核对摘要（2026-10-27）
 'lp_nissen06': ('https://doi.org/10.1001/jama.295.13.jpc60002', 'live'),   # PubMed 核对摘要（2026-10-27）
 'lp_ornish98': ('https://doi.org/10.1001/jama.280.23.2001', 'live'),   # PubMed 核对摘要（2026-10-27）
 'lp_vodnala12': ('https://doi.org/10.1016/j.amjcard.2012.04.062', 'live'),   # PubMed 核对摘要（2026-10-27）
 'lp_accord10': ('https://doi.org/10.1056/NEJMoa1001282', 'live'),   # PubMed 核对摘要（2026-10-27）
 'lp_prominent22': ('https://doi.org/10.1056/NEJMoa2210645', 'live'),   # PubMed 核对摘要（2026-10-27）
 'lp_whitehead14': ('https://doi.org/10.3945/ajcn.114.086108', 'live'),   # PubMed 核对摘要（2026-10-27）
 'lp_lai23': ('https://doi.org/10.1007/s10620-023-08172-0', 'live'),   # PubMed 核对摘要（2026-10-27）
 'ht_cao25': ('https://doi.org/10.1016/j.medj.2025.100808', 'live'),   # PubMed 核对摘要（2026-10-27，更新为最新全国数据）
 'ht_zhang23': ('https://doi.org/10.1136/bmj-2022-071952', 'live'),   # PubMed 核对摘要（2026-10-27，更新为最新全国数据）
 'dm_zhou25': ('https://doi.org/10.1186/s40779-025-00615-1', 'live'),   # PubMed 核对摘要（2026-10-27，更新为最新全国数据）
 'lp_peng23': ('https://doi.org/10.1016/j.lanwpc.2023.100809', 'live'),   # PubMed 核对摘要（2026-10-27，更新为最新全国数据）
 'lp_huang22': ('https://doi.org/10.1186/s12889-022-14263-w', 'live'),   # PubMed 核对摘要（2026-10-27，更新为最新全国数据）
}
