from typing import Tuple

import click
import numpy as np
import cv2
import noise
import webcolors
from scipy.interpolate import RectBivariateSpline

Color = list[int, int, int]
WeightedColor = list[Color, float]

def process_colors(colors: str) -> Tuple[np.ndarray, np.ndarray]:
    """
    Parses a string representation of colors and weights and returns
    arrays of colors and cumulative weights.
    
    Args:
        colors: A string of hex values and their corresponding weights,
                separated by commas and colons, e.g. "#D99AB7:0.2,#F2B950:0.3,#E3D2B5:0.5"
    
    Returns:
        color_array: An ndarray of shape (num_colors, 3) containing RGB colors
        cumulative_weights: An ndarray of shape (num_colors + 1,) containing the cumulative weights
    """
    # Parse the input string and create a list of colors and weights
    parsed = [c.split(":") for c in colors.split(",")]
    # Separate the colors and weights into two separate lists
    color_array, weights = zip(*parsed)
    color_array = np.array([webcolors.hex_to_rgb(c) for c in color_array], dtype=np.float32)
    weights = np.array(weights, dtype=np.float32)
    
    # Compute the cumulative sum of weights, ensuring the sum is 1
    cumulative_weights = np.cumsum(weights) / np.sum(weights)
    # Add a zero at the beginning of cumulative_weights
    cumulative_weights = np.hstack(([0], cumulative_weights))
    
    return color_array, cumulative_weights


def noise_to_color_array(noise: np.ndarray, color_array: np.ndarray, cumulative_weights: np.ndarray) -> np.ndarray:
    """
    Maps the noise values to colors based on the provided color_array and cumulative_weights.
    
    Args:
        noise: An ndarray of shape (height, width) containing noise values in the range [0, 1]
        color_array: An ndarray of shape (num_colors, 3) containing RGB colors
        cumulative_weights: An ndarray of shape (num_colors + 1,) containing the cumulative weights
    
    Returns:
        result: An ndarray of shape (height, width, 3) containing the noise values mapped to colors
    """
    num_colors = len(color_array)
    
    # Determine the color interval for each noise value by comparing it to the cumulative weights
    idx = np.sum((noise[..., np.newaxis] > cumulative_weights), axis=-1) - 1
    
    # Compute the weight of the noise value within the selected color interval
    t = (noise - cumulative_weights[idx]) / (cumulative_weights[idx + 1] - cumulative_weights[idx])
    # Add a new axis to t to allow for element-wise multiplication with the color array
    t = t[..., np.newaxis]
    
    # Linearly interpolate between the colors at the beginning and the end of the interval,
    # using np.mod(idx + 1, num_colors) instead of (idx + 1) % num_colors to make the list seamless
    result = (color_array[idx] * (1 - t) + color_array[np.mod(idx + 1, num_colors)] * t).astype(np.uint8)
    
    return result

def rescaled_noise(x, y, scale):
    noise_value = noise.snoise2(x * scale, y * scale)
    return (noise_value + 1) / 2

@click.command()
@click.option("--width", default=640, type=int, help="Video width")
@click.option("--height", default=480, type=int, help="Video height")
@click.option("--fps", default=60, type=int, help="Frames per second")
@click.option("--duration", default=10, type=int, help="Video duration in seconds")
@click.option("--noise_size_scale", default=0.0016, type=float, help="Scaling factor to determine the size (freqency) of the noise")
@click.option("--noise_time_scale", default=0.1, type=float, help="Scaling factor to determine how quickly we move through the noise space")
@click.option("--colors", default="#E3D2B5:2,#F2B950:5,#D99748:3,#D99AB7:5,#D98989:2", type=str, help="JSON list of CSS3 color names and weights")
@click.option("--scale-factor", default=1, type=int, help="Factor to scale the output by")
def main(width: int, height: int, fps: int, duration: int, noise_size_scale: float, noise_time_scale: float, colors: str, scale_factor: int) -> None:
    max_frames = fps * duration
    color_array, cumulative_weights = process_colors(colors)

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video_writer = cv2.VideoWriter('perlin_noise_color_space.mp4', fourcc, fps, (width, height), True)

    x_coords, y_coords = np.meshgrid(np.arange(width // scale_factor), np.arange(height // scale_factor))
    vectorized_noise = np.vectorize(rescaled_noise)

    for t in range(max_frames):
        print(t)
        small_frame = np.zeros((height // scale_factor, width // scale_factor, 3), dtype=np.uint8)

        # Calculate noisey_t_x and noisey_t_y for circular traversal
        angle = (2 * np.pi * t * noise_time_scale) / max_frames
        tx, ty = width * np.sin(angle), height * np.cos(angle)
        noisey_t_x = tx + vectorized_noise(tx, tx, noise_size_scale)
        noisey_t_y = ty + vectorized_noise(ty*2, ty*2, noise_size_scale)

        space_noise_1 = vectorized_noise(x_coords + noisey_t_x, y_coords + noisey_t_y, noise_size_scale)
        space_noise_2 = vectorized_noise(x_coords - noisey_t_x, y_coords - noisey_t_y, noise_size_scale)

        combined_noise = (space_noise_1 + space_noise_2 ) % 1

        small_frame = noise_to_color_array(combined_noise, color_array, cumulative_weights)
        
        # Upscale the small frame using linear interpolation
        x = np.arange(width // scale_factor)
        y = np.arange(height // scale_factor)
        x_new = np.linspace(0, width // scale_factor - 1, width)
        y_new = np.linspace(0, height // scale_factor - 1, height)
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        for i in range(3):
            interpolator = RectBivariateSpline(y, x, small_frame[..., i], kx=1, ky=1)
            frame[..., i] = interpolator(y_new, x_new)
        
        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)  # Convert the frame from RGB
        video_writer.write(frame_bgr)
    video_writer.release()

if __name__ == "__main__":
    main()