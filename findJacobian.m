function [J] = findJacobian(Win,bHid,Wout,s,R,t)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%  
%  Alkim GOKCEN -                       Contact: alkim.gokcen@outlook.com,
%  FeedForwardNeuralNetwork             a.gokcen@baylanwatermeters.com,
%                                       y190207003@ogr.ikc.edu.tr
%  University of Izmir Katip Celebi, Institute of Applied Sciences, EEE
%  Baylan Watermeters, Research & Development Department
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Syntax ------------------------------------------------------------------
% ** Win, bHid, Wout => necessary weights and bias to compute jacobian
% ** s, R => # of neurons and features, T => represents the input matrix.
% ** J is the jacobian matrix.
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%



for i = 1:length(t)
    for j=1:s*R
        k = mod(j-1,s)+1;
        m = fix((j-1)/s)+1;
        J(i,j) = -Wout(1,k)*t(m,i)*(dh(Win(k,:)*t(:,i)+bHid(k,1)));
    end
    for j=(s*R+1):(s*R+s)
        J(i,j) = -Wout(1,j-s*R)*(dh(Win(j-s*R,:)*t(:,i)+bHid(j-s*R,1)));
    end
    for j=(s*(R+1)+1):(s*(R+2))
        J(i,j) = -h(Win(j-(R+1)*s,:)*t(:,i)+bHid(j-(R+1)*s,1));
    end
    for j=((s*(R+2)+1)):((s*(R+2)+1))
        J(i,j) = -1;
    end
end
end
function y = h(x)
    y = tansig(x);
end
function y = dh(x)
    y = (1-tansig(x).^2);
end
