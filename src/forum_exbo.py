import requests
from datetime import datetime

class ForumEXBO:
	def __init__(self):
		self.api = "https://forum.exbo.ru"
		self.headers = {
		"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36",
		"Content-Type": "application/json; charset=UTF-8"
		}
		self.token = None
		self.user_id = None
		self.get_cookies()
		
	def get_cookies(self):
		response =  requests.get(self.api, headers=self.headers)
		self.flarum_session = response.cookies["flarum_session"]
		self.x_csrf_token = response.headers["X-CSRF-Token"]
		self.headers["cookie"] = f"flarum_session={self.flarum_session}"
		self.headers["x-csrf-token"] = self.x_csrf_token

	def login(
			self,
			identification: str,
			password: str,
			remember: bool = True):
		data = {
		"identification": identification,
		"password": password,
		"remember": remember
		}
		response = requests.post(
			f"{self.api}/login", json=data, headers=self.headers).json()
		try:
			self.token = response["token"]
			self.user_id = response["userId"]
		except Exception as e:
			print(e)
		return response

	def like_comment(self, comment_id: int):
		data = {
		"data": {
			"type": "posts",
			"id": comment_id,
			"attributes": {
				"isLiked": True
				}
			}
		}
		return requests.post(
			f"{self.api}/api/posts/{comment_id}",
			json=data,
			headers=self.headers).json()

	def unlike_comment(self, comment_id: int):
		data = {
			"data": {
				"type": "posts",
				"id": comment_id,
				"attributes": {
					"isLiked": False
				}
			}
		}
		return requests.post(
			f"{self.api}/api/posts/{comment_id}",
			json=data,
			headers=self.headers).json()

	def react_comment(self, comment_id: int, reaction_id: int = 5):
		data = {
			"data": {
				"type": "posts",
				"id": comment_id,
				"attributes": {
					"reaction": reaction_id
				}
			}
		}
		return requests.post(
			f"{self.api}/api/posts/{comment_id}",
			json=data,
			headers=self.headers).json()

	def comment(self, discussion_id: int, content: str):
		data = {
			"data": {
				"type": "posts",
				"attributes": {"content": content},
				"relationships": {
					"discussion": {
						"data": {
							"type": "discussions",
							"id": discussion_id
						}
					}
				}
			}
		}
		return requests.post(
			f"{self.api}/api/posts",
			json=data,
			headers=self.headers).json()

	def edit_comment(
			self,
			comment_id: int,
			content: str = None,
			is_hidden: bool = False):
		data = {
			"data": {
				"type": "posts",
				"id": comment_id
			}
		}
		if content:
			data["attributes"] = {"content": content}
		if is_hidden:
			data["attributes"] = {"isHidden": is_hidden}
		return requests.post(
			f"{self.api}/api/posts/{comment_id}",
			json=data,
			headers=self.headers).json()

	def report_comment(
			self,
			comment_id: int,
			reason: str,
			detail: str = None):
		data = {
			"data": {
				"type": "flags",
				"attributes": {
					"reason": reason
				},
				"relationships": {
					"user": {
						"data": {
							"type": "users",
							"id": self.user_id
						}
					},
				"post": {
					"data": {
						"type": "posts",
						"id": comment_id
						}
					}
				}
			}
		}
		if detail:
			data["attributes"] = {"reasonDetail": detail}
		return requests.post(
			f"{self.api}/api/flags",
			json=data,
			headers=self.headers).json()

	def follow_discussion(self, discussion_id: int):
		data = {
			"data": {
				"type": "discussions",
				"id": discussion_id,
				"attributes": {
					"subscription": "follow"
				}
			}
		}
		return requests.post(
			f"{self.api}/api/discussions/{discussion_id}",
			json=data,
			headers=self.headers).json()

	def unfollow_discussion(self, discussion_id: int):
		data = {
			"data": {
				"type": "discussions",
				"id": discussion_id,
				"attributes": {
					"subscription": None
				}
			}
		}
		return requests.post(
			f"{self.api}/api/discussions/{discussion_id}",
			json=data,
			headers=self.headers).json()

	def get_user_discussions(
			self,
			username: str,
			include: str = "user,lastPostedUser,mostRelevantPost,mostRelevantPost.user,tags,tags.parent,firstPost,lastPost", 
			sort: str = "-createdAt", 
			offset: int = 0):
		return requests.get(
			f"{self.api}/api/discussions?include={include}&filter[q]=author:{username}&sort={sort}&page[offset]={offset}",
			headers=self.headers).json()

	def get_user_mentioned(
			self,
			user_id: int,
			offset: int = 0,
			limit: int = 20,
			sort: str = "-createdAt"):
		return requests.get(
			f"{self.api}/api/posts?filter[type]=comment&filter[mentioned]={user_id}&page[offset]={offset}&page[limit]={limit}&sort={sort}",
			headers=self.headers).json()
	
	def get_user_comments(
			self,
			username: str,
			offset: int = 0,
			limit: int = 20,
			sort: str = "-createdAt"):
		return requests.get(
			f"{self.api}/api/posts?filter[author]={username}&filter[type]=comment&page[offset]={offset}&page[limit]={limit}&sort={sort}",
			headers=self.headers).json()

	def get_user_info(self, user_id: int):
		return requests.get(
			f"{self.api}/api/users/{user_id}", headers=self.headers).json()

	def get_notifications(self, offset: int = 0):
		return requests.get(
			f"{self.api}/api/notifications?page[offset]={offset}", headers=self.headers).json()

	def get_discussions(
			self,
			include: str = "user,lastPostedUser,tags,tags.parent,firstPost,firstPost,lastPost",
			sort: str = "-createdAt",
			offset: int = 20):
		return requests.get(
			f"{self.api}/api/discussions?include={include}&sort={sort}&page[offset]={offset}",
			headers=self.headers).json()

	def mark_discussions_read(self):
		data = {
			"data": {
				"type": "users",
				"id": self.user_id,
				"attributes": {
					"markedAllAsReadAt": f"{datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]}Z"
				}
			}
		}
		return requests.post(
			f"{self.api}/api/users/{self.user_id}", 
			json=data,
			headers=self.headers).json()

	def ignore_user(self, user_id: int):
		data = {
			"data": {
				"type": "users",
				"id": user_id,
				"attributes": {
					"ignored": True
				}
			}
		}
		return requests.post(
			f"{self.api}/api/users/{user_id}",
			json=data,
			headers=self.headers).json()


	def unignore_user(self, user_id: int):
		data = {
			"data": {
				"type": "users",
				"id": user_id,
				"attributes": {
					"ignored": False
				}
			}
		}
		return requests.post(
			f"{self.api}/api/users/{user_id}",
			json=data,
			headers=self.headers).json()

	def reset_password(self, email: str):
		data = {
		"email": email
		}
		return requests.post(
			f"{self.api}/forgot",
			json=data,
			headers=self.headers).json()
