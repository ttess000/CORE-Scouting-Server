import os

#bootstrap / activate virtual environment
activate_this = os.path.dirname(__file__) + '/virtualenv/bin/activate_this.py'
execfile(activate_this, dict(__file__=activate_this))

import web
import model.user as user
import model.helper as helper
from threading import Timer

urls = (
	'/', 'Index',
	'/user(?:/(.*))?', 'UserRequest',
	#TODO: add mongs like db browser, with option to only return json (read only?) (restricted - not able to read user collection)
	'/(.*)', 'Static',
)
app = web.application(urls, globals())


def cron():
	"""handles simple cron-like jobs such as rescraping"""
	print "cron jobs can be put here"
	t = Timer(10000, cron)
	t.start()

cron()


def processor(handler):
	"""app processor for setting contextual vars and dealing with output of script"""
	web.ctx.user = user.Instance()
	web.ctx.dev = (web.input(dev='False').dev == 'True')  # if ?dev=True then dev will be set to True, otherwise it defaults to False
	web.ctx.notify = []  # an array that holds notifications (like non-fatal errors or important messages)

	inputs = web.input(username='', token='')
	#only run user.check if username and token are defined... still allows use of default guest account
	if inputs.username != '' and inputs.token != '':
		try:
			web.ctx.user.check(username=inputs.username, token=inputs.token)  # validate user token if username and token are supplied
		except Exception as error:
			return helper.json_dump(helper.error_dump(error))  # needs json dump wrapper because returns done here won't get processed

	response = handler()

	if type(response) != str:
		response = helper.json_dump(response)  # format the response in json if it is a variable (not html being returned)

	return response

app.add_processor(processor)


class Index:
	def GET(self):
		return "<html><head><title>CSD</title></head><body>put docs generated by sphinx here</body></html>"


class UserRequest:
	def GET(self, name=''):
		""" handles requests for user data, logins, and signups """
		if name == None or name == '':
			return web.ctx.user.safe_data()
		elif name == 'login':
			#CONSIDER: add a delay to prevent excessive attempts
			inputs = web.input(username='', email='', password='')
			try:
				web.ctx.user.login(username=inputs.username, email=inputs.email, password=inputs.password)
			except Exception as error:
				return helper.error_dump(error)

			return helper.json_dump({'token': web.ctx.user.data['session']['token']})

		elif name == 'signup' or name == 'update':  # signup and update are basically the same thing
			inputs = web.input(data={})
			try:
				web.ctx.user.update(inputs.data)
			except Exception as error:
				return helper.error_dump(error)
			return {'notify': 'update successful'}

		else:
			return web.application.notfound(app)  # this means it is not one of the defined methods for interacting w/ the server


class Static:
	def GET(self, filename):
		"""
			searches for and returns a requested static file or 404s out
			this allows files in /static to be accessed as if they were in /
		"""
		try:
			return open(os.path.dirname(__file__) + '/static/' + filename, 'r').read()
		except:
			web.application.notfound(app)  # file not found


if __name__ == "__main__":
	app.run()
