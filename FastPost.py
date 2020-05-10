# -*- coding: utf-8 -*-

import json
import time

Prefix = '!!fp'
OrderJsonFile = './plugins/MsgOrders.json'
saveDelay = 1
orders = {
	'players': [],
	'ids': [0]
}
helpmsg = '''---------FastPost ---------
一个支持游戏内给其他玩家发送邮件的插件
§a【格式说明】§r
!!fp -获取帮助信息
!!fp send <player> <message> -给指定玩家发送邮件
!!fp check -检查自己的收件箱
!!fp clean -清理自己的收件箱
-----------------------'''.format(Prefix)

def postMsg(server, info):
	sender = info.player
	receiver = info.content.split()[2]
	msg = info.content.split()[3]
	if checkPlayer(receiver):
		server.tell(sender, '[FastPost] 成功发送邮件: ' + msg)
	else:
		server.tell(sender, '[FastPost] 无法找到玩家' + receiver + '在服务器里,可能该玩家还没有登入过!')
	postId = getNextId()
	orders[postId] = {
		'sender': sender,
		'receiver': receiver,
		'msg': msg
	}
	regularSaveOrderJson()

def checkPlayer(player):
	for id in orders['players']:
		if id == player:
			return True
	return False

def checkMsg(server, info): # TODO
	listmsg = ''
	for orderid in orders['ids']:
		order = orders.get(str(orderid))
		if not order:
			continue
		if order.get('receiver') == info.player:
			listmsg = listmsg + '[' + str(orderid) + ']' + order.get('sender') + ': ' + order.get('msg') + '\n'
	if listmsg == '':
		server.tell(info.player,'[FastPost] 空空如也，你没有收到的邮件')
		return
	listmsg = '''==========================================
{0}输入 >!!fp clean< 以清理您的收件箱.
==========================================='''.format(listmsg)
	server.tell(info.player, listmsg)

def cleanMsg(server, info):
	for orderid in orders['ids']:
		order = orders.get(str(orderid))
		if not order:
			continue
		if order.get('receiver') == info.player:
			delOrder(server, orderid)
	regularSaveOrderJson()

def delOrder(server, id):
    global orders
    try:
        orders.pop(id)
        orders['ids'].remove(int(id))
    except Exception:
        server.say('[FastPost] 在试图执行命令时出现错误.')
        return False

def isNewMessages(player): ## TODO
	for orderid in orders['ids']:
		try:
			order = orders[str(orderid)]
		except:
			continue
		if order.get('receiver') == player:
			return True
	return False

def getNextId():
    nextid = 1
    orders['ids'].sort()
    for i, id in enumerate(orders['ids']):
        if i != id:
            nextid = i
            orders['ids'].append(nextid)
            return str(nextid)
    nextid = len(orders['ids'])
    orders['ids'].append(nextid)
    return str(nextid)

def on_info(server, info): # 接收输入
	if info.is_user:
		if info.content == Prefix:
			server.reply(info, helpmsg)
		elif info.content.startswith(Prefix + ' send '):
			postMsg(server, info)
		elif info.content == Prefix + ' check':
			checkMsg(server, info)
		elif info.content == Prefix + ' clean':
			cleanMsg(server, info)

def on_load(server, old_module): # 初始化
	loadOrdersJson()
	server.add_help_message(Prefix, "一个支持游戏里发邮件的MCDR插件")

def on_server_startup(server): # 初始化
	loadOrdersJson()

def regularSaveOrderJson(): # Auto Save
	if len(orders['ids']) % saveDelay == 0:
		saveOrdersJson()

def loadOrdersJson():
	global orders
	try:
		with open(OrderJsonFile) as f:
			orders = json.load(f, encoding='utf8')
	except:
		return

def saveOrdersJson():
	global orders
	try:
		with open(OrderJsonFile, 'w') as f:
			json.dump(orders, f, indent=4)
		server.logger.info("[FastPost] 已保存发件文件.")
	except:
		return

def on_player_joined(server, player):
	global orders
	if checkPlayer(player):
		if isNewMessages(player):
			time.sleep(3)   # 延迟 3s 后再提示，防止更多进服消息混杂而看不到提示
			server.tell(player, "[FastPost] 你有新的邮件，请及时处理. 输入 >!!fp check< 以查看你的收件箱.")
	else:
		orders['players'].append(player)
		server.logger.info('[FastPost] 已添加玩家 ' + player + ' 至玩家列表.')
		saveOrdersJson()