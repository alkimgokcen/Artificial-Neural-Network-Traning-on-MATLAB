%% This code is to implement the Newton-Rhapson one dimensional optimization
% to be able to find the derivative of purpose function with respect to sk
% by using the numerical approximation of differentiation


function sk = newtonRhapson(x0,pk,t,y,s,R)
xk = x0;
sk = 0.01;     % initial sk
loop1 = 1;
tolerance = 1e-3;
tolerance_change = 1e-3;
stepSize = 1e-6;    
while loop1
    [Win,Wout,bin,bout] = devecotrization(xk+sk*pk,s,size(y,1),R);
    [prediction] = ffnnetpredict(t, Win, Wout, bin, bout);
    f = 0.5*(((y-prediction).^2));
    df = diff(f)./stepSize;
    ddf = diff(df)./stepSize;
    df = sum(df); ddf = sum(ddf);
    deltaXk = - df/ddf;     % update parameter is found
    sk = sk + deltaXk;                  % update rule
    df_old = df;
    
     [Win,Wout,bin,bout] = devecotrization(xk+sk*pk,s,size(y,1),R);
    [prediction] = ffnnetpredict(t, Win, Wout, bin, bout);
    f = 0.5*(((y-prediction).^2));
    
    df = diff(f)./stepSize;
    df = sum(df);
if df < tolerance || df - df_old < tolerance_change || deltaXk<tolerance
    loop1 = 0;
end
end
end