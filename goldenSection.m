function [t1,t2,ft1,ft2,N,tolerance] = goldenSection(tLowerLimit,tUpperLimit,tFinalPoint,y,s,tk,pk,R,t)
%% Alkim GOKCEN
%  140403003
%  Electrical Electronics Engineering
%  Introduction to Artifical Neural Networks
%  Class Assignment - 2
%  15/10/2018
%%      
    tao = 0.38197;    
    tolerance = tFinalPoint/(tUpperLimit - tLowerLimit);    
    N = floor(-2.078*log(tolerance));
    t1 = tLowerLimit + tao*(tUpperLimit - tLowerLimit);
    [Win,Wout,bin,bout] = devecotrization(tk+t1*pk,s,size(y,1),R);
    [prediction] = ffnnetpredict(t, Win, Wout, bin, bout);
    ft1 = 0.5*(((y-prediction).^2));
    t2 = tUpperLimit - tao*(tUpperLimit - tLowerLimit);
    [Win,Wout,bin,bout] = devecotrization(tk+t2*pk,s,size(y,1),R);
    [prediction] = ffnnetpredict(t, Win, Wout, bin, bout);
    ft2 = 0.5*(((y-prediction).^2));
    ft1 = sum(ft1);
    ft2 = sum(ft2);
    k = 0;    
    for i=1:N    
     if k<N        
        if ft1>ft2            
            tLowerLimit = t1;            
            t1 = t2;            
            ft1 = ft2;            
            t2 = tUpperLimit - tao*(tUpperLimit - tLowerLimit); 
            [Win,Wout,bin,bout] = devecotrization(tk+t2*pk,s,size(y,1),R);
            [prediction] = ffnnetpredict(t, Win, Wout, bin, bout);
            ft2 = 0.5*(((y-prediction).^2));
            ft2 = sum(ft2);
            k = k + 1;                       
        elseif ft1<ft2            
            tUpperLimit = t2;
            t2 = t1;           
            ft2 = ft1;           
            t1 = tLowerLimit + tao*(tUpperLimit - tLowerLimit);
            [Win,Wout,bin,bout] = devecotrization(tk+t1*pk,s,size(y,1),R);
            [prediction] = ffnnetpredict(t, Win, Wout, bin, bout);
            ft1 = 0.5*(((y-prediction).^2));
            ft1 = sum(ft1);
            k = k + 1;          
        end        
     else       
        break;
     end  
    end 
end