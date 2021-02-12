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
% ** normalizez() function normalizes the dataset
% ** neuron is the # of neuron in hidden layer
% ** minMSE is termination condition which represents minimum MSE traning
%    error should be achieved
% ** Win/Wout/bin/bout are model parameters. Ws are weights, Bs are biases
% ** ffnnetpredict() predicts the first input related output.
% ** rsquared() computes R2 and Adj.R2 metrics.
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

clc; clear; close all;
% generate an input
X = 0:0.01:5-0.01;

% generate an output
Y = 50*cosd(2*pi*20*X) + 70*cosd(2*pi*50*X);



% normalize data
[x_normalized,min_x,max_x] = normalizez(X); 
                                           
[y_normalized,min_y,max_y] = normalizez(Y); 

input    = x_normalized;
output   = y_normalized;

neuron   = 10;

minMSE = 1; 

[Win, Wout, bin, bout, nin, pred] = ffnnetwork(input, output, neuron, minMSE);
disp('Traning is over');
[prediction] = ffnnetpredict(input, Win, Wout, bin, bout);
figure();
plot(prediction,'LineWidth',3); hold on; plot(y_normalized,'LineWidth',3); 
legend('Prediction','Observation'); title('Prediction');
hold off;
[r2,adjr2]=rsquared(y_normalized,prediction);
disp(['R^2 Metric: ',num2str(r2)]);
disp(['Adj.R^2 Metric: ',num2str(adjr2)]);
figure();
plot(linspace(0.01,1,size(X,2)),linspace(0,1,size(X,2)),'LineWidth',3);
hold on;
plot(prediction,y_normalized,'o'); hold off;
legend('Observation','Prediction','Location','northwest'); title('Prediction vs Observation');
xlim([-.1 1.1]); ylim([-.1 1.1]);




