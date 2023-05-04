from typing import Tuple

import click
import numpy as np
import cv2
import noise
import webcolors

from line_profiler import LineProfiler

Color = list[int, int, int]
WeightedColor = list[Color, float]

@profile
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


@profile
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
@click.option("--noise_scale", default=0.0033, type=float, help="Perlin noise scale")
@click.option("--colors", default="#E3D2B5:2,#F2B950:5,#D99748:3,#D99AB7:5,#D989/url89:2", type=str, help="JSON list of CSS3 color names and weights")
@profile
def main(width: int, height: int, fps: int, duration: int, noise_scale: float, colors: str) -> None:
    max_frames = fps * duration
    color_array, cumulative_weights = process_colors(colors)

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video_writer = cv2.VideoWriter('perlin_noise_color_space.mp4', fourcc, fps, (width, height), True)

    x_coords, y_coords = np.meshgrid(np.arange(width), np.arange(height))
    vectorized_noise = np.vectorize(rescaled_noise)

    for t in range(max_frames):
        print(t)

        frame = np.zeros((height, width, 3), dtype=np.uint8)
        noisey_t_x = t + vectorized_noise(t, t, noise_scale * 10)
        noisey_t_y = t + vectorized_noise(t*2, t*2, noise_scale * 10)
        space_noise_1 = vectorized_noise(x_coords + noisey_t_x, y_coords + noisey_t_y, noise_scale)
        space_noise_2 = vectorized_noise(x_coords - noisey_t_x, y_coords - noisey_t_y, noise_scale)

        combined_noise = (space_noise_1 + space_noise_2 ) % 1

        frame = noise_to_color_array(combined_noise, color_array, cumulative_weights) 
        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)  # Convert the frame from RGB
        video_writer.write(frame_bgr)
    video_writer.release()

if __name__ == "__main__":
    main()
