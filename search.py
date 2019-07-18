import numpy as np

def divide(points, N):
    min = np.min(points)
    max = np.max(points)
    w = max - min
    ind = np.empty_like(points,dtype=np.int32)
    ind[:] = ((points - min)/w)*N
    return ind, min, max, w

def search(point, points, ind, low, w, N):
    pi = np.empty_like(point,dtype=np.int32)
    pi[:] = ((point - low)/w)*N
    
    found = False
    r = 1
    while not found:
        pix = np.array([min(max(0,p),N-1) for p in range(pi[0]-r,pi[0]+r+1)], dtype=np.int32)
        piy = np.array([min(max(0,p),N-1) for p in range(pi[1]-r,pi[1]+r+1)], dtype=np.int32)
        piz = np.array([min(max(0,p),N-1) for p in range(pi[2]-r,pi[2]+r+1)], dtype=np.int32)
        
        pidx = np.in1d(ind[:,0], pix)
        pidy = np.in1d(ind[:,1], piy)
        pidz = np.in1d(ind[:,2], piz)
        pids = np.logical_and(pidx,np.logical_and(pidy,pidz))
        
        diff = points[pids] - point
        dist = np.einsum('ij,ij->i', diff, diff)
        if len(dist):
            i = np.argmin(dist)
            id = np.flatnonzero(pids)[i]
            return points[id],id,dist[i],r
        r += 1

if __name__ == "__main__":

    from time import time
    
    PTS = 1000000
    points = np.random.random(3 * PTS)
    points.shape = -1,3
    
    N=100
    ind, lo, hi, w = divide(points,N)
    
    #for p,i in zip(points,ind):
    #    print(p,i)

    p = np.array([0.5,0.5,0.5])

    start = time()
    r = search(p, points, ind, lo, w, N)
    print(time()-start)
    print(p,r)

    start = time()
    diff = points - p
    dist = np.einsum('ij,ij->i', diff, diff)
    i = np.argmin(dist)
    print(time()-start)
    print(p, (points[i], i, dist[i]))
    
