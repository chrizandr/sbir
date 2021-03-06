"""Find shape context descriptor."""
import math
import numpy as np
import pdb

from scipy.spatial.distance import cdist
from skimage.io import imread
from settings import sample_points


def shape_context(points, nbins_r, nbins_theta, r_inner, r_outer, max_window_size, window=None):
    """Computes the Shape Context Feature Descriptor for the given input points."""
    nbins = nbins_theta * nbins_r
    t_points = points.shape[0]

    descriptor = []

    r_array = cdist(points, points)
    am = r_array.argmax()
    max_points = [am // t_points, am % t_points]
    r_array_n = r_array // r_array.mean()
    r_bin_edges = np.logspace(np.log10(r_inner), np.log10(r_outer), nbins_r)
    r_array_q = np.zeros((t_points, t_points), dtype=int)

    for m in range(nbins_r):
        r_array_q += (r_array_n < r_bin_edges[m])

    fz = r_array_q > 0

    theta_array = cdist(points, points, lambda u, v: math.atan2((v[1] - u[1]), (v[0] - u[0])))
    norm_angle = theta_array[max_points[0], max_points[1]]
    theta_array = (theta_array - norm_angle * (np.ones((t_points, t_points)) - np.identity(t_points)))
    theta_array[np.abs(theta_array) < 1e-7] = 0

    theta_array_2 = theta_array + 2 * math.pi * (theta_array < 0)
    theta_array_q = (1 + np.floor(theta_array_2 // (2 * math.pi / nbins_theta))).astype(int)

    for i in range(t_points):
        sn = np.zeros((nbins_r, nbins_theta))
        x, y = points[i]

        if window is not None:
            local_x = np.where((points[:, 0] >= (x-window)) & (points[:, 0] <= (x+window)))
            local_y = np.where((points[:, 0] >= y-window) & (points[:, 0] <= y+window))
            local_points = np.intersect1d(local_x, local_y)
            for j in local_points:
                if (fz[i, j]):
                    sn[r_array_q[i, j] - 1, theta_array_q[i, j] - 1] += 1
        else:
            for j in range(t_points):
                if (fz[i, j]):
                    sn[r_array_q[i, j] - 1, theta_array_q[i, j] - 1] += 1
        # There need not be 500 points in the image, you can have less than 500 also.
        descriptor.append(sn.reshape(nbins))

    return np.array(descriptor)


if __name__ == "__main__":
    # Image is already binary with Canny Edge detection done
    img = imread('test_edge.png', as_gray=True)
    edge_pixels = img.nonzero()
    indices = np.arange(len(edge_pixels[0]))

    try:
        samples = np.random.choice(indices, (sample_points), False)
    except ValueError:
        samples = indices

    points = np.array([[edge_pixels[0][i], edge_pixels[1][i]] for i in samples])
    descriptor = shape_context(points, window=5, max_window_size=5, nbins_r=5, nbins_theta=12, r_inner=0.1250, r_outer=2.0)
    pdb.set_trace()
