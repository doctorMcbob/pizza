# PuzzlePalace.py
from __future__ import unicode_literals, print_function
import pygame
from pygame.locals import *
import Game.gameassets
from Game.gameassets import *
import random as rd

pygame.init()
CLOCK = pygame.time.Clock()
SCREEN = pygame.display.set_mode((1000, 700))

TF1 = pygame.font.SysFont("Helvetica", 25)
TF2 = pygame.font.SysFont("Helvetica", 50)


IMG = {
	"C": pygame.image.load("bin/chs.png").convert(),
	"P": pygame.image.load("bin/pep.png").convert(),
	"V": pygame.image.load("bin/veg.png").convert(),
	"CRUST": pygame.image.load("bin/crust.png").convert(),
	"PLAYER":{
		"stand": pygame.image.load("bin/player_stand.png").convert(),
		"fall": pygame.image.load("bin/player_fall.png").convert(),
	},
	"BTN":{
		"L": pygame.image.load("bin/left_button.png").convert(),
		"R": pygame.image.load("bin/right_button.png").convert(),
		"D": pygame.image.load("bin/down_button.png").convert(),
		"P": pygame.image.load("bin/pep_button.png").convert(),
		"V": pygame.image.load("bin/veggie_button.png").convert(),
		"C": pygame.image.load("bin/cheese_button.png").convert(),
	},
	"WALL": pygame.image.load("bin/wall.png").convert(),
}
for key in IMG["PLAYER"]:
	IMG["PLAYER"][key].set_colorkey((254, 255, 255))
	IMG["PLAYER"][key] = [None, IMG["PLAYER"][key], pygame.transform.flip(IMG["PLAYER"][key], 1, 0)]

for key in IMG["BTN"]:
	IMG["BTN"][key].set_colorkey((255, 255, 255))

IMG["CRUST"].set_colorkey((0, 0, 0))

def makeplatform(*args, **kwargs):
	platform = Game.gameassets.makeplatform(*args, **kwargs)
	img = pygame.surface.Surface((platform["rect"].w, platform['rect'].h))
	for x in range(platform['rect'].w/40 +1):
		for y in range(platform['rect'].h/40 +1):
			img.blit(IMG['WALL'], (x*40, y*40))
	platform["img"] = img
	return platform

def player_advance(this, **kwargs): 
	if this['state'] == 'stand': this['jumps'] = 1
	this['img'] = IMG["PLAYER"][this['state']][this['direction']]
def pressbtn(this, level={"btns":[]}):
	for btn in level['btns']:
		if btn['state'] == 'pressable': btn['press'](btn)
player = {
	'name': '@',
	'rect': pygame.rect.Rect((50, 610), (20, 40)),
	'img': IMG["PLAYER"]['stand'][1],
	'color': (200, 150, 150),
	'x vel': 0,
	'y vel': 0,
	'state': 'stand',
	'jumps': 1,
	'jump vel': -12,
	'grav': 1,
	'speed': 5,
	'walk speed': 5,
	'direction': 1,
	'friction': 1,
	'advance function': player_advance,
	'action': pressbtn,
	'buttons': {
		"left": K_LEFT,
		"right": K_RIGHT,
		"jump": K_z,
		"action":K_x,
	}
}

########### ------------ INTRO SCENE ------------
walls = [makeplatform((0, 0, 5, 700), invisible=True), makeplatform((800, 0, 200, 600)), makeplatform((0, 680, 1000, 20)), ]
FLAG = False
COUNT = 0
def doortrigger(this, game): 
	global FLAG, COUNT
	COUNT += 1
	if COUNT > 40:
		FLAG = True

door = {
	'name':'door',
 	'rect':pygame.rect.Rect(800, 600, 200, 80),
 	'color': (0, 0, 0),
 	'trigger function': doortrigger
 }
drawing = [[pygame.rect.Rect(720, 600, 75, 29), (150, 150, 100)], [pygame.rect.Rect(720, 595, 80, 2), (0, 0, 0)]]

while not FLAG:
	SCREEN.fill((255, 255, 255))
	for rect, color in drawing:
		pygame.draw.rect(SCREEN, color, rect)
	SCREEN.blit(TF1.render("Enter",0,(0,0,0)), (722, 602))
	render_input({"player":player, 'btns':[]})
	move_and_collision(player, walls)
	trigger(door, player, None)
	for actor in [door, player] + walls:
		if 'advance function' in actor: actor['advance function'](actor)
		draw(actor, SCREEN)
	SCREEN.blit(TF1.render("PiZZA PETE'S",0,(0,0,0)), (100, 100))
	SCREEN.blit(TF2.render("PUZZLE PALACE",0,(0,0,0)), (100, 126))
	pygame.display.update()
	CLOCK.tick(30)

########### ------------ GAME SCENE -------------
player['rect'].x, player['rect'].y = (700, 600)
HEL20 = pygame.font.SysFont("Helvetica", 20)

W, H = 7, 10
board =  [[None for x in range(W)] for x in range(H)]
#how true gangsters write Queues in python
qhead = [None,None]
qtail = qhead

SPEED = 1000
POS = [3, 0]
def mkpiece():
	return rd.choice(["C", "P", "V"])
piece = mkpiece()
nextp = mkpiece()
board[POS[1]][POS[0]] = piece
def mkorder():
	return mkpiece() + mkpiece()
ORDERS = [mkorder() for x in range(5)]


def nbrs(pos, board):
	""" generator, returns neighbors in format:
	[ 0, 1, 2,
	  3, 4, 5,
	  6, 7, 8,]
	"""
	for x in [-1, 0, 1]:
		for y in [-1, 0, 1]:
				if -1 < pos[0] + x < W and -1 < pos[1] + y < H:
					yield board[pos[1]+y][pos[0]+x]
				else:
					yield None

def mkbtn(rect, output):
	def spit(this):
		global qtail	
		qtail[1] = [this['output'], None]
		qtail = qtail[1]

	def reset(this, **kwargs):
		this['state'] = 'not'	
	def press(this, g):
		this['state'] = 'pressable'
	return {
		"name": output + " btn",
		"output": output,
		"advance function": reset,
		'press': spit,
		"trigger function": press,
		"state": "idle",
		"timer": 0,
		"img": (IMG['BTN'][output], (-10, -10)),

		'rect': pygame.rect.Rect(rect),
		'color': (50, 50, 120),
	}

def drawboard(SCREEN, board):
	SCREEN.fill((95, 70, 46))
	pygame.draw.rect(SCREEN, (0,0,0), pygame.rect.Rect(45, 45, 430, 610))
	for y, line in enumerate(board):
		for x, piece in enumerate(line):
			if piece is not None:
				SCREEN.blit(IMG[piece], ((x*60)+50, (y*60)+50))
			else:
				pygame.draw.rect(SCREEN, (95, 70, 46), pygame.rect.Rect((x*60)+50, (y*60)+50, 60, 60))

def draworders(SCREEN, ORDERS, X=500, Y=20):
	SCREEN.blit(HEL20.render("ORDERS:",0,(0,0,0)), (X, Y))
	Y+=25
	pygame.draw.rect(SCREEN, (0, 0, 0), pygame.rect.Rect(X-5, Y-5, 130, 125*len(ORDERS)+5))
	for order in ORDERS:
		SCREEN.blit(IMG[order[0]], (X, Y))
		SCREEN.blit(IMG[order[1]], (X+60, Y))
		SCREEN.blit(IMG[order[0]], (X, Y+60))
		SCREEN.blit(IMG[order[1]], (X+60, Y+60))
		SCREEN.blit(IMG["CRUST"], (X, Y))
		Y += 125

def drawnext(SCREEN, next, X=415, Y=20):
	pygame.draw.rect(SCREEN, (0,0,0), pygame.rect.Rect(X, Y, 70, 70))
	SCREEN.blit(IMG[nextp], (X+5, Y+5))
	pygame.draw.rect(SCREEN, (0,0,0), pygame.rect.Rect(X+25, Y+45, 50, 30))
	pygame.draw.rect(SCREEN, (95,70,46), pygame.rect.Rect(X+30, Y+50, 40, 20))
	SCREEN.blit(HEL20.render("Next", 0, (0,0,0)), (X+30, Y+48))

def resolve_queue():
	global qhead, qtail, board, POS, piece, nextp
	while True:
		try:
			if qhead[0] == "L":
				if board[POS[1]][POS[0]-1] is None:
					board[POS[1]][POS[0]] = None
					POS[0] = max(0, POS[0]-1)
					board[POS[1]][POS[0]] = piece
			if qhead[0] == "R":
				if board[POS[1]][POS[0]+1] is None:
					board[POS[1]][POS[0]] = None
					POS[0] += 1
					board[POS[1]][POS[0]] = piece
			if qhead[0] == "D":
				if board[POS[1]+1][POS[0]] is None:
					board[POS[1]][POS[0]] = None
					POS[1] += 1
					board[POS[1]][POS[0]] = piece

			if qhead[0] in ["P", "V", "C"]:
				nextp = qhead[0]
		except IndexError:
			pass

		if qhead is qtail:
			qhead[0] = None
			break
		qhead = qhead[1]

def drop(board):
	global POS
	for y in range(len(board))[::-1][1:]:
		for x, spot in enumerate(board[y]):
			if [x, y] == POS: 
				
				continue
			if spot is None: continue
			if board[y+1][x] is None:
				board[y+1][x] = spot
				board[y][x] = None
				

def step():
	global board, POS, piece, nextp, t
	if t > SPEED:
		t = 0
		drop(board)
		if POS[1] + 1 < len(board) and board[POS[1]+1][POS[0]] is None:
			board[POS[1]][POS[0]] = None
			POS[1] += 1
			board[POS[1]][POS[0]] = piece
		else:
			POS = [3, 0]
			if board[POS[1]][POS[0]] == None:
				piece = nextp
				nextp = mkpiece()
				board[POS[1]][POS[0]] = piece
			else:
				return False
	return True

def check():
	global board, ORDERS
	for y, line in enumerate(board):
		for x, spot in enumerate(line):
			if spot is None: continue
			mini = [piece for piece in nbrs((x, y), board)]
			if None in [mini[4], mini[5], mini[7], mini[8]]:
				continue
			if (mini[4] == mini[5] and mini[7] == mini[8]) or (mini[4] == mini[7] and mini[5] == mini[8]):
				if mini[4] + mini[8] in ORDERS or mini[8] + mini[4] in ORDERS:
					return (x, y)		
	return None

level1 = {
	"limit": 10,
	"player":player,
	"platforms": [makeplatform(rect) for rect in [(640, 680, 380, 20),(640, 300, 380, 20),(640,320,20,360),(980,320,20,360)]],
	"btns": [mkbtn((680, 640, 20, 20), "L"), mkbtn((935, 640, 20, 20), "R"), mkbtn((800, 640, 20, 20), "D")],
}
level2 = {
	"limit": 10.,
	"player":player,
	"platforms": [makeplatform(rect) for rect in [(640, 680, 380, 20),(640, 300, 380, 20),(640,320,20,360),(980,320,20,360)]],
	"btns": [mkbtn((680, 610, 20, 20), "L"), mkbtn((935, 610, 20, 20), "R"), mkbtn((800, 610, 20, 20), "D")],
}
level3 = {
	"limit": 15,
	"player":player,
	"platforms": [makeplatform(rect) for rect in [
		(640, 680, 380, 20),(640, 300, 380, 20),(640, 320, 20, 360),(980, 320, 20, 360),
		(660, 640, 40, 20),(940, 640, 40, 20),(730, 590, 40, 20),(870, 590, 40, 20),(800, 550, 40, 20)
		]],
	"btns": [
		mkbtn((725, 640, 20, 20), "P"), mkbtn((895, 640, 20, 20), "C"), mkbtn((810, 640, 20, 20), "V"),
		mkbtn((740, 550, 20, 20), "L"), mkbtn((880, 550, 20, 20), "R"), mkbtn((810, 510, 20, 20), "D"),
	],
}
level4 = {
	"limit": 15,
	"player":player,
	"platforms": [makeplatform(rect) for rect in [
		(640, 680, 380, 20),(640, 300, 380, 20),(640, 320, 20, 360),(980, 320, 20, 360),
		(660, 615, 40, 20),(940, 615, 40, 20),(730, 550, 40, 20),(870, 550, 40, 20),(800, 590, 40, 20)
		]],
	"btns": [
		mkbtn((725, 640, 20, 20), "P"), mkbtn((895, 640, 20, 20), "C"), mkbtn((810, 640, 20, 20), "V"),
		mkbtn((740, 510, 20, 20), "L"), mkbtn((880, 510, 20, 20), "R"), mkbtn((810, 550, 20, 20), "D"),
	],
}

levels = [level1, level2, level3, level4]#[::-1]#DEBUG
clears = 0
leveln = 0
def drawclears(SCREEN):
	global leveln, levels, clears
	SCREEN.blit(HEL20.render("LEVEL: "+str(leveln+1)+" NEXT LEVEL IN: "+str(levels[leveln]['limit']-clears),0,(0,0,0)), (640, 270))


def platformer_step(level):
	render_input(level)
	move_and_collision(level['player'], level['platforms'])
	for actor in level['platforms'] + level['btns'] + [level['player']]:
		if "advance function" in actor:
			actor['advance function'](actor,level=level)
		if "trigger function" in actor:
			trigger(actor, level['player'], level)
		draw(actor, SCREEN)


t = CLOCK.tick(30)
while step():
	za = check()
	t += CLOCK.tick(30)
	resolve_queue()
	drawboard(SCREEN, board)
	draworders(SCREEN, ORDERS)
	drawnext(SCREEN, next)
	drawclears(SCREEN)
	platformer_step(levels[leveln])
	pygame.display.update()
	if za:
		t=0
		clears += 1
		while t<(1000):
			drawboard(SCREEN, board)
			draworders(SCREEN, ORDERS)
			drawnext(SCREEN, next)
			drawclears(SCREEN)
			SCREEN.blit(IMG["CRUST"], ((za[0]*60)+50,(za[1]*60)+50))
			platformer_step(levels[leveln])
			pygame.display.update()
			t+=CLOCK.tick(30)
		if tuple(POS) in [(za[0],za[1]),(za[0]+1,za[1]),(za[0],za[1]+1),(za[0]+1,za[1]+1)]:
			POS = [3, 0]
			piece = nextp
			nextp = mkpiece()
		if board[za[1]][za[0]] + board[za[1]+1][za[0]+1] in ORDERS:
			ORDERS.remove(board[za[1]][za[0]] + board[za[1]+1][za[0]+1])
		else:
			ORDERS.remove(board[za[1]+1][za[0]+1] + board[za[1]][za[0]])
		ORDERS.append(mkorder())
		for x, y in [(za[0],za[1]),(za[0]+1,za[1]),(za[0],za[1]+1),(za[0]+1,za[1]+1)]:
			board[y][x] = None
		if clears >= levels[leveln]['limit']:
			clears = 0
			leveln += 1
			if leveln >= len(levels): 
				print("thats all i've programmed sorry")
				exit()

