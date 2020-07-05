from flask import Flask, render_template
from flask import request
import requests
import pkg_resources
from symspellpy import SymSpell, Verbosity
import nltk 
from nltk.corpus import wordnet
import pandas as pd
import numpy as np
import pickle
import clean_text2 as ct2
# import speech_recognition as sr
from googletrans import Translator


translator = Translator()

dictionary_path = pkg_resources.resource_filename("symspellpy", "frequency_dictionary_en_82_765.txt")
bigram_path = pkg_resources.resource_filename("symspellpy", "frequency_bigramdictionary_en_243_342.txt")
data_set = pd.read_csv('./Covid1.csv')
sym_spell = SymSpell(max_dictionary_edit_distance=3, prefix_length=7)
sym_spell.load_dictionary(dictionary_path, term_index=0, count_index=1)
sym_spell.load_bigram_dictionary(bigram_path, term_index=0, count_index=2)
def merge_two_dicts(x, y):
	z = x.copy()   # start with x's keys and values
	z.update(y)    # modifies z with y's keys and values & returns None
	return z

pickle_in1 = open('wv1.pickle','rb')
res1 = pickle.load(pickle_in1)
pickle_in2 = open('wv2.pickle','rb')
res2 = pickle.load(pickle_in2)
pickle_in1.close()
pickle_in2.close()
w2v = merge_two_dicts(res1,res2)
for i in range(3,9):
    pickle_in = open('wv{}.pickle'.format(i),'rb')
    w2v = merge_two_dicts(w2v,pickle.load(pickle_in))
    pickle_in.close()
pickle_in3 = open('vocab.pickle','rb')
vocab = pickle.load(pickle_in3)

def spelling_correction(sym_spell,input_term):
	suggestions = sym_spell.lookup_compound(input_term, max_edit_distance=2)
	sentence = []
	for suggestion in suggestions:
		sentence.append(str(suggestion).split(',')[0])
	return sentence
def cos_sim(u,v):
	numerator_ = u.dot(v)
	denominator_= np.sqrt(np.sum(np.square(u))) * np.sqrt(np.sum(np.square(v)))
	return numerator_/denominator_
def overall_similarity(q1,data_set):
	similarity=[]
	q1_clean = [ct2.getClearReview(i) for i in [q1]][0].split()
	x = len(q1_clean)
	for i in range(data_set.shape[0]):
		q2 = data_set.iloc[i]['Question']
		q2_clean = [ct2.getClearReview(i) for i in [q2]][0].split()
		ans = 0;
		for w1 in q1_clean:
			if w1 not in vocab:
				x-=1
				continue
			max1_ = 0
			for w2 in q2_clean:
				if w2 not in vocab:
					continue
				sim1 = cos_sim(w2v[w1],w2v[w2])
				max1_ = max(sim1,max1_)
			ans += max1_
		if(x>0):
			similarity.append(ans/len(q1_clean))
		else:
			similarity.append(0)

	return similarity



intents = np.unique(list(data_set.iloc[:]['Intent']))
dataset = data_set
l = []
def reply(sym_spell,input_term,isHindi=False):
	global dataset
	global l
	print(input_term)
	if isHindi==False:
		t=translator.detect(input_term)
		if t.lang=="hi":
			print("LAJSLJHFJ")
			s=translator.translate(input_term)
			input_term=s.text
			print(input_term)
			isHindi = True
	default_message = """Hello, hope you are staying at home safe. Welcome to Covid-19 Bot , I am here to answer your all chatbot related Faq's(To know how bot works type /help/ (slashes are important)). <br>Choose any one of the given intent: /testing/, /general/, /prevention_and_protection/, /spread/, /service/, /info/, /mental_health_and_fitness/, /myths_and_rumours/, /cure/, /child_women_pet/, /symptoms/, /movement/, /gathering/, /impact_of_corona/, /help"    help_message = "Hello, I am Covid 19 bot , How this bot works: this bot answers question related to all Covid 19 queries. First you need to choose a specific intent and then bot will suggest you  more question. Type any one of the question and bot will answer that question. If you want to ask any other intent question then type /main_menu/ and if any other question from same intent , then type that question and bot will answer that question and suggest more three question siilar to that question."""
	help_message = """Hello, I am Covid 19 bot , How this bot works: this bot answers question related to all Covid 19 queries. First you need to choose a specific intent and then bot will suggest you  more question. Type any one of the question and bot will answer that question. If you want to ask any other intent question then type /main_menu/ and if any other question from same intent , then type that question and bot will answer that question and suggest more three question siilar to that question. <br>Choose any one of the given intent: /testing/, /general/, /prevention_and_protection/, /spread/, /service/, /info/, /mental_health_and_fitness/, /myths_and_rumours/, /cure/, /child_women_pet/, /symptoms/, /movement/, /gathering/, /impact_of_corona/, /help"""
	extra_response = '/main menu/'
	last_ques = "For choosing other Faq from other intent type /main menu/ for going back"
	question = ""
	options = ""
	if(input_term == '/help/' or input_term=='/main_menu'):
		dataset = data_set
		if isHindi:
			return translator.translate(help_message,dest='hi').text
		return help_message

	if input_term[0]=='/':
		# if(len(input_term) == 2 and int(input_term[1])>0 and int(input_term[1])<4):

		# 	# # return three question

		# 	similarity2 = overall_similarity(l[int(input_term[1])-1], data_set)
		# 	# return l[int(input_term[1])-1]
		# 	ans = data_set.iloc[np.argmax(similarity2)]['Answer']
		# 	answer =  ans + '<br><br>Suggested questions:<br><br>'
		# 	l = []
		# 	for i in range(3):
		# 		similarity2[np.argmax(similarity2)] = 0
		# 		answer += str(i + 1)
		# 		answer += ". "
		# 		answer += data_set.iloc[np.argmax(similarity2)]['Question'] + '<br><br>'
		# 		l.append(str(data_set.iloc[np.argmax(similarity2)]['Question']))
		# 	if isHindi:
		# 		return translator.translate(answer,dest='hi').text
		# 	return answer

		if input_term[1:] in intents:
			# print(input_term)
			l = []
	#         if(input_term == i):
			dataset = data_set[data_set['Intent']== input_term[1:]]
			#return three question
			question = 'Choose from the suggestions given below or ask a question in the text field below.'
			if isHindi:
				question = translator.translate(question,dest='hi').text
			question += "^"
			for i in range(len(dataset.iloc[:3]['Question'])):
				# print('hi')
				# question += str(i+1)
				# question += ". "
				if isHindi:
					question += translator.translate(dataset.iloc[i]['Question'],dest='hi').text + "@"
				else:
					question += dataset.iloc[i]['Question'] +"@"
				# question += '<form action="/submit" name="msg"><input type="hidden" name="msg" value="{}"><button type="submit" class="link-button">'.format(dataset.iloc[i]['Question']) + str(dataset.iloc[i]['Question']) +'</button></form>'
				# l.append(str(dataset.iloc[i]['Question']))
				# question += "<br><br>"
			# question += "<br>Another Question?"
			# print(question)
			# if isHindi:
			# 	return translator.translate(question,dest='hi').text
			return question

	input_term = str(spelling_correction(sym_spell,input_term)[0])
	input_term = input_term.replace('corona virus','coronavirus')
	input_term = input_term.replace(' ovid' , ' coronavirus')
	input_term = input_term.replace('kovid' , ' covid')
	# print(input_term)
	#intent predict
	unique_intent=['general','mental_health_and_fitness','movement','smalltalk','child_women_pet','myths_and_rumours','spread','service','symptoms','testing','help','info','prevention_and_protection','impact_of_corona','gathering','cure']
	# pred = predictions(input_term)
	# intent_name=get_final_output(pred, unique_intent)[0]
	# dataset1=data_set[data_set["Intent"]==intent_name]
	#similarity matching in only question with predicted intent
	if type(dataset) != type(data_set):
		dataset = data_set
	similarity = overall_similarity(input_term,dataset)
	similarity2 = overall_similarity (input_term,data_set)
	# similarity3=overall_simialrity(input_term,dataset1)
	if(similarity2[np.argmax(similarity2)]>=similarity[np.argmax(similarity)]):
		ans = data_set.iloc[np.argmax(similarity2)]['Answer']
		if isHindi:
			ans = translator.translate(ans,dest='hi').text
		answer = ans + "^"
		for i in range(3):
			similarity2[np.argmax(similarity2)] = 0
			# answer += str(i+1)
			# answer += ". "
			if isHindi:
				answer += translator.translate(data_set.iloc[np.argmax(similarity2)]['Question'],dest='hi').text + "@"
			else:
				answer += data_set.iloc[np.argmax(similarity2)]['Question']+"@"
		# return dataset.iloc[np.argmax(similarity)]['Answer']
		# print(answer)
		# if isHindi:
		# 	answer = translator.translate(answer,dest='hi').text
		# 	print(answer) 
		# 	return answer
		return answer
	#return top three question, question
	ans = dataset.iloc[np.argmax(similarity)]['Answer']
	if isHindi:
		ans = translator.translate(ans,dest='hi').text
	answer = ans + "^"
	for i in range(3):
		similarity[np.argmax(similarity)]=0
		answer += str(i+1)
		answer += ". "
		if isHindi:
			answer += translator.translate(dataset.iloc[np.argmax(similarity)]['Question'],dest='hi').text + "@"
		else:
			answer += dataset.iloc[np.argmax(similarity)]['Question']+ "@"
	# return dataset.iloc[np.argmax(similarity)]['Answer']
	# if isHindi:
		# return translator.translate(answer,dest='hi').text
	return answer

print('Ready!!!')

app = Flask(__name__)


# @app.route('/process',methods=['POST'])
# def process():
# 	user_input=request.form['user_input']

# 	bot_response=answer(sym_spell,user_input)
# 	# bot_response=str(bot_response)
# 	print("CovidBot: "+bot_response)
# 	return render_template('index.html',user_input=user_input,
# 		bot_response=bot_response
# 		)

# @app.route("/answer", methods=["POST"])
# def answer():
#     countryselected = request.form['countryyy']
#     print("country selected!")
#     new_url = requests.get('https://corona.lmao.ninja/v2/countries/' + countryselected)
#     object = new_url.json()
#     print("json received!")
#     totc = object['cases']
#     actc = object['active']
#     recd = object['recovered']
#     ded = object['deaths']
#     newc = object['todayCases']
#     newd = object['todayDeaths']
#     crit = object['critical'] 

#     return render_template('index.html', cases = totc, active=actc, recovered=recd, deaths=ded, todayCases=newc, todayDeaths=newd, critical=crit)

@app.route("/get")
def get_bot_response():

	userText = request.args.get('msg')
	return reply(sym_spell,userText)

# @app.route('/submit')
# def submit():
	# for key, value in request.form.items():
		# print("key: {0}, value: {1}".format(key, value))
	# userText = str(request.form['msg'])
	# return reply(sym_spell,"hello")



@app.route("/")
def home():
	return render_template('home.html')

@app.route("/chatbot")
def chatbot():
	return render_template('chatbot.html')

@app.route("/tracker")
def tracker():
	return render_template('tracker.html')


@app.route("/answer", methods=["POST"])
def answer():
	countryselected = request.form['countryyy']
	print("country selected!")
	new_url = requests.get('https://corona.lmao.ninja/v2/countries/' + countryselected)
	object = new_url.json()
	print("json received!")
	totc = object['cases']
	actc = object['active']
	recd = object['recovered']
	ded = object['deaths']
	newc = object['todayCases']
	newd = object['todayDeaths']
	crit = object['critical']

	return render_template('tracker.html', show = True, cases = totc, active=actc, recovered=recd, deaths=ded, todayCases=newc, todayDeaths=newd, critical=crit)


if __name__=='__main__':
	app.run()
