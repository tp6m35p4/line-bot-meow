import json
import re
class LineData:
	def __init__(self, requestData):
		self.requestData = requestData
		self.jsonData = json.loads(requestData)

	def getType(self):
		return self.jsonData['events'][0]['message']['type']

	def getText(self):
		return self.jsonData['events'][0]['message']['text']
		
	def getUserId(self):
		return self.jsonData['events'][0]['source']['userId']

	def getReplyToken(self):
		return self.jsonData['events'][0]['replyToken']

	def isType(self, type):
		return self.getType() == type

	def isSeeSay(self):
		pattern = re.compile("^see[\u4e00-\u9fa5a-zA-Z0-9 ]{1,}say[\u4e00-\u9fa5a-zA-Z0-9 ]{1,}")
		print (type(self.getText()))
		if pattern.match(self.getText()):
			print ('Y')
			return True
		else:
			print ('N')
			return False
		
		# return pattern.match(self.getText())