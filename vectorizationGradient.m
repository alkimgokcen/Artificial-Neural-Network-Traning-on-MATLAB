function [y] = vectorizationGradient(gradWin,gradWout,gradbin,gradbout,N,feature,numout)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%  
%  Alkim GOKCEN -                       Contact: alkim.gokcen@outlook.com,
%  FeedForwardNeuralNetwork             a.gokcen@baylanwatermeters.com,
%                                       y190207003@ogr.ikc.edu.tr
%  University of Izmir Katip Celebi, Institute of Applied Sciences, EEE
%  Baylan Watermeters, Research & Development Department
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    counter = 1;
    for i = 1:feature
        for j=1:N
            y(counter,1) = gradWin(j,i);
            counter = counter+1;
        end
    end
    
    for i=1:N
        y(counter,1) = gradbin(i);
        counter = counter+1;
    end
    
    for i=1:numout
        for j=1:N
            y(counter,1) = gradWout(i,j);
            counter = counter+1;
        end
    end
    
    for i=1:numout
        y(counter,1) = gradbout(i);
        counter=counter+1;
    end
    
    
end