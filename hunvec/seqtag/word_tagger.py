from math import sqrt


from pylearn2.models.mlp import MLP, CompositeLayer, Tanh, Linear
from pylearn2.space import CompositeSpace, IndexSpace
from pylearn2.sandbox.nlp.models.mlp import ProjectionLayer


class WordTaggerNetwork(MLP):
    def __init__(self, vocab_size, window_size, total_feats, feat_num,
                 hdims, edim, n_classes):
        self.vocab_size = vocab_size
        self.ws = window_size
        self.total_feats = total_feats
        self.feat_num = feat_num
        self.hdims = hdims
        self.edim = edim
        self.n_classes = n_classes
        layers, input_space = self.create_network()
        input_source = ('words', 'features')
        super(WordTaggerNetwork, self).__init__(layers=layers,
                                                input_space=input_space,
                                                input_source=input_source)

    def create_network(self):
        # words and features
        input_space = CompositeSpace([
            IndexSpace(max_labels=self.vocab_size, dim=self.ws),
            IndexSpace(max_labels=self.total_feats, dim=self.feat_num)
        ])

        input_ = CompositeLayer(
            layer_name='input',
            layers=[
                ProjectionLayer(layer_name='words', dim=self.edim, irange=.1),
                ProjectionLayer(layer_name='feats', dim=self.edim, irange=.1),
            ],
            inputs_to_layers={0: [0], 1: [1]}
        )

        # for parameter settings, see Remark 7 (Tricks) in NLP from scratch
        hiddens = []
        for i, hdim in enumerate(self.hdims):
            h = Tanh(layer_name='h{}'.format(i), dim=hdim,
                     istdev=1./sqrt(hdim), W_lr_scale=1./hdim)
            hiddens.append(h)

        output = Linear(layer_name='tagger_out',
                        istdev=1. / sqrt(self.n_classes),
                        dim=self.n_classes, W_lr_scale=1./self.n_classes)

        return [input_] + hiddens + [output], input_space