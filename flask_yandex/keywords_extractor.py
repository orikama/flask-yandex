from rake_nltk import Rake


class KeywordsExtractor():

    def __init__(self):
        self.extractor = Rake(language="russian")

    def get_keywords(self, text):
        self.extractor.extract_keywords_from_text(text)

        return self.extractor.get_ranked_phrases()
