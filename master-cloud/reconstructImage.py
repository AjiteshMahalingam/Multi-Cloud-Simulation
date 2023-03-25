import numpy as np
import cv2
import os

TEMP_FOLDER = "./temp"

def modInv(a,p):          
  for i in range(1,p):
    if (i*a)%p==1:
      return i
  raise ValueError(str(a)+" has no inverse mod "+str(p))

def reconstruct_secret (I, shadows) : 
  x, y = I.shape
  s1 = shadows[0]
  s2 = shadows[1]
  s5 = shadows[2]

  for P in range(0, x, 5) :
    for Q in range(0, y, 5) :
      B = np.hstack((s1[P:P+5,(Q+4)//5].reshape((5, 1)), s2[P:P+5,(Q+4)//5].reshape((5, 1)), s5[P:P+5,(Q+4)//5].reshape((5, 1))))
      I_dash = np.mod(np.matmul(np.transpose(B), B), 251)
      adj = np.round(np.mod(np.multiply(np.linalg.inv(I_dash), np.linalg.det(I_dash)), 251))
      inverse = np.multiply(adj, modInv(np.mod(int(np.round(np.linalg.det(I_dash))), 251), 251))
      inverse = np.mod(inverse, 251)
      Proj_B = np.mod(np.matmul(np.matmul(B, inverse), np.transpose(B)), 251)
      I[P:P+5, Q:Q+5] = np.mod(np.add(I[P:P+5, Q:Q+5], Proj_B),251).astype(np.double)

  return I

def reconstruct_image (image_id, imgPath, shadows) :
  R_loaded = np.loadtxt(imgPath).astype(int)
  R_loaded = R_loaded.reshape(R_loaded.shape[0], R_loaded.shape[1] // 3, 3)

  b_channel, g_channel, r_channel = cv2.split(R_loaded)
  shadows_r = []
  shadows_b = []
  shadows_g = []

  for shadow in shadows :
    shadow_loaded = np.loadtxt(shadow).astype(int)
    shadow_loaded = shadow_loaded.reshape(shadow_loaded.shape[0], shadow_loaded.shape[1] // 3, 3)
    b, g, r = cv2.split(shadow_loaded)
    shadows_r.append(r)
    shadows_g.append(g)
    shadows_b.append(b)

  r = reconstruct_secret(r_channel, shadows_r)
  g = reconstruct_secret(g_channel, shadows_g)
  b = reconstruct_secret(b_channel, shadows_b)

  reconst = cv2.merge([r, g, b])[0:256, 0:256]
  cv2.imwrite("Reconst_img.jpg", reconst)

  reconst = reconst.reshape(reconst.shape[0], -1)
  filename = image_id + "_reconst.txt"
  filename = os.path.join(TEMP_FOLDER, filename)
  np.savetxt(filename, reconst)
  
  return filename