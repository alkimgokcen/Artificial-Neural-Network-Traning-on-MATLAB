%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%  
%  Alkim GOKCEN - PhD.                  Contact: alkim.gokcen@outlook.com,
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

clc; clear; close all;
% generate an input
X = 0:0.01:5-0.01;

% generate an output
Y = 50*cosd(2*pi*20*X) + 70*cosd(2*pi*50*X);



% normalize data
[x_normalized,min_x,max_x] = normalizez(X); % If M>1;
                                           % Normalize each row individualy
                                           
[y_normalized,min_y,max_y] = normalizez(Y); % If k>1;
                                           % Normalize each row individualy
input    = x_normalized;
output   = y_normalized;
neuron   = 60;
maxiter  = 100;

[Win, Wout, bin, bout, nin, pred] = ffnnetwork(input, output, neuron, maxiter);
[prediction] = ffnetforcast(input, Win, Wout, bin, bout);

plot(prediction); hold on; plot(y_normalized); 
legend('Prediction','Observation');




