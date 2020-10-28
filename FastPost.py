# -*- coding: utf-8 -*-

import json
import time
import traceback
from utils.rtext import *

Prefix = '.fp'
Version = 'v1.1.1'
OrderJsonFile = './plugins/FastPostOrders.json'
orders = {
	'players': ['[Server]'],
	'ids': [0]
}
helpmsg = '''---- §eMCDR FastPost {1}§r ----
给其他玩家发送在线或离线邮件.
§a【格式说明】§r
{0} send <player> <message> - §e给指定玩家发送邮件
{0} check - §e检查自己的收件箱
{0} clean - §e清理自己的收件箱
{0} clean [id] - §e删除序号为[id]的邮件
-----------------------
§7由BCP TECH强力驱动.
§7Powered by BCP Tech.'''.format(Prefix, Version)
#改了一下细节。 ——HackerRouter In 2020.10.28

def loadOrdersJson():
	global orders
	try:
		with open(OrderJsonFile) as f:
			orders = json.load(f, encoding='utf8')
	except:
		return

def on_load(server, old_module):
	loadOrdersJson()
	server.add_help_message(Prefix, "给其他玩家发送在线或离线邮件.")

def on_server_startup(server):
	loadOrdersJson()

def on_player_joined(server, player):
	global orders
	if checkPlayer(player):
		for orderid in orders['ids']:
			try:
				order = orders[str(orderid)]
			except:
				continue
			if order.get('receiver') == player:
				time.sleep(3) # 延迟 3s 后再提示，防止更多进服消息混杂而看不到提示
				server.tell(
					player,
					'§e[FastPost] 你有新的邮件，' +
					RText('§a点击此处查收')
						.h('对应指令: §7' + Prefix + ' check')
						.c(RAction.run_command, f'{Prefix} check')
					+ '§e.'
				)
			return True
	else:
		orders['players'].append(player)
		server.logger.info('§e[FastPost] 已添加玩家 ' + player + ' 至玩家列表.')
		saveOrdersJson()

def on_info(server, info):
	if info.is_user and info.content.startswith(Prefix):
		if info.content == Prefix:
			server.reply(info, helpmsg)
		elif info.content.startswith(Prefix + ' send '):
			postMsg(server, info)
		elif info.content.startswith(Prefix + ' check'):
			checkMsg(server, info)
		elif info.content == Prefix + ' clean':
			cleanMsg(server, info)
		elif info.content.startswith(Prefix + ' clean '):
			cleanSpecifiedMsg(server, info)
		else:
			server.reply(info, '§e[FastPost] §4输入格式不正确.')

def postMsg(server, info):
	if info.is_player:
		sender = info.player
	else:
		sender = '[Server]'
	msg = ''
	if len(info.content.split()) < 4:
		server.reply(info, '§e[FastPost] §4输入格式不正确. 指令格式: §7' + Prefix + ' send <player> <message>')
		return
	receiver = info.content.split()[2]
	for i in range(3, len(info.content.split())):
		msg += info.content.split()[i] + ' '
	if checkPlayer(receiver):
		postId = getNextId()
		orders[postId] = {
			'sender': sender,
			'receiver': receiver,
			'msg': msg,
			'time': time.strftime("%Y-%m-%d %X", time.localtime())
		}
		saveOrdersJson()
		server.reply(info, '§e[FastPost] §a成功向§b' + receiver + '§a发送邮件: §e' + msg)
	else:
		server.reply(info, '§e[FastPost] §4在服务器里找不到玩家§b' + receiver + '§4,可能该玩家还没有登入过!')
	

def checkMsg(server, info):
	if info.is_player:
		player = info.player
	else:
		player = '[Server]'
	listmsg = ''
	count = 0
	for orderid in orders['ids']:
		order = orders.get(str(orderid))
		if not order:
			continue
		if order.get('receiver') == player:
			count += 1
			listmsg += '\n' + RText('§c[§a' + str(count) + '§c] ').h('§c删除第[§a' + str(count) + '§c]条邮件§a(对应指令: §7' + Prefix + ' clean ' + str(count) + '§a)').c(RAction.run_command, f'{Prefix} clean ' + str(count)) + RText('§b' + order.get('sender')).h('§e回复§b' + order.get('sender') +'§a(对应指令: §7' + Prefix + ' send ' + order.get('sender') + ' <message>§a)').c(RAction.suggest_command, f'{Prefix} send ' + order.get('sender') + ' ') + ': ' + RText(order.get('msg')).h(order.get('time'))
	if listmsg == '':
		server.reply(info, '§e[FastPost] 空空如也，你没有收到的邮件.')
	else:
		server.reply(info, 
			'§e[FastPost] 邮件列表:   ' + 
			RText('§a[§c清空收件箱§a]')
				.h('对应指令: §7' + Prefix + ' clean')
				.c(RAction.run_command, f'{Prefix} clean') + 
			listmsg
		)
		
def cleanMsg(server, info):
	if info.is_player:
		player = info.player
	else:
		player = '[Server]'
	delIds = []
	for orderid in orders['ids']:
		order = orders.get(str(orderid))
		if not order:
			continue
		if order.get('receiver') == player:
			delIds.append(orderid)
	if len(delIds) == 0:
		server.reply(info, '§e[Fastpost] §4没有可删除的邮件.')
	else:
		try:
			for orderid in delIds:
				delMsg(orderid)
			server.reply(info, '§e[Fastpost] §a删除完成，共删除' + str(len(delIds)) + '条邮件.')
		except Exception:
			server.reply(info, '§e[Fastpost] §4删除邮件失败.')

def cleanSpecifiedMsg(server, info):
	if info.is_player:
		player = info.player
	else:
		player = '[Server]'
	count = 0
	try:
		id = int(info.content.split()[2])
	except Exception:
		server.reply(info, '§e[FastPost] §4输入格式不正确.')
	for orderid in orders['ids']:
		order = orders.get(str(orderid))
		if not order:
			continue
		if order.get('receiver') == player:
			count += 1
			if count == id:
				try:
					delMsg(orderid)
					server.reply(info, '§e[Fastpost] §a删除完成.')
				except Exception:
					server.reply(info, '§e[Fastpost] §4删除邮件失败.')
				checkMsg(server, info)
				return True

def delMsg(orderid):
	try:
		orders.pop(str(orderid))
		orders['ids'].remove(orderid)
	except Exception:
		server.logger.error("[FastPost] 删除邮件时出现错误.")
		server.logger.error(traceback.format_exc())
	saveOrdersJson()

def saveOrdersJson():
	global orders
	try:
		with open(OrderJsonFile, 'w') as f:
			json.dump(orders, f, indent=4)
		server.logger.info("[FastPost] 已保存Json数据.")
	except:
		return

def checkPlayer(player):
	for id in orders['players']:
		if id == player:
			return True
	return False

def getNextId():
	nextid = 1
	orders['ids'].sort() # 排序ids
	for i, id in enumerate(orders['ids']):
		if i != id: # 如果ids非连续则从中间插入
			nextid = i
			orders['ids'].append(nextid)
			return str(nextid)
	nextid = len(orders['ids'])
	orders['ids'].append(nextid)
	return str(nextid)