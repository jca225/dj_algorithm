import numpy as np
import math

class Transformer:
    pass

class Encoder:
    pass


class Decoder:
    pass



class Embedder:
    """
    ### Source:
        Bengio, Y., Ducharme, R., Vincent, P., & Jauvin, C. (2003). A neural probabilistic language model.
        *Journal of Machine Learning Research*, 3, 1137-1155, https://www.jmlr.org/papers/volume3/bengio03a/bengio03a.pdf
    """

    def __init__(self, V, m, h, n):
        
        """
        Parameters:
            V: Number of words in the vocabulary
            m: Number of features associated with each word
            h: Number of hidden units
            n: Context, based on the n-gram model. Developed by Mercer et. al. 1980
        """
        self.C = np.ones([V, m]) # Each word is associated with a column vector
        self.H = np.ones([h, m*(n-1)])
        self.d = np.ones([h, 1])
        self.b = np.ones([V, 1])
        self.U = np.ones([V, h])
        self.W = np.ones([V, m*(n-1)])

    def softmax(self, A):
        return np.apply_along_axis(lambda row: row/np.sum(row), 1, np.exp(A))
    
    def relu(self, A):
        a1 = A
        a1[A <= 0] = 0
        return a1
    
    def feedForward(self, X):
        """
        Forward phase (p. 1145)
        
        Parameters:
            X: "Word feature activation layer, which is the concatenation of the input word features 
                from the matrix C"
        """

        # Perform forward computation for hidden layer
        o = self.d + (self.H * X)
        a = np.apply_along_axis(lambda row: math.tanh(row), 1, o)
        y = self.b + (self.W * X) + (self.U * a)

        # Perform forward computation for output units in the ith block
        # Loop over j in the ith block

        pass
    def train(self, x_train, y_train, x_val, y_val, epochs, learning_rate=0.01, batchsize=64):

        pass
    pass



