class StopWords :
    def __init__(self) :
        self.stopwords = self.load_data("dictionary/stopwords")
        self.backadj = self.load_data("dictionary/back_adjective")
        self.backwords = self.load_data("dictionary/back_nouns")
        self.unitwords = self.load_data("dictionary/unit_words")
        self.pre_build_unit = self.load_data("dictionary/pre_build_unit")
        self.ko_num = self.load_data("dictionary/ko_num")
        self.not_ko_num = self.load_data("dictionary/not_ko_num")
        self.kiwi_stopwords = self.load_data("dictionary/kiwi_stopwords")
        self.kiwi_adj_stopwords = self.load_data("dictionary/kiwi_stopadjective")
    
    def load_data(self,path) :
        result = []
        with open(f'./{path}.txt','r') as f:
            while True:
                line = f.readline()
                if not line : break
                result.append(line.strip().replace(' ',""))
        
        return result
    
    def reload_stopwords(self) :
        self.stopwords = self.load_data("dictionary/stopwords")
        self.backadj = self.load_data("dictionary/back_adjective")
        self.backwords = self.load_data("dictionary/back_nouns")
        self.unitwords = self.load_data("dictionary/unit_words")
        self.pre_build_unit = self.load_data("dictionary/pre_build_unit")
        self.ko_num = self.load_data("dictionary/ko_num")
        self.not_ko_num = self.load_data("dictionary/not_ko_num")
        self.kiwi_stopwords = self.load_data("dictionary/kiwi_stopwords")
        self.kiwi_adj_stopwords = self.load_data("dictionary/kiwi_stopadjective")
        return True