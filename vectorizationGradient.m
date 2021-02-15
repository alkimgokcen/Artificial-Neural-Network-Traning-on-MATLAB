function [y] = vectorizationGradient(gradWin,gradWout,gradbin,gradbout,N,feature,numout)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%  
%  Alkim GOKCEN -                       Contact: alkim.gokcen@outlook.com,
%  FeedForwardNeuralNetwork             a.gokcen@baylanwatermeters.com,
%                                       y190207003@ogr.ikc.edu.tr
%  University of Izmir Katip Celebi, Institute of Applied Sciences, EEE
%  Baylan Watermeters, Research & Development Department
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    
    y = [];
    
    y = [y; reshape(gradWin, [N*feature,1])];
    
    y = [y; reshape(gradbin, [N, 1])];
    
    y = [y; reshape(gradWout,[N*numout, 1])];
    
    y = [y; reshape(gradbout,[numout, 1])];
    
end