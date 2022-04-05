import hashlib
from tqdm import tqdm
import os
from time import sleep
import requests

def GetHash(file : str) -> bytes:
	hasher = hashlib.sha256()
	bar = tqdm(total = os.path.getsize(file), leave=False, desc="Hashing file...", unit="B")
	with open(file, "rb") as f:
		chunk = 0
		while chunk != b'':
			
			bar.update(1024)
			chunk = f.read(1024)
			hasher.update(chunk)

		bar.close()
		sleep(1)
		return hasher.hexdigest()


def split(path: str) -> list:
	import os
	pathsplit = []
	path = os.path.abspath(path)
	if ("\\" in path):
		pathsplit = path.split("\\")
	elif ("/" in path):
		pathsplit = path.split("/")

	Drive = pathsplit[0]
	Directory = "/".join(pathsplit[1:-1])
	if ("." in pathsplit[-1]):
		file = pathsplit[-1].split(".")
		Filename = ".".join(file[:-1])
		ext = file[-1]
	else:
		ext = ""
		Filename = pathsplit[-1]

	pathsplit = [Drive, Directory, Filename, ext]

	return pathsplit

def DownloadFile(url, q, name):
	try:
		r = requests.get(url, stream=True)
	except requests.exceptions.ConnectionError:
		q.put("no internet")
		return
	size = r.headers.get("content-length", None)
	q.put(size)
	while q.get() != "start":
		sleep(0.1)
	with open(name, "wb") as file:
		for i in r.iter_content(1024):
			q.put(len(i))
			file.write(i)

	q.put("done")
	return