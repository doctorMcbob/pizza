#building the puzzle game
from __future__ import unicode_literals, print_function
import pygame
from pygame.locals import *
import random as rd

pygame.init()
SCREEN = pygame.display.set_mode((1000, 700))
CLOCK = pygame.time.Clock()
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

IMG = {
	"C": pygame.image.load("bin/chs.png").convert(),
	"P": pygame.image.load("bin/pep.png").convert(),
	"V": pygame.image.load("bin/veg.png").convert(),
	"CRUST": pygame.image.load("bin/crust.png").convert()
}
IMG["CRUST"].set_colorkey((0, 0, 0))

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

def inputrender():
	global qtail
	for event in pygame.event.get():
		if event.type == QUIT:
			exit()
		if event.type == KEYDOWN:
			if event.key == K_LEFT:
				qtail[1] = ["L", None]
				qtail = qtail[1]
			if event.key == K_RIGHT:
				qtail[1] = ["R", None]
				qtail = qtail[1]
	
	if pygame.key.get_pressed()[K_SPACE]:
		qtail[1] = ["D", None]
		qtail = qtail[1]

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
	global qhead, qtail, board, POS, piece
	while True:
		try:
			if qhead[0] == "L":
				if board[POS[1]][POS[0]-1] is None:
					board[POS[1]][POS[0]] = None
					POS[0] -= 1
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

t = CLOCK.tick(30)
while step():
	t += CLOCK.tick(30)
	inputrender()
	resolve_queue()
	drawboard(SCREEN, board)
	draworders(SCREEN, ORDERS)
	drawnext(SCREEN, next)
	pygame.display.update()
	za = check()
	if za:
		POS = [3,0]
		piece = nextp
		nextp = mkpiece()
		t=0
		while t<(1000):
			drawboard(SCREEN, board)
			draworders(SCREEN, ORDERS)
			drawnext(SCREEN, next)
			SCREEN.blit(IMG["CRUST"], ((za[0]*60)+50,(za[1]*60)+50))
			pygame.display.update()
			t+=CLOCK.tick(30)
		if board[za[1]][za[0]] + board[za[1]+1][za[0]+1] in ORDERS:
			ORDERS.remove(board[za[1]][za[0]] + board[za[1]+1][za[0]+1])
		else:
			ORDERS.remove(board[za[1]+1][za[0]+1] + board[za[1]][za[0]])
		ORDERS.append(mkorder())
		for x, y in [(za[0],za[1]),(za[0]+1,za[1]),(za[0],za[1]+1),(za[0]+1,za[1]+1)]:
			board[y][x] = None
		
