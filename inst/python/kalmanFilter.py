import numpy as np
from numpy.linalg import multi_dot	

class KalmanFilter(object):
    """docstring for KalmanFilter"""

    def __init__(self, initial_state):
        # Define sampling time
        self.dt = 1

        # Define the  control input variables
        self.u = np.matrix([[0],[0]])

        # Intial State
        self.x = np.matrix([[initial_state[0]],[initial_state[1]],[0],[0]])

        # Define the State Transition Matrix A
        self.A = np.matrix([[1, 0, self.dt, 0],
                            [0, 1, 0, self.dt],
                            [0, 0, 1, 0],
                            [0, 0, 0, 1]])

        # Define the Control Input Matrix B
        self.B = np.matrix([[(self.dt**2)/2, 0],
                            [0,(self.dt**2)/2],
                            [self.dt,0],
                            [0,self.dt]])

        # Define Measurement Mapping Matrix
        self.H = np.matrix([[1, 0, 0, 0],
                            [0, 1, 0, 0]])

        #Initial Process Noise Covariance
        self.q = np.matrix([[2.5,0],
                           [0, 3.1]])
        
        self.Q = np.dot(self.B,np.dot(self.q,self.B.T))

        #Initial Measurement Noise Covariance
        self.R = np.matrix([[2.5,0],
                           [0, 3.1]])

        #Initial Covariance Matrix
        self.P = self.Q

    """Predict function which predicst next state based on previous state"""
    def predict(self):
       
        # Update time state
        #x_k =Ax_(k-1) + Bu_(k-1)
        self.x = np.dot(self.A, self.x) + np.dot(self.B, self.u)

        # Calculate error covariance
        # P= A*P*A' + Q 
        self.P = np.dot(np.dot(self.A, self.P), self.A.T) + self.Q
        
        temp = np.asarray(self.x)
        return temp[0], temp[1]

    """Correct function which correct the states based on measurements"""
    def correct(self, currentMeasurement):
       
        # S = H*P*H'+R
        S = np.dot(self.H, np.dot(self.P, self.H.T)) + self.R

        # Calculate the Kalman Gain
        # K = P * H'* inv(H*P*H'+R)
        K = np.dot(np.dot(self.P, self.H.T), np.linalg.inv(S))

        self.x = np.round(self.x + np.dot(K, (currentMeasurement - np.dot(self.H, self.x))))

        I = np.eye(self.H.shape[1])

        # Update error covariance matrix
        self.P = (I - (K * self.H)) * self.P 
        
        temp = np.asarray(self.x)
        return temp[0], temp[1]

