# import numpy as np

# #https://www.researchgate.net/profile/Nawaf-Hazim/publication/301693492_Fingerprint_Recognition_Improvement_Using_Histogram_Equalization_and_Compression_Methods/links/5723049108ae262228a5f7c9/Fingerprint-Recognition-Improvement-Using-Histogram-Equalization-and-Compression-Methods.pdf?origin=publication_detail&_tp=eyJjb250ZXh0Ijp7ImZpcnN0UGFnZSI6InB1YmxpY2F0aW9uIiwicGFnZSI6InB1YmxpY2F0aW9uRG93bmxvYWQiLCJwcmV2aW91c1BhZ2UiOiJwdWJsaWNhdGlvbiJ9fQ&__cf_chl_tk=B8vlUmnVp2DVqW1IEHwk1LGhim_bGWy0f_utc8SboCs-1778571971-1.0.1.1-0jM3pxjzWLq.CrA.4kWrafoDHrzHlzex1lVgzM9yrdQ
# #https://www.researchgate.net/profile/Cristinel-Mares/publication/44262481_Image_Enhancement_for_Fingerprint_Minutiae-Based_Algorithms_Using_CLAHE_Standard_Deviation_Analysis_and_Sliding_Neighborhood/links/00b7d525bfdc7e33f5000000/Image-Enhancement-for-Fingerprint-Minutiae-Based-Algorithms-Using-CLAHE-Standard-Deviation-Analysis-and-Sliding-Neighborhood.pdf?origin=publication_detail&_tp=eyJjb250ZXh0Ijp7ImZpcnN0UGFnZSI6InB1YmxpY2F0aW9uIiwicGFnZSI6InB1YmxpY2F0aW9uRG93bmxvYWQiLCJwcmV2aW91c1BhZ2UiOiJwdWJsaWNhdGlvbiJ9fQ&__cf_chl_tk=WN6tPeiivNxaSe24LYgX6FWxGhPGvJ53F3_faZRcWtk-1778585172-1.0.1.1-rXhaTfkJnHunC3UTG1rD6yEl3MUefs08EUADvAol8DI
# #https://www.acsu.buffalo.edu/~tulyakov/papers/Wu_MCRCS06_ImageQuality.pdf
# def histogram_equalization(img):

#     h, w = img.shape
#     N = h * w

#     # 1. histogram n_k
#     n_k = np.zeros(256, dtype=np.int32)

#     for y in range(h):
#         for x in range(w):
#             n_k[img[y, x]] += 1

#     # 2. probability density p_r(r_k)
#     p_r = n_k / N

#     # 3. cumulative distribution function (CDF)
#     cdf = np.zeros(256, dtype=np.float32)
#     cdf[0] = p_r[0]

#     for k in range(1, 256):
#         cdf[k] = cdf[k - 1] + p_r[k]

#     # 4. normalization (mapping to [0,255])
#     s_k = np.round(255 * cdf).astype(np.uint8)

#     # 5. apply transform
#     out = np.zeros_like(img, dtype=np.uint8)

#     for y in range(h):
#         for x in range(w):
#             out[y, x] = s_k[img[y, x]]

#     return out


# def histogram_equalization_local(block):
#     """local HE for one tile"""

#     h, w = block.shape
#     N = h * w

#     hist = np.zeros(256, dtype=np.int32)

#     for y in range(h):
#         for x in range(w):
#             hist[block[y, x]] += 1

#     cdf = np.cumsum(hist) / N
#     lut = np.floor(255 * cdf).astype(np.uint8)

#     return lut[block]


# def clahe(img, tile_size=16, clip_limit=0.01):

#     img = img.astype(np.uint8)

#     h, w = img.shape

#     out = np.zeros_like(img, dtype=np.uint8)

#     # =========================
#     # number of tiles
#     # =========================
#     n_tiles_y = (h + tile_size - 1) // tile_size
#     n_tiles_x = (w + tile_size - 1) // tile_size

#     # each tile stores normalized CDF
#     tiles = np.zeros((n_tiles_y, n_tiles_x, 256), dtype=np.float32)

#     # ==========================================================
#     # 1. HISTOGRAM + CLIPPING + NORMALIZED CDF
#     # ==========================================================
#     for ty in range(n_tiles_y):
#         for tx in range(n_tiles_x):

#             y0 = ty * tile_size
#             x0 = tx * tile_size

#             block = img[y0:y0 + tile_size, x0:x0 + tile_size]

#             # =========================
#             # histogram
#             # =========================
#             hist = np.zeros(256, dtype=np.float32)

#             bh, bw = block.shape

#             for y in range(bh):
#                 for x in range(bw):
#                     hist[block[y, x]] += 1

#             # =========================
#             # CLAHE clipping
#             # =========================
#             max_clip = clip_limit * block.size

#             excess = np.sum(np.maximum(hist - max_clip, 0))

#             hist = np.minimum(hist, max_clip)

#             # redistribute clipped pixels
#             hist += excess / 256.0

#             # =========================
#             # normalized CDF
#             # =========================
#             cdf = hist.cumsum()

#             if cdf[-1] != 0:
#                 cdf = cdf / cdf[-1]

#             tiles[ty, tx] = cdf

#     # ==========================================================
#     # 2. BILINEAR INTERPOLATION
#     # ==========================================================
#     for y in range(h):
#         for x in range(w):

#             ty = y // tile_size
#             tx = x // tile_size

#             # neighboring tiles
#             ty1 = min(ty + 1, n_tiles_y - 1)
#             tx1 = min(tx + 1, n_tiles_x - 1)

#             # interpolation weights
#             fy = (y % tile_size) / tile_size
#             fx = (x % tile_size) / tile_size

#             pixel = img[y, x]

#             cdf00 = tiles[ty, tx][pixel]
#             cdf01 = tiles[ty, tx1][pixel]
#             cdf10 = tiles[ty1, tx][pixel]
#             cdf11 = tiles[ty1, tx1][pixel]

#             # bilinear interpolation
#             top = (1 - fx) * cdf00 + fx * cdf01
#             bottom = (1 - fx) * cdf10 + fx * cdf11

#             value = (1 - fy) * top + fy * bottom

#             out[y, x] = int(np.clip(value * 255, 0, 255))

#     return out