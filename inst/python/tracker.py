import numpy as np 
#from kalmanFilter import KalmanFilter
from scipy.optimize import linear_sum_assignment
from collections import deque
import math

class Tracks(object):
	"""docstring for Tracks"""
	def __init__(self, detection, trackId, initial_state):
		self.KF = KalmanFilter(initial_state)
		self.KF.predict()
		self.KF.correct(np.matrix(detection).reshape(2,1))
		self.trace = deque(maxlen=20)
		self.prediction = detection.reshape(1,2)
		self.trackId = trackId
		self.skipped_frames = 0
		correction = self.KF.correct(np.matrix(detection).reshape(2,1))
		self.correction = np.array(correction).reshape(1,2)

	def predict(self,detection):
		self.prediction = np.array(self.KF.predict()).reshape(1,2)
		#self.KF.correct(np.matrix(detection).reshape(2,1))

	def correct(self,detection):
		correction = self.KF.correct(np.matrix(detection).reshape(2,1))
		self.correction = np.array(correction).reshape(1,2)
	
	def get_orientation(self):
		if(len(self.trace)>1):
			x0 = self.trace[-2][0,0]
			y0 = self.trace[-2][0,1]
		else:
			x0 = 0
			y0 = 0
		x1 = self.trace[-1][0,0]
		y1 = self.trace[-1][0,1]
		orientation = math.atan2(y0-y1,x1-x0)
		if(orientation<0):
			orientation = 2*np.pi + orientation
		self.orientation = orientation
		return self.orientation

	def get_position(self):
		x = self.trace[-1][0,0]
		y = self.trace[-1][0,1]
		return x, y

	def get_velocity(self):
		if(len(self.trace)>1):
			x0 = self.trace[-2][0,0]
			y0 = self.trace[-2][0,1]
		else:
			x0 = self.trace[-1][0,0]
			y0 = self.trace[-1][0,1]
		x1 = self.trace[-1][0,0]
		y1 = self.trace[-1][0,1]
		dx = x1-x0
		dy = y0-y1
		vel = math.sqrt(dx**2+dy**2)
		return vel

class Tracker(object):
	"""docstring for Tracker"""
	def __init__(self, dist_threshold, max_frame_skipped, max_fish):
		self.dist_threshold = dist_threshold
		self.max_frame_skipped = max_frame_skipped
		self.max_fish = max_fish
		self.trackId = 0
		self.tracks = []
	
	def fill(self,x):
		a = np.empty([1,self.max_fish], float)
		a.fill(np.nan)
		len_x = x.shape[1]
		a[0,0:len_x] = x
		return a
 
	def get_positions(self):
		list_x=[]
		list_y=[]
		for i in range(len(self.tracks)):
			x, y = self.tracks[i].get_position()
			list_x.append(x)
			list_y.append(y)
		list_x = np.array([list_x])
		list_y = np.array([list_y])
		list_x = self.fill(list_x)
		list_y = self.fill(list_y)
		return list_x, list_y

	def get_velocitys(self):
		list_vel=[]
		for i in range(len(self.tracks)):
			vel = self.tracks[i].get_velocity()
			vel=vel/30
			list_vel.append(vel)
		list_vel = np.array([list_vel])
		list_vel = self.fill(list_vel)
		return list_vel
	
	def get_metrics(self):
		x, y = self.get_positions()
		vel = self.get_velocitys()
		return x, y, vel
 
	def update(self, detections):
		if len(self.tracks) == 0:
			for i in range(detections.shape[0]):
				track = Tracks(detections[i], self.trackId, detections[i])
				self.trackId +=1
				self.tracks.append(track)

		N = len(self.tracks)
		M = len(detections)
		cost = []
		for i in range(N):
			diff = np.linalg.norm(self.tracks[i].prediction - detections.reshape(-1,2), axis=1)
			cost.append(diff)

		cost = np.array(cost)
		row, col = linear_sum_assignment(cost)
		assignment = [-1]*N
		for i in range(len(row)):
			assignment[row[i]] = col[i]

		# Identify tracks with no assignment, if any
		un_assigned_tracks = []
		for i in range(len(assignment)):
			if (assignment[i] != -1):
				# check for cost distance threshold.
				# If cost is very high then un_assign (delete) the track
				if (cost[i][assignment[i]] > self.dist_threshold):
					assignment[i] = -1
					un_assigned_tracks.append(i)
				pass
			else:
				self.tracks[i].skipped_frames += 1
				#print('Id: ',str(self.tracks[i].trackId),'   skipped_frames: ', str(self.tracks[i].skipped_frames))

		del_tracks = []
		for i in range(len(self.tracks)):
			if self.tracks[i].skipped_frames > self.max_frame_skipped :
				del_tracks.append(i)

		if len(del_tracks) > 0:
			for i in range(len(del_tracks)):
				print('Id: ',str(self.tracks[del_tracks[i]].trackId),'   skipped_frames: ', str(self.tracks[del_tracks[i]].skipped_frames))
				del self.tracks[del_tracks[i]]
				del assignment[del_tracks[i]]

		for i in range(len(detections)):
			if len(detections)>len(self.tracks) and len(self.tracks)<self.max_fish:
				if i not in assignment:
					track = Tracks(detections[i], self.trackId, detections[i])
					track.trace.append(track.correction)
					self.trackId +=1
					self.tracks.append(track)

		for i in range(len(assignment)):
			if(assignment[i] != -1):
				self.tracks[i].skipped_frames = 0
				self.tracks[i].correct(detections[assignment[i]])
				self.tracks[i].predict(detections[assignment[i]])
			else:
				self.tracks[i].correct(self.tracks[i].prediction)
				self.tracks[i].predict(self.tracks[i].prediction)
			self.tracks[i].trace.append(self.tracks[i].correction)


