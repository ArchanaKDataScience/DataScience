#from PIL import Image
#import numpy as np

#def generate_image(prompt):
 #   img = np.zeros((256, 256, 3), dtype=np.uint8)
  #  return Image.fromarray(img)

from diffusers import StableDiffusionPipeline
import torch

pipe = StableDiffusionPipeline.from_pretrained("runwayml/stable-diffusion-v1-5")
pipe = pipe.to("cuda" if torch.cuda.is_available() else "cpu")

def generate_image(prompt):
    image = pipe(prompt).images[0]
    return image

