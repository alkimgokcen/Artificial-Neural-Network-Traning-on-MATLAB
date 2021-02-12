function [r2,adjr2]=rsquared(ydata,yestimation)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%  
%  Alkim GOKCEN -                       Contact: alkim.gokcen@outlook.com,
%  FeedForwardNeuralNetwork             a.gokcen@baylanwatermeters.com,
%                                       y190207003@ogr.ikc.edu.tr
%  University of Izmir Katip Celebi, Institute of Applied Sciences, EEE
%  Baylan Watermeters, Research & Development Department
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

    SSres=sum( (ydata-yestimation).^2 );
    SStot=sum( (ydata-mean(ydata)).^2 );
    
    r2=1-SSres/SStot;
    
    n = length(yestimation);
    k = 8;
    
    adjr2 = 1 - (  (1-r2)*(n-1)/( n-k-1 )  );

end