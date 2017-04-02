from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk import tokenize
sentence='no'
lines_list = tokenize.sent_tokenize(sentence)
sid = SentimentIntensityAnalyzer()
ss = sid.polarity_scores(sentence)
print ss['neg']
