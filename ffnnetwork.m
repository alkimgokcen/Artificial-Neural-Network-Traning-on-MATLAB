%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%  
%  Alkim GOKCEN -                       Contact: alkim.gokcen@outlook.com,
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
% ** minMSE is minimum traning error shoudl be achieved
% ** feature is # of feature
% ** nin is # of neuron
% ** nout is # of output
% ** iter is the epoch
% ** uK is the hessian scaler
% ** uscale,min,max are hessian scaler determination parameters
% ** findJacobian() computes jacobian
% ** vectorizationGradient() vectorizes the matrix
% ** devecotrization() performs devecotrization to vector
% ** pk, zk, param are the cendidate steps (pk,zk) and coefficient vector.
% ** costx is the traning cost.
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
function [Win, Wout, bin, bout, nin, pred] = ffnnetwork(input, output, neuron, minMSE)
X = input;
Y = output;
[feature, ~] = size(X); % sample is # of data, feature is # of input
[nout,~] = size(Y); % outcol is # of output
nin = neuron; % number of neuron

    Win  = rand(nin, feature); % input layer weight matrix
    bin  = rand(nin, 1); % input layer bias matrix
    Wout = rand(nout, nin); %output layer weight matrix
    bout = rand(nout, 1);  %output layer bias matrix

[~, error,netout,netin] = yprediction(X,Win,bin,Wout,bout,Y);
iter = 0;
uK = 1.01;
uscale = 10;
umin = 1e-10;
umax = 1e+10;
costx = 0.5*sum(error.^2);
loop1 = 1;

while loop1
    iter = iter +1;
    param = vectorizationGradient(Win,Wout,bin,bout,nin,feature,nout);
    J = findJacobian(netout, netin, Wout, X, nin, feature, nout);
    
    loop2 = 1;
    
    while loop2
        
        pk = -inv(J'*J + uK*eye(size(J,2),size(J,2)))*J'*error';
        zk = param + pk;
        [Win,Wout,bin,bout] = devecotrization(zk,nin,nout,feature);
        [pred, error,netout,netin] = yprediction(X,Win,bin,Wout,bout,Y);
        costz = 0.5*sum(error.^2); 
        
        if costz<costx
            [~,sk,~,~,~,~] = goldenSection(LowerLimit,UpperLimit,1e-10,Y,nin,param,pk,feature,X);
            % sk = newtonRhapson(param,pk,X,Y,nin,feature);
            param = param + 0.001*pk;
            [Win,Wout,bin,bout] = devecotrization(zk,nin,nout,feature);
            [~, error,netout,netin] = yprediction(X,Win,bin,Wout,bout,Y);
            costx = sum(error.^2);
            uK = uK/uscale;
            loop2 = 0;
            clc;
            disp('Cost');
            disp(costx);
        else
            uK = uK*uscale;
        end
        
        
        if(uK<umin)||(umax<uK)
            loop1 = 0;
            loop2 = 0;
        end
    end
    if costx<minMSE
        loop1 = 0;
    end
end

end
function y = h(x)
    y = tansig(x);
end
function y = hprime(x)
    y = (1-tansig(x).^2);
end
function y = hOut(x)
    y = x;
end
function y = hprimeOut(x)
    y = ones(size(x));
end
function [ypred,error,netout,netin] = yprediction(X,Win,bin,Wout,bout,Y)
netin = Win*X + bin;
netout = Wout*h(netin) + bout;
ypred = hOut(netout);
error = Y-ypred;
end

