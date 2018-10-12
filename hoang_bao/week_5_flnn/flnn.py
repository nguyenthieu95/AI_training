import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from DE import DifferentialEvolution
from GA import  GeneticAlgorithm
import time
def update_weights(xfunc,weights,learning_rate,error):
    for i in range(len(weights)):
        weight_change = learning_rate*xfunc[i]*error
        weights[i] = weights[i] + weight_change
    return weights
def denormalize(A,max1,min1):
  #  
    B = np.zeros(len(A))
    for i in range(len(A)):
        B[i] = A[i]*(max1-min1) + min1
   # print("ket qua",np.subtract(A,B))
    return B
def normalize(A,max1,min1):
    # ma = max(A)
    # mi = min(A)
    t = max1-min1
    B = [(A[i]-min1)/t for i in range(len(A))]
    return B
#functional expansion
def CFLNN(x,degree):
    if degree == 0 :
        return 1
    elif degree == 1:
        return x
    else:
        return 2*x*CFLNN(x,degree-1) - CFLNN(x,degree-2)
def itself(x):
    return x
def elu(x, alpha=1):
    return np.where(x < 0, alpha * (np.exp(x) - 1), x)
def relu(x):
    return np.maximum(0, x)
def tanh(x):
    return np.tanh(x)
def sigmoid(x):
    return 1.0 / (1.0 + np.exp(-x))
def FLNN(X_train,Y_train):
    MAE = 0 
    RMSE = 0
    learning_rate = 0.025
    weights = np.random.uniform(-0.5,0.5,10)
    print("w:",weights)
    epochs = 200
    #1000 epochs , moi epocs se chay tung diem trong tap x_train va cap nhat trong so
    error = 0
    for i in range(epochs):
        SE = 0
        mx = []
        for train_index in range(len(X_train)):
            xfunc,output = feed_forward(X_train[train_index],weights)
            error = Y_train[train_index] - output 
            mx.append(error)
            SE = SE + np.square(error) 
            weights = update_weights(xfunc,weights,learning_rate,error)
            #print("error at train index",train_index," in epochs ",i,"is",error)  
            # 
      #  print("epoch: ",i," ---error : ",SE/len(X_train))    
        print("recal mse:",np.mean(np.square(mx)))
    print("best ",weights)
    return weights
def FLNN_DE(X_train,Y_train):
    MAE = 0 
    RMSE = 0
    problem_size = 10
    lower  = -0.5
    upper  = 0.5
    search_space  = [[lower,upper] for i in range(problem_size)]
    max_gens = 500
    pop_size = 15*problem_size 
    weightf = 0.5
    crossf = 0.5    
    DE = DifferentialEvolution(X_train,Y_train)
    best_weight =  DE.search(max_gens,search_space,pop_size,weightf,crossf)
    return best_weight[0]

def FLNN_GA(X_train,Y_train):
    problem_size = 10
    pop_size = 10*problem_size
    max_gens = 20
    search_space = [[-0.5,0.5] for _ in range(problem_size)]
    crossf = 0.9
    mutationf = 0.005
    
    GA = GeneticAlgorithm(problem_size,pop_size,max_gens,search_space,mutationf,crossf,X_train,Y_train)
    best = GA.search()
    return best[0]

def predict(X_test,weights):
    Y_predict = [relu(feed_forward(X_test[i],weights)[1]) for i in range(len(X_test))]
    return Y_predict

def feed_forward(train_data,weights):
    x = []
    #train_data[0] = cpu --> dua ra 5 dau ra khac nhau
    for i in range(5):
        x.append(CFLNN(train_data[0],i))
    for i in range(5):
        x.append(CFLNN(train_data[1],i))
    # print("x.weights: ",np.matmul(x,weights))
    return x,np.matmul(x,weights)



if __name__ == "__main__":
    file_name ='./data_resource_usage_5Minutes_6176858948.csv'
    df = pd.read_csv(file_name,header=None)
    # do vao cpu va mem
    cpu = list(df[3])
    mem = list(df[4])
    cpu_normalized = normalize(cpu,max(cpu),min(cpu))
    mem_normalized = normalize(mem,max(mem),min(mem))
    train_size = int(len(cpu)*0.8)

    X_train = []
    Y_train = []
    X_test = []
    Y_test = []
    Y_test = cpu[train_size:] # y_test thi lay luon cpu[train_size:] ko can chuan hoa
    for i in range(train_size-1):
        X_train.append([cpu_normalized[i],mem_normalized[i]])
        Y_train.append([cpu_normalized[i+1]])
    # print (X_train[0])
    # print (Y_train[0])
    # print (X_train[1])
    # print (Y_train[1])
    for i in range(train_size -1,len(cpu)-1):
        X_test.append([cpu_normalized[i],mem_normalized[i]])
        #Y_test.append([cpu_normalized[i+1]])
    start_time = time.clock()    
    weights  = FLNN_DE(X_train,Y_train)
    end_time = time.clock()
    print("execution time", end_time-start_time)
    Y_predict = predict(X_test,weights)
   # print("Y_predict",Y_predict,"len pre",len(Y_predict))
    Y_predict = denormalize(Y_predict,max(cpu),min(cpu))
    RMSE = np.sqrt(np.sum(np.square(Y_predict-Y_test))/len(Y_predict))
    MAE = np.mean(np.abs(Y_predict-Y_test))
    MAE2= np.sum(np.abs(np.subtract(Y_predict,Y_test)))/len(Y_predict)
    str1 = 'RMSE' + str(RMSE)
    str2 = 'MAE' + str(MAE)
    with open("./result/de_flnn_res_ram_200_epoch_05_05.csv","w") as f:
        for i in range(len(Y_predict)):
            f.write(str(Y_predict[i])+","+str(Y_test[i])+"\n")
        f.write(str(RMSE)+","+str(MAE))
    
    #str3 = 'MAE2' + str(MAE2)
    plt.plot(Y_test,color='b')
    plt.plot(Y_predict,color='r')
    
    plt.text(0, 5, str1)
    plt.text(0,6,str2)
    #plt.text(0,2,str3)
    plt.legend(['Actual','Predict'],loc='best')
    plt.show()
