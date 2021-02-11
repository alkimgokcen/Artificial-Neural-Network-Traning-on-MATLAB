%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%  
%  Alkim GOKCEN -                       Contact: alkim.gokcen@outlook.com,
%  FeedForwardNeuralNetwork             a.gokcen@baylanwatermeters.com,
%                                       y190207003@ogr.ikc.edu.tr
%  University of Izmir Katip Celebi, Institute of Applied Sciences, EEE
%  Baylan Watermeters, Research & Development Department
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Syntax ------------------------------------------------------------------
% ** input is a matrix in size of MxN where M is the # of feature,N is the#
%    of sample
% ** output is a matrix in size of KxN where K is the # of outputs, N is
%    the #of sample
% ** neuron is a scalar value that represents the # of hiddenLayer neurons
% ** learningRate represents the LR for gradient descent algorithm
% ** maxIter represent the stopping criteria for gradient descent
% ** onOff if 1, means online learning else 0, means offline learning
% ** coefs is a matrix like [Win,Wout,bin,bout]
% ** Win represents weights of input layer
% ** Wout represents weights of output layer
% ** bin represents bias values hidden layer neurons
% ** bout represents bias value of output layer neurons
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
function [Win, Wout, bin, bout, nin, pred] = ffnnetwork(input, output, neuron, maxiter)
X = input;
Y = output;
[feature, ~] = size(X); % sample is # of data, feature is # of input
[nout,~] = size(Y); % outcol is # of output
nin = neuron; % number of neuron

    Win  = rand(nin, feature); % input layer weight matrix
    bin  = rand(nin, 1); % input layer bias matrix
    Wout = rand(nout, nin); %output layer weight matrix
    bout = rand(nout, 1);  %output layer bias matrix

[~, error,netout,netin] = yprediction(X,Win,bin,Wout,bout,Y);
iter = 0;
V=0;
while maxiter>iter
iter = iter +1;
param = vectorizationGradient(Win,Wout,bin,bout,nin,feature,nout);
[J] = findJacobian(Win,bin,Wout,nin,feature,input);
dWout = findGradWout(error,netout,netin);
dbout = sum(findGradbout(error,netout),2);
dWin = findGradWin(error,netout,Wout,netin,X);
dbin = sum(findGradbin(error,netout,netin,Wout),2);
% 
grad = vectorizationGradient(dWin,dWout,dbin,dbout,nin,feature,nout);
hessian  = 2*(J')*J;

% newton method
param = param - pinv(hessian)*grad;

% gradient descent
% param = param - 0.000001*grad; % optional

[Win,Wout,bin,bout] = devecotrization(param,nin,nout,feature);
[pred, error,netout,netin] = yprediction(X,Win,bin,Wout,bout,Y);
clc;
disp('Error^2 norm');
disp(norm(error));
end
function y = h(x)
    y = tansig(x);
end
function y = hprime(x)
    y = (1-tansig(x).^2);
end
function y = hOut(x)
    y = x;
end
function y = hprimeOut(x)
    y = ones(size(x));
end
function [ypred,error,netout,netin] = yprediction(X,Win,bin,Wout,bout,Y)
netin = Win*X + bin;
netout = Wout*h(netin) + bout;
ypred = hOut(netout);
error = Y-ypred;
end
function y = findGradWout(error,netout,netin)
    y = -(error.*hprimeOut(netout))*h(netin)';
end
function y = findGradbout(error,netout)
    y = -error.*hprimeOut(netout);
end
function y = findGradWin(error,netout,Wout,netin,X)
    y = -((Wout'*(error.*hprimeOut(netout)).*hprime(netin)))*X';
end
function y = findGradbin(error,netout,netin,Wout)
    y = -((Wout'*(error.*hprimeOut(netout)).*hprime(netin)));
end
end
