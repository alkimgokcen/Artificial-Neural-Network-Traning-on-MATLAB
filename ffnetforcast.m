%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%  
%  Alkim GOKCEN -                       Contact: alkim.gokcen@outlook.com,
%  FeedForwardNeuralNetwork             a.gokcen@baylanwatermeters.com,
%                                       y190207003@ogr.ikc.edu.tr
%  University of Izmir Katip Celebi, Institute of Applied Sciences, EEE
%  Baylan Watermeters, Research & Development Department
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Syntax ------------------------------------------------------------------
% ** X is a matrix in size of MxN where M is the # of feature,N is the
%    % of sample
% ** Win represents weights of input layer
% ** Wout represents weights of output layer
% ** bin represents bias values hidden layer neurons
% ** bout represents bias value of output layer neurons
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


function [prediction] = ffnetforcast(X, Win, Wout, bin, bout)
netin = Win*X + bin;
netout = Wout*h(netin) + bout;
prediction = hOut(netout);
function y = h(x)
    y = tansig(x);
end
function y = hOut(x)
    y = x;
end
function y = hprime(x)
    y = (1-tansig(x).^2);
end
end