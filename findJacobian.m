function J = findJacobian(netout, netin, Wout, X, nin, feature, nout)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%  
%  Alkim GOKCEN -                       Contact: alkim.gokcen@outlook.com,
%  FeedForwardNeuralNetwork             a.gokcen@baylanwatermeters.com,
%                                       y190207003@ogr.ikc.edu.tr
%  University of Izmir Katip Celebi, Institute of Applied Sciences, EEE
%  Baylan Watermeters, Research & Development Department
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

for i = 1: size(X,2)
    dWout = findGradWout(netout(:,i),netin(:,i));
    dbout = sum(findGradbout(netout(:,i)),2);
    dWin = findGradWin(netout(:,i),Wout,netin(:,i),X(:,i));
    dbin = sum(findGradbin(netout(:,i),netin(:,i),Wout),2);
    grad = vectorizationGradient(dWin,dWout,dbin,dbout,nin,feature,nout);
    J(i,:) = grad;
end


end


function y = findGradWout(netout,netin)
    y = -(hprimeOut(netout))*h(netin)';
end
function y = findGradbout(netout)
    y = -hprimeOut(netout);
end
function y = findGradWin(netout,Wout,netin,X)
    y = -((Wout'*(hprimeOut(netout)).*hprime(netin)))*X';
end
function y = findGradbin(netout,netin,Wout)
    y = -((Wout'*(hprimeOut(netout)).*hprime(netin)));
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