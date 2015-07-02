import sys
import argparse
from itertools import izip

from numpy import argsort, sort
from pylearn2.utils import serial

from hunvec.datasets.word_tagger_dataset import WordTaggerDataset
from hunvec.corpus.tagged_corpus import RawCorpus, TaggedCorpus
from hunvec.utils.fscore import FScCounter

def create_argparser():
    argparser = argparse.ArgumentParser()
    argparser.add_argument('model')
    argparser.add_argument('--input', dest='input_')
    argparser.add_argument('--output', dest='output')
    argparser.add_argument('--gold', action='store_true')
    argparser.add_argument('--fscore', action='store_true',
                           help='if given, compute f1 score')
    argparser.add_argument('--precision', action='store_true',
                           help='if given, compute per word precision')
    return argparser.parse_args()

class Tagger:

    def __init__(self, args):
        
        self.wt = serial.load(args.model)
        i2w = dict([(v, k) for k, v in self.wt.w2i.iteritems()])
        self.i2t = [t for t, i in sorted(self.wt.t2i.items(), 
            key=lambda x: x[1])] 
        self.input_ = args.input_ 
        self.output = (open(args.output, 'w') if args.output is not None
                else sys.stdout)
        self.init_scores(args)
    
    def tag_sen(self, window_words, window_feats):
        return self.wt.tag_sen(window_words,
                window_feats, debug=False)

    def tag(self):

        for sen_data in self.generate_sen_data():
            self.process_sen(sen_data)
   
    def process_sen(self, sen_data):
            w, f, to_print = sen_data
            if len(w) < 3:
                continue
            window_words, window_feats = WordTaggerDataset.process_sentence(
                    w, f, self.wt.window_size, self.wt.featurizer)
            result = self.tag_sen(window_words, window_feats)
            sen_data = self.update_sen_data(sen_data, result)
            self.write_result(sen_data)
            self.update_scores(to_print, result)
        self.write_scores()    
     
    def update_scores(self, to_print, result):
        pass
    
    def init_scores(self, args):
        pass

    def write_scores(self):
        pass

    def update_sen_data(self, sen_data, result):
        sen_data.append(list(result.flatten()))
        return sen_data

    def generate_sen_data(self):
       
        rc = RawCorpus(self.input_, self.wt.featurizer, w2i=self.wt.w2i,
                use_unknown=True)
        for sen in rc.read():
            w, f, orig_words = [list(t) for t in zip(*sen)]
            yield [w, f, orig_words]
    
    def write_result(self, sen_data):
        for item in izip(*(sen_data)):
            self.write_sen_result(item)
        self.output.write('\n')

    def write_sen_result(self, item):
        w, f, tp, res = item
        i = int(res)
        tag = self.i2t[i]
        self.output.write(u'{0}\t{1}\n'.format(tp, tag).encode('utf-8'))
        

class GoldLabeledTagger(Tagger):
    
    def init_scores(self, args):
        
        self.fscore = args.fscore
        self.precision = args.precision
        if self.fscore:
            self.count_f1 = True
            self.i2t = [t for t, i in sorted(self.wt.t2i.items(),
                key=lambda x: x[1])]
            self.counter = FScCounter(self.i2t, binary_input=False)
            self.counter.init_confusion_matrix()
        if self.precision:
            self.count_prec = True
            self.good = 0.0
            self.bad = 0.0
    
    def write_scores(self):
        if self.fscore:
            for l in self.counter.calculate_f():
                self.output.write('{0}\n'.format('\t'.join([str(s)
                    for s in l])))
        if self.precision: 
            self.output.write('per word accuracy: {0}\n'.format(
                self.good/(self.good + self.bad)))
    
    def process_sen(self, sen_data):
        
        self.super().process_sen
        self.write_result(sen_data)
        self.update_scores(to_print, result)


    def generate_sen_data(self):
        
        tc = TaggedCorpus(self.input_, self.wt.featurizer, w2i=self.wt.w2i,
                t2i=self.wt.t2i, use_unknown=True)
        for sen in tc.read():
            w, orig_t, f, orig_words = [list(t) for t in zip(*sen)]
            to_print = map(lambda x: u'{0}\t{1}'.format(x[0], self.i2t[x[1]]), 
                    izip(orig_words, orig_t))
            yield [w, f, to_print]
         
    def update_scores(self, to_print, result):
        gold = map(lambda x:self.wt.t2i[x.split('\t')[1]], to_print)
        result = map(lambda x:x[0], result)
        if self.fscore:
            self.counter.process_sen(gold, result)
        if self.precision:
            g = sum(map(lambda x: x[0]==x[1], zip(gold, result)))
            self.good += sum(map(lambda x: x[0]==x[1], zip(gold, result)))
            self.bad += len(gold) - g
        
def main():
    args = create_argparser()
    if not args.gold:
        a = Tagger(args)
    else:
        a = GoldLabeledTagger(args)
    a.tag()


if __name__ == '__main__':
    main()
