from util import *
import sys
import matplotlib.pyplot as plt
plt.ion()

def InitNN(num_inputs, num_hiddens, num_outputs):
    """Initializes NN parameters."""
    W1 = 0.01 * np.random.randn(num_inputs, num_hiddens)
    W2 = 0.01 * np.random.randn(num_hiddens, num_outputs)
    b1 = np.zeros((num_hiddens, 1))
    b2 = np.zeros((num_outputs, 1))
    return W1, W2, b1, b2

def TrainNN(num_hiddens, eps, momentum, num_epochs, CE=0):
    """Trains a single hidden layer NN.

    Inputs:
      num_hiddens: NUmber of hidden units.
      eps: Learning rate.
      momentum: Momentum.
      num_epochs: Number of epochs to run training for.

    Returns:
      W1: First layer weights.
      W2: Second layer weights.
      b1: Hidden layer bias.
      b2: Output layer bias.
      train_error: Training error at at epoch.
      valid_error: Validation error at at epoch.
    """

    inputs_train, inputs_valid, inputs_test, target_train, target_valid, target_test = LoadData('digits.npz')
    W1, W2, b1, b2 = InitNN(inputs_train.shape[0], num_hiddens, target_train.shape[0])
    dW1 = np.zeros(W1.shape)
    dW2 = np.zeros(W2.shape)
    db1 = np.zeros(b1.shape)
    db2 = np.zeros(b2.shape)
    train_error = []
    valid_error = []
    train_MCE_arr = []
    valid_MCE_arr = []
    num_train_cases = inputs_train.shape[1]
    for epoch in xrange(num_epochs):
        # Forward prop
        h_input = np.dot(W1.T, inputs_train) + b1  # Input to hidden layer.
        h_output = 1 / (1 + np.exp(-h_input))  # Output of hidden layer.
        logit = np.dot(W2.T, h_output) + b2  # Input to output layer.
        prediction = 1 / (1 + np.exp(-logit))  # Output prediction.

        # Compute cross entropy
        train_CE = -np.mean(target_train * np.log(prediction) + (1 - target_train) * np.log(1 - prediction))

        # for section 2.2
        train_MCE = incorrect_ratio(prediction, target_train)
        # Compute deriv
        dEbydlogit = prediction - target_train

        # Backprop
        dEbydh_output = np.dot(W2, dEbydlogit)
        dEbydh_input = dEbydh_output * h_output * (1 - h_output)

        # Gradients for weights and biases.
        dEbydW2 = np.dot(h_output, dEbydlogit.T)
        dEbydb2 = np.sum(dEbydlogit, axis=1).reshape(-1, 1)
        dEbydW1 = np.dot(inputs_train, dEbydh_input.T)
        dEbydb1 = np.sum(dEbydh_input, axis=1).reshape(-1, 1)

        #%%%% Update the weights at the end of the epoch %%%%%%
        dW1 = momentum * dW1 - (eps / num_train_cases) * dEbydW1
        dW2 = momentum * dW2 - (eps / num_train_cases) * dEbydW2
        db1 = momentum * db1 - (eps / num_train_cases) * dEbydb1
        db2 = momentum * db2 - (eps / num_train_cases) * dEbydb2

        W1 = W1 + dW1
        W2 = W2 + dW2
        b1 = b1 + db1
        b2 = b2 + db2

        valid_CE = Evaluate(inputs_valid, target_valid, W1, W2, b1, b2)

        # for section 2.2
        valid_MCE = EvaluMCE(inputs_valid, target_valid, W1, W2, b1, b2)

        train_error.append(train_CE)
        valid_error.append(valid_CE)

        # for section 2.2

        train_MCE_arr.append(train_MCE)
        valid_MCE_arr.append(valid_MCE)
        if CE == 1:
            sys.stdout.write('\rStep %d Train CE %.5f Validation CE %.5f' % (epoch, train_CE, valid_CE))
            sys.stdout.flush()
            if (epoch % 100 == 0):
                sys.stdout.write('\n')
        if CE == 2:
            sys.stdout.write('\rStep %d Train MCE %.5f Validation MCE %.5f' % (epoch, train_MCE, valid_MCE))
            sys.stdout.flush()
            if (epoch % 100 == 0):
                sys.stdout.write('\n')



    sys.stdout.write('\n')
    if CE == 1:
        final_train_error = Evaluate(inputs_train, target_train, W1, W2, b1, b2)
        final_valid_error = Evaluate(inputs_valid, target_valid, W1, W2, b1, b2)
        final_test_error = Evaluate(inputs_test, target_test, W1, W2, b1, b2)
        print 'Error: Train %.5f Validation %.5f Test %.5f' % (final_train_error, final_valid_error, final_test_error)
    if CE == 2:
        final_train_MCE = EvaluMCE(inputs_train, target_train, W1, W2, b1, b2)
        final_valid_MCE = EvaluMCE(inputs_valid, target_valid, W1, W2, b1, b2)
        final_test_MCE = EvaluMCE(inputs_test, target_test, W1, W2, b1, b2)
        print 'MCE: Train %.5f Validation %.5f Test %.5f' % (final_train_MCE, final_valid_MCE, final_test_MCE)
    return W1, W2, b1, b2, train_error, valid_error, train_MCE_arr, valid_MCE_arr

def Evaluate(inputs, target, W1, W2, b1, b2):
    """Evaluates the model on inputs and target."""
    h_input = np.dot(W1.T, inputs) + b1  # Input to hidden layer.
    h_output = 1 / (1 + np.exp(-h_input))  # Output of hidden layer.
    logit = np.dot(W2.T, h_output) + b2  # Input to output layer.
    prediction = 1 / (1 + np.exp(-logit))  # Output prediction.
    CE = -np.mean(target * np.log(prediction) + (1 - target) * np.log(1 - prediction))
    return CE


#added for 2.2

def incorrect_ratio(predict,tars):
    incorrect = 0
    diff = predict - tars
    for d in diff[0]:
        if np.abs(d) >= 0.5:
            incorrect += 1

    return (float(incorrect) / float(tars.size)) * 100

#added for 2.2

def EvaluMCE(inputs, target, W1, W2, b1, b2):
    """Evaluates the model on inputs and targe"""
    h_input = np.dot(W1.T, inputs) + b1  # Input to hidden layer.
    h_output = 1 / (1 + np.exp(-h_input))  # Output of hidden layer.
    logit = np.dot(W2.T, h_output) + b2  # Input to output layer.
    prediction = 1 / (1 + np.exp(-logit))  # Output prediction.

    return incorrect_ratio(prediction, target)



def DisplayErrorPlot(train_error, valid_error, y_lable='', ctitle=''):

    plt.figure(1)
    plt.clf()
    plt.plot(range(len(train_error)), train_error, 'b', label='Train')
    plt.plot(range(len(valid_error)), valid_error, 'g', label='Validation')
    plt.xlabel('Epochs')

    plt.ylabel(y_lable)
    #plt.ylim([min(valid_error) - 10, max(valid_error) + 10])
    plt.title(ctitle)
    plt.legend()
    #plt.show()
    plt.draw()
    raw_input('Press Enter to exit.')

def SaveModel(modelfile, W1, W2, b1, b2, train_error, valid_error):
    """Saves the model to a numpy file."""
    model = {'W1': W1, 'W2' : W2, 'b1' : b1, 'b2' : b2,
             'train_error' : train_error, 'valid_error' : valid_error}
    print 'Writing model to %s' % modelfile
    np.savez(modelfile, **model)

def LoadModel(modelfile):
    """Loads model from numpy file."""
    model = np.load(modelfile)
    return model['W1'], model['W2'], model['b1'], model['b2'], model['train_error'], model['valid_error']




def main():
    print""


if __name__ == '__main__':
    main()
