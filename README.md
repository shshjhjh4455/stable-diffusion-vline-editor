
# V-Line Inpaint Editor with Stability AI API

This project leverages the Stability AI API for inpainting to create a V-line jaw effect on facial images. The main functionality includes detecting a face, generating a mask for the jawline, and applying an inpainting prompt to create a professional portrait with a sharp, V-line jaw effect. The solution dynamically adjusts mask boundaries based on facial proportions, ensuring the V-line effect appears natural across varying face shapes and sizes.

## Features

- **Dynamic Jaw Mask Creation**: Adjusts mask boundaries based on face size and jaw proportions.
- **Customizable V-Line Strength**: Offers control over the strength of the V-line effect.
- **Stability AI Inpainting Integration**: Utilizes the Stability AI API to apply image edits based on specified prompts.

## Table of Contents

1. [Installation](#installation)
2. [Usage](#usage)
3. [Core Logic Explained](#core-logic-explained)
4. [Example Output](#example-output)
5. [Acknowledgments](#acknowledgments)

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/your-username/vline-inpaint-editor.git
   cd vline-inpaint-editor
   ```

2. Install the required libraries:

   ```bash
   pip install -r requirements.txt
   ```

3. Download the `shape_predictor_68_face_landmarks.dat` file for dlib (available [here](http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2)) and place it in the project directory.

## Usage

1. Replace `YOUR_API_KEY` in the code with your Stability AI API key.

2. Run the example code to apply the V-line effect on an image:

   ```python
   from vline_inpaint import apply_vline_sdxl

   image_path = "path/to/your/image.jpg"
   api_key = "YOUR_API_KEY"

   result_image = apply_vline_sdxl(image_path, api_key)
   result_image.show()
   ```

## Core Logic Explained

### 1. Dynamic Jaw Mask Creation

The `create_jaw_mask` function dynamically generates a mask to accentuate the V-line effect. This function uses facial landmarks to identify and modify the jawline region. Key elements include:

- **Jawline Height Calculation**:
   - The code calculates the jawline height (`jaw_height`) based on the highest and lowest y-coordinates of jawline landmarks.
   - This measurement adapts the mask’s top and bottom boundaries in proportion to the face size.

- **Dynamic Offset Calculation**:
   - The mask’s upper boundary is offset by 15% of `jaw_height`, while the lower boundary is extended by 30%.
   - These proportional offsets prevent the mask from being too large on smaller faces or too small on larger faces, resulting in a natural jawline transition.

### 2. Center-Based Jawline Modification

The jawline points are moved toward the face center to enhance the V-line shape, based on the following calculations:

- **Center Distance and Vertical Factor**:
   - Each jaw point’s distance from the chin center is calculated to adjust the point's movement strength.
   - A vertical factor is applied based on the jawline's top-to-bottom range, ensuring points near the chin move more than those closer to the ears.

- **Dynamic V-Strength Application**:
   - A `v_strength` parameter defines the degree of movement for each jaw point toward the center.
   - By combining `v_strength` with the center distance and vertical factor, each point is naturally repositioned to create a balanced V-line effect across different face shapes.

### 3. Stability AI Inpainting

Using the generated mask, the Stability AI API applies the inpainting prompt to enhance the jawline. The mask image and prompt are sent to the API, which returns a modified image with the desired V-line jaw effect.

## Example Output

| Original Image | Mask | Result Image |
| --- | --- | --- |
| ![Original](example/original.jpg) | ![Mask](example/mask.jpg) | ![Result](example/result.jpg) |

## Acknowledgments

- **Stability AI**: For providing the powerful inpainting model used in this project.
- **dlib**: For the facial landmark detection model used to locate jawline points.
