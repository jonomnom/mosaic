from PIL import Image
import numpy as np
import os


def average_color(image):
    """Compute the average color of an image, always return RGB values."""
    arr = np.array(image)
    
    # If the image is grayscale (2D), convert it to 3D by duplicating the channel
    if len(arr.shape) == 2:  # Grayscale image
        arr = np.stack([arr] * 3, axis=-1)  # Convert grayscale to RGB
    
    # If the image has an alpha channel (RGBA), ignore the alpha channel
    if arr.shape[-1] == 4:  # RGBA image
        print("Warning: Ignoring alpha channel")
        assert False, "Image must be RGB"
    
    # Compute and return the average color (RGB)
    return np.mean(arr, axis=(0, 1))

def resize_image(image, size):
    """Resize image to a specified size."""
    return image.resize(size)

def closest_image(tile_colors, target_color):
    """Find the image whose average color is closest to the target color."""
    distances = np.sqrt(np.sum((tile_colors - target_color) ** 2, axis=1))
    return np.argmin(distances)

def create_mosaic(target_image_path, tile_image_dir, grid_size):
    """Create a photomosaic from a target image using a set of tile images."""
    
    # Load the target image and get its size
    print("Loading target image...")
    target_image = Image.open(target_image_path)
    target_width, target_height = target_image.size
    print(f"Target image loaded. Size: {target_width}x{target_height}")
    
    # Define the size of each cell in the grid
    cell_width = (target_width // grid_size[0])
    cell_height = (target_height // grid_size[1])
    print(f"Grid size: {grid_size[0]}x{grid_size[1]} (each cell is {cell_width}x{cell_height} pixels)")
    
    # Load tile images and compute their average colors
    print("Loading and processing tile images...")
    tile_images = []
    tile_colors = []
    
    for idx, file_name in enumerate(os.listdir(tile_image_dir)):
        tile_image_path = os.path.join(tile_image_dir, file_name)
        tile_image = Image.open(tile_image_path)
        
        # Resize tile image to fit the grid cell
        resized_tile = resize_image(tile_image, (cell_width, cell_height))
        try:
            tile_colors.append(average_color(resized_tile))
            tile_images.append(resized_tile)
        except Exception as e:
            print(f"Error converting {file_name} to RGB: {e}")
        
        if idx % 10 == 0:  # Print progress every 10 tiles
            print(f"Processed {idx + 1} tile images...")

    print(f"All {len(tile_images)} tile images loaded and processed.")
    for i in range(1000):
        print(tile_colors[i])
    tile_colors = np.array(tile_colors)
    
    # Create a new blank image for the mosaic
    mosaic_image = Image.new('RGB', (target_width, target_height))
    
    # Process each grid cell in the target image
    print("Starting to build the mosaic...")
    for i in range(grid_size[0]):
        for j in range(grid_size[1]):
            # Crop the current grid cell from the target image
            left = i * cell_width
            top = j * cell_height
            right = (i + 1) * cell_width
            bottom = (j + 1) * cell_height
            grid_cell = target_image.crop((left, top, right, bottom))
            
            # Compute the average color of the grid cell
            target_color = average_color(grid_cell)
            
            # Find the tile image with the closest average color
            tile_index = closest_image(tile_colors, target_color)
            best_tile = tile_images[tile_index]
            
            # Paste the best tile into the mosaic
            mosaic_image.paste(best_tile, (left, top))
        
        # Print progress every row
        print(f"Completed row {i + 1} of {grid_size[0]}")
    
    print("Mosaic creation complete.")
    return mosaic_image

# Example usage:
# target_image_path = 'path/to/target/image.jpg'
# tile_image_dir = 'path/to/tile/images/'
# grid_size = (50, 50)  # 50x50 grid cells
# mosaic_image = create_mosaic(target_image_path, tile_image_dir, grid_size)
# mosaic_image.show()  # To display the result
# mosaic_image.save('mosaic_output.jpg')  # To save the result


target_image_path = './in/02-inputs/mosaic-target.jpeg'
tile_image_dir = './out'
grid_size = (300, 400)  # 50x50 grid cells
mosaic_image = create_mosaic(target_image_path, tile_image_dir, grid_size)
# mosaic_image.show()  # To display the result
mosaic_image.resize((3000 * 5, 4000 * 5)).show()  # To display the result
mosaic_image.save('mosaic_output.jpg')  # To save the result
