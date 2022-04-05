import os
os.chdir(os.path.split(__file__)[0])
import argparse
import queue
import re
from DataLib import GetFile
import sys
from time import sleep
from datetime import datetime
from multiprocessing import Process
from multiprocessing import Queue
from tqdm import tqdm
sys.path.append("G:\\NewCode\\Wordle\\app")
import misc
import json
from random import choice
from colorama import Fore

def ParseArgs():
	parser = argparse.ArgumentParser("app ", description="Info: If every time you try to run the game, you get a 'MemoryError', then this is due to the datafile being messed up, just delete the 'data.ini' located at the root of the program (all of your data will be gone)")
	parser.add_argument("-p", "--play", help="Use this to start playing the game", action="store_true")
	parser.add_argument("-a", "--account", help="Use this to manage your account", action="store_true")
	parser.add_argument("-i", "--account-info", help="Get your account info", action="store_true")
	parser.add_argument("-hi", "--history", help="Use this to view your games and history", action="store_true")

	args = parser.parse_args()

	return args

def DownloadWords():
	print("Downloading words...")
	q = Queue()
	#p = Process(target=misc.DownloadFile, args=("https://raw.githubusercontent.com/first20hours/google-10000-english/master/google-10000-english-usa-no-swears.txt", q, "words"))
	p = Process(target=misc.DownloadFile, args=("https://raw.githubusercontent.com/tabatkins/wordle-list/main/words", q, "words"))
	p.start()
	try:
		size = q.get(timeout=5)
	except queue.Empty:
		p.terminate()
		sys.exit("Unstable internet")
	if (size == "no internet"):
		p.terminate()
		sys.exit("No internet")
	q.put("start")
	while True:
		try:
			data = q.get()
			if (data == "done"):
				break
		except queue.Empty:
			break
	p.terminate()
	



def main():
	args = ParseArgs()
	if (os.path.exists("data.ini") == False):
		open("data.ini", "wb").close()
		GetFile("data.ini").save()

	datafile = GetFile("data.ini")

	if (len(datafile.GetKeys())) == 0:
		print("No account detected, making new one...")
		sleep(1)
		user = input("Username ? ")
		r = re.compile("(([a-zA-Z])?[0-9]?)+")
		if (r.match(user).group() != user):
			print(f"'{user}' is an invalid username")
			return
		datafile.SaveKey("username", str(user))
		datafile.SaveKey("total", str(0))
		datafile.SaveKey("right", str(0))
		datafile.SaveKey("wrong", str(0))
		datafile.SaveKey("history", {})
		datafile.save()
		print(f"{Fore.GREEN}Account Made!{Fore.WHITE}")

	if (args.account_info):
		print("Getting info...")
		sleep(0.5)
		print("      Username: " + datafile.ReadKey("username"))
		print(
f'''      Total games done: {datafile.ReadKey("total")}
	Games won: {datafile.ReadKey("right")}
	Games lost: {datafile.ReadKey("wrong")}''')
		return
	if (args.account):
		print("Options: delete, changeuser")
		opt = input("> ").lower()
		if (opt == "delete"):
			os.remove("data.ini")
			print("Data wiped")
		elif (opt == "changeuser"):
			r = re.compile("(([a-zA-Z])?[0-9]?)+")
			user = input("New username ? ")
			if (r.match(user).group() != user):
				print(f"'{user}' is an invalid username")
				return
			datafile.SaveKey("username", str(user))
			datafile.save()
			print("Username changed")
		return

	if (args.play):
		DownloadWords()
		os.system("cls")
		words = []
		with open("words", "r") as f:
			data = list(f.readlines())
		os.remove("words")
		r = re.compile("([a-z]){5}")
		for i in data:
			i = i.replace("\n", "")
			if (r.match(i) != None):
				if (r.match(i).group() == i):
					words.append(i)
		word = choice(words)
		Lives = 5
		print("Type 'exit' to exit")
		hist = ""
		while Lives != 0:
			hist += "Lives: " + str(Lives) + "\n"
			print("Lives: " + str(Lives))
			while True:
				guess = input("Guess word ? ").lower()
				hist += "Guess word ? " + guess + "\n"
				if (guess == "exit"):
					datafile.save()
					sys.exit()
				if (r.match(guess) != None):
					if (r.match(guess).group() == guess):
						if (guess in words):
							break
						else:
							hist += "Not in list of words\n"
							print("Not in list of words")
					else:
						hist += "Invalid characters or not 5 letters\n"
						print("Invalid characters or not 5 letters")
				else:
					hist += "Invalid characters or not 5 letters\n"
					print("Invalid characters or not 5 letters")
			if (guess != word):
				Lives -= 1
			string = ""
			for i in range(len(guess)):
				if (guess[i] == word[i]):
					string += f"   {Fore.GREEN}" + guess[i]
				elif (guess[i] in word):
					string += f"   {Fore.YELLOW}" + guess[i]
				else:
					string += f"   {Fore.RED}" + guess[i]
			string += Fore.WHITE
			hist += string + "\n"
			print(string)
			if (guess == word):
				hist += f"\n{Fore.GREEN}CORRECT!{Fore.WHITE}" + "\n"
				print(f"\n{Fore.GREEN}CORRECT!{Fore.WHITE}")
				break
		datafile.SaveKey("total", str(int(datafile.ReadKey("total"))+1))
		if (Lives == 0):
			hist += f"The correct word was '{word}'" + "\n"
			print(f"The correct word was '{word}'")
			datafile.SaveKey("wrong", str(int(datafile.ReadKey("wrong"))+1))
		else:
			hist += "Good Job!\n"
			print("Good Job!")
			datafile.SaveKey("right", str(int(datafile.ReadKey("right"))+1))
		data = datafile.ReadKey("history")
		keys = list(data.keys())
		keys.sort()
		if (len(keys) == 0):
			key = 1
		else:
			key = keys[-1]+1
		time = datetime.now()
		datatosave = {"word": word, "time": f"{time.month}-{time.day}-{time.year} {time.hour}:{time.minute}:{time.second}", "history": hist}
		data[key] = datatosave
		datafile.SaveKey("history", data)
		datafile.save()
	if (args.history):
		data = datafile.ReadKey("history")
		print("Type in a game's ID to view the history or type 'no' to exit\n")
		for i in list(data.keys()):
			print("ID: " + str(i) + " " * (5-len(str(i))) + "Word: " + str(data[i]["word"]) + " " * (5-len(str(i))) + "Time: " + str(data[i]["time"]))
		id = input("\nID ? ").lower()
		if (id == "no"):
			return
		else:
			id = int(id)
		if (id not in list(data.keys())):
			print("Not a valid ID")
			return
		os.system("cls")
		print(f"{Fore.CYAN}History for game {i}:\n{Fore.WHITE}")
		print(data[id]["history"])
		


if (__name__ == "__main__"):
	main()