import os
import MySQLdb
import itchat
import threading
from threading import *
import time
import jieba
from config import databases


base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
jieba.load_userdict(base_dir+'/dict.txt')


class WeChat(Thread):
    def __init__(self):
        super().__init__()
        self.db = databases()
        self.cursor = databases().cursor()
        self.EXPR_DONT_UNDERSTAND = '未匹配到关键词'
        self.supplement = "\n\n更多解决方案可以输入下列关键词:电话问题,电脑问题,网络问题来获取更多帮助!\n您也可以直接美式扫工位二维码或online在线提单来快速联系IT!"

    def database_search(self, msg):
        text = ''
        if msg in ('电话问题', '电脑问题', '网络问题'):
            table = '58_robot_1'
            self.cursor.execute('select * from {} where keyword LIKE "{}";'.format(table, msg))
            a = self.cursor.fetchall()
            if a != ():
                text = a[0][2]
            return text
        elif 'add-' in msg:
            key = msg.split('-')[1]
            if key != '':
                with open(base_dir + '/dict.txt', 'a') as k:
                    k.write(key + ' ' + '10' + '\n')
                jieba.add_word(key)
                text = '关键词已经激活'
                return text
            else:
                text = '请按照此格式激活:add-关键词'
                return text
        elif 'del-' in msg:
            dict_txt = []
            key = msg.split('-')[1]
            if key != '':
                fp = open(base_dir + '/dict.txt', 'r')
                txt = fp.readlines()
                for i in txt:
                    if key in i:
                        jieba.del_word(key)
                    else:
                        dict_txt.append(i)
                fp.close()

                with open(base_dir + '/dict.txt', 'w+') as fp:
                    for i in dict_txt:
                        fp.write(i)
                text = '关键词已经删除'
                return text
            else:
                text = '请按照此格式删除:del-关键词'
                return text
        else:
            dict_list = []
            table = '58_robot_2'
            des = self.supplement
            print(jieba.lcut(msg, cut_all=False, HMM=False))
            for x in jieba.cut(msg, cut_all=False, HMM=False):
                dict_list.append(x)
            num_list = [len(o) for o in dict_list]
            if max(num_list, default=0) in [0, 1]:
                a = None
            else:
                seg = dict_list[num_list.index(max(num_list))]
                self.cursor.execute('select * from {} where keyword LIKE "{}";'.format(table, seg))
                a = self.cursor.fetchall()
            if a != ():
                text = a[0][2] + des
            else:
                text = self.EXPR_DONT_UNDERSTAND
            return text

    def run(self):
        @newInstance.msg_register('Text')
        def reply(msg):
            text = msg.text.replace(' ', '')
            # print(msg)
            info = self.database_search(text)
            # print('From:',text,'\n'+'To:',info)
            # with open('wechat_msg_log1.txt','a') as wc:
            #     wc.write('{}{}{}'.format(msg_time+'\n','From:'+text,'\n'+'To:'+info+'\n'))
            # user = msg['User']
            # print(msg)
            # print('%s %s'%(user['UserName'],msg.text))
            # text = msg.text
            # info = get_reponse(text)
            # 不回复自己的消息
            # myusername = newinstance.get_friends(update=True)[0]["UserName"]
            # if not msg['FromUserName'] == myusername and info != EXPR_DONT_UNDERSTAND:
            #     itchat.send(info, msg['FromUserName'])
            # else:
            #     pass

            if info != self.EXPR_DONT_UNDERSTAND:
                msg_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                try:
                    self.cursor.execute(
                        'insert into 58_robot_3 (im, time, question, answer) values ("Wechat", "{}", "{}", "{}")'
                        .format(msg_time, text, info))
                    self.db.commit()
                except:
                    self.db.rollback()
                newInstance.send(info, msg['FromUserName'])

        @newInstance.msg_register('Text', isGroupChat=True)
        def group_reply(msg):
            text = msg.text
            info = self.database_search(text)
            print('From:', text, '\n' + 'To:', info)
            # with open('wechat_msg_group_log1.txt', 'a') as wc:
            #     wc.write('{}{}{}'.format(msg_time + '\n', 'From:' + text, '\n' + 'To:' + info + '\n'))
            # print(msg['User']['UserName'])
            #print(text)

            # 不回复自己的消息

            # myusername = newinstance.get_friends(update=True)[0]["UserName"]
            # if not msg['User']['UserName'] == myusername and info != EXPR_DONT_UNDERSTAND:
            #     itchat.send(info, msg['User']['UserName'])
            if info != self.EXPR_DONT_UNDERSTAND:
                msg_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                try:
                    self.cursor.execute(
                        'insert into 58_robot_3 (im, time, question, answer) values ("Wechat", "{}", "{}", "{}")'
                        .format(msg_time, text, info))
                    self.db.commit()
                except:
                    self.db.rollback()
                newInstance.send(info, msg['User']['UserName'])


def main():
    t1 = WeChat()
    t2 = WeChat()
    t3 = WeChat()
    t4 = WeChat()
    t5 = WeChat()
    t6 = WeChat()
    t7 = WeChat()
    t8 = WeChat()
    for t in [t1, t2, t3, t4, t5, t6, t7, t8]:
        t.start()
        t.join()


if __name__ == '__main__':
    pkl_dir = os.path.dirname(os.path.abspath(__file__))
    name, py = os.path.basename(__file__).split('.')
    newInstance = itchat.new_instance()
    newInstance.auto_login(hotReload=True, statusStorageDir='%s/pkls/%s.pkl' % (pkl_dir, name))
    main()
    newInstance.run()
