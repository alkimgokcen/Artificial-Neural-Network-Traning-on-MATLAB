%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%  
%  Alkim GOKCEN -                       Contact: alkim.gokcen@outlook.com,
%  FeedForwardNeuralNetwork             a.gokcen@baylanwatermeters.com,
%                                       y190207003@ogr.ikc.edu.tr
%  University of Izmir Katip Celebi, Institute of Applied Sciences, EEE
%  Baylan Watermeters, Research & Development Department
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

function [Win,Wout,bin,bout] = devecotrization(vector,N,numout,feature)

    Win = reshape(vector(1:feature*N), [N, feature]);
    vector = vector(feature*N+1:end);

    bin = reshape(vector(1:N), [N, 1]);
    vector = vector(N+1:end);
    
    Wout = reshape(vector(1:numout*N), [numout, N]);
    vector = vector((numout*N)+1:end);
    
    bout = reshape(vector(1:end), [numout, 1]);

end