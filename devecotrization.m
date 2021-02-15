%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%  
%  Alkim GOKCEN -                       Contact: alkim.gokcen@outlook.com,
%  FeedForwardNeuralNetwork             a.gokcen@baylanwatermeters.com,
%                                       y190207003@ogr.ikc.edu.tr
%  University of Izmir Katip Celebi, Institute of Applied Sciences, EEE
%  Baylan Watermeters, Research & Development Department
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

function [Win,Wout,bin,bout] = devectorization(vector,N,numout,feature)
    counter = 1;
    for i=1:feature
        for j=1:N
            Win(j,i) = vector(counter);
            counter = counter+1;
        end
    end
    
    for i=1:N
        bin(i,1) = vector(counter);
        counter = counter+1;
    end
    
    for i=1:numout
        for j=1:N
            Wout(i,j) = vector(counter);
            counter = counter+1;
        end
    end
    
    for i=1:numout
        bout(i,1) = vector(counter);
        counter=counter+1;
    end


end
