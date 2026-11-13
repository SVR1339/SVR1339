import numpy as np
from PIL import Image
from scipy import ndimage

p_in = 'C:/Users/asus/.gemini/antigravity/brain/df77c114-ace1-49d7-85f6-4c78ab0ec581/.user_uploaded/media_1794611349604_0009e7ce.jpg'
p_out = 'C:/Users/asus/.gemini/antigravity/scratch/github-profile/assets/hero-bg.jpg'

im = Image.open(p_in).convert('RGB')
arr = np.array(im, dtype=np.float32)

# Text bounding box in original image
# x: 38..505, y: 70..205
roi = arr[68:208, 35:510]
lum = 0.299 * roi[:,:,0] + 0.587 * roi[:,:,1] + 0.114 * roi[:,:,2]

# Text is dark letters against bright sky
# In this ROI, sky luminance is > 175, letters are < 140
text_mask = lum < 142

# Dilate by 3 pixels to include all anti-aliased font edges
text_mask = ndimage.binary_dilation(text_mask, iterations=3)

# For each letter pixel, sample the local sky color by taking the median of clean pixels
clean_roi = roi.copy()

# Perform fast distance-weighted interpolation from the nearest non-text sky pixels
# using ndimage.distance_transform_edt
coords = ndimage.distance_transform_edt(text_mask, return_distances=False, return_indices=True)

# Replace text pixels with the exact nearest clean sky pixels
for c in range(3):
    channel = roi[:, :, c]
    channel[text_mask] = channel[coords[0][text_mask], coords[1][text_mask]]
    # Slight smooth blur only on the inpainted pixels
    blurred = ndimage.gaussian_filter(channel, sigma=1.8)
    channel[text_mask] = blurred[text_mask]
    roi[:, :, c] = channel

arr[68:208, 35:510] = roi

# Add matched grain
np.random.seed(42)
noise = np.random.normal(0, 0.8, (140, 475, 3))
arr[68:208, 35:510][text_mask] += noise[text_mask]

clean_arr = np.clip(arr, 0, 255).astype(np.uint8)
clean_im = Image.fromarray(clean_arr)
clean_im.save(p_out, quality=96)
print(f"✓ Local sky interpolation inpainting completed! Saved to {p_out}")
