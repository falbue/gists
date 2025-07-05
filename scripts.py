import requests
import json

def gist_data(tta_data):
	gist_id = tta_data["gist_id"]
	url = f"https://api.github.com/gists/{gist_id}"
	response = requests.get(url)
	gist_data = response.json()
	
	description = gist_data.get("description", "")
	num_files = len(gist_data["files"])
	updated_at = gist_data["updated_at"]
	comments = gist_data["comments"]
	owner = f"https://github.com/users/{gist_data['owner']['login']}"
	created_at = gist_data["created_at"]
	forks_count = len(gist_data.get("forks", []))
	
	data = {
	    "gist_description": description,
	    "gist_num_files": num_files,
	    "gist_updated_at": updated_at,
	    "gist_forks_count": forks_count,
	    "gist_comments": comments,
	    "gist_created_at": created_at,
	    "gist_owner": owner
	}

	return data

def get_gists(tta_data):
	owner = 'falbue'
	url = f"https://api.github.com/users/{owner}/gists"
	response = requests.get(url)
	if response.status_code == 200:
		gist_data = response.json()
		keyboard = {}
		for gist in gist_data:
			keyboard[f'gist|{gist["id"]}'] = gist["description"]
	else:
		keyboard = {"error":"Гисты не найдены"}
	return keyboard

def gist_files(tta_data):
	gist_id = tta_data["gist_id"]
	url = f"https://api.github.com/gists/{gist_id}"
	response = requests.get(url)
	gist_data = response.json()
	
	files = (gist_data["files"])
	data = {}

	for filename in files:
		file = files[filename]
		data[f'gist_file|{gist_id}|{file["filename"]}'] = file["filename"]

	return data

def code_file(tta_data):
	# print(tta_data)
	gist_id = tta_data["gist_id"]
	url = f"https://api.github.com/gists/{gist_id}"
	response = requests.get(url)
	gist_data = response.json()

	files = (gist_data["files"])
	data = {}

	code = files[tta_data['gist_file']]["content"]

	data["code"] = code

	return data

# code_file({"gist_id":"42bccfd10353c810408b8535dcc20816", "filename":"Dockerfile"})