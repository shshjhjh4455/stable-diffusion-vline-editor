import requests
from PIL import Image
import base64
import io
import dlib
import numpy as np
import cv2
import matplotlib.pyplot as plt

class VLineInpaintEditorSDXL:
    def __init__(self, api_key):
        self.api_key = api_key
        self.host = "https://api.stability.ai/v2beta/stable-image/edit/inpaint"
        
        # dlib 초기화는 마스크 생성을 위해 유지
        self.detector = dlib.get_frontal_face_detector()
        self.predictor = dlib.shape_predictor('shape_predictor_68_face_landmarks.dat')

    def image_to_base64(self, image):
        """PIL Image를 base64 문자열로 변환"""
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode()

    def create_jaw_mask(self, image, landmarks, v_strength=0.5):
        """턱선 마스크 생성 - 얼굴 크기에 비례하여 V라인 효과 강화"""
        if isinstance(image, Image.Image):
            image = np.array(image)
        
        if len(image.shape) == 2:
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
        elif image.shape[2] == 4:
            image = cv2.cvtColor(image, cv2.COLOR_RGBA2RGB)
            
        height, width = image.shape[:2]
        mask = np.zeros((height, width), dtype=np.uint8)
        
        # 턱선 포인트 추출 (2-15번이 실제 턱 부분)
        jaw_points = []
        for i in range(2, 15):
            point = landmarks.part(i)
            jaw_points.append([point.x, point.y])
        jaw_points = np.array(jaw_points)
        
        # 턱선 높이 계산 (얼굴 크기에 비례하는 기준)
        jaw_height = np.max(jaw_points[:, 1]) - np.min(jaw_points[:, 1])
        
        # 위아래 경계선을 얼굴 크기에 비례하여 설정
        top_offset = int(jaw_height * 0.15)  # 얼굴 높이의 15%를 위로 확장
        bottom_offset = int(jaw_height * 0.3)  # 얼굴 높이의 30%를 아래로 확장

        # 턱선 중심점 계산
        center_x = np.mean(jaw_points[:, 0])
        chin_idx = len(jaw_points) // 2
        chin_y = jaw_points[chin_idx, 1]
        
        # V라인 형태로 수정된 포인트 생성 (더 강한 변형)
        modified_points = jaw_points.copy()
        for i in range(len(jaw_points)):
            if i != chin_idx:  # 턱 끝점 제외
                dist_from_center = abs(i - chin_idx) / chin_idx
                vertical_factor = (jaw_points[i, 1] - np.min(jaw_points[:, 1])) / (np.max(jaw_points[:, 1]) - np.min(jaw_points[:, 1]))
                move_strength = v_strength * (1 - dist_from_center) * vertical_factor
                modified_points[i, 0] = jaw_points[i, 0] + (center_x - jaw_points[i, 0]) * move_strength
        
        # 마스크 포인트 생성
        mask_points = []
        
        # 위쪽 경계선 (블렌딩을 위해 얼굴 크기에 비례하여 조정)
        for point in jaw_points:
            mask_points.append([point[0], max(0, point[1] - top_offset)])
        
        # 아래쪽 경계선 (V라인 형태로 얼굴 크기에 비례하여 조정)
        for point in modified_points[::-1]:
            mask_points.append([point[0], min(height - 1, point[1] + bottom_offset)])
        
        # 마스크 생성
        mask_points = np.array(mask_points)
        cv2.fillPoly(mask, [mask_points.astype(np.int32)], 255)
        
        # 마스크 부드럽게 처리
        kernel_size = 11
        mask = cv2.GaussianBlur(mask, (kernel_size, kernel_size), 0)
        
        # 마스크 강화
        mask = cv2.threshold(mask, 127, 255, cv2.THRESH_BINARY)[1]
        
        return Image.fromarray(mask)

    def process_image(self, image_path, prompt="professional portrait photo with perfect v-line jawline", seed=123):
        original_image = Image.open(image_path).convert('RGB')
        image_np = np.array(original_image)
        
        # 얼굴 감지 및 마스크 생성
        gray = cv2.cvtColor(image_np, cv2.COLOR_RGB2GRAY)
        faces = self.detector(gray)
        if len(faces) == 0:
            raise ValueError("No face detected")
            
        landmarks = self.predictor(gray, faces[0])
        mask_image = self.create_jaw_mask(image_np, landmarks)
        
        # 마스크 이미지를 PNG 형식으로 저장
        mask_buffer = io.BytesIO()
        mask_image.save(mask_buffer, format="PNG")
        mask_buffer.seek(0)
        
        # API 요청 준비
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "image/*"
        }
        
        files = {
            "image": (image_path, open(image_path, "rb"), "image/png"),
            "mask": ("mask.png", mask_buffer, "image/png")
        }
        
        payload = {
            "prompt": prompt,
            "seed": seed,
            "mode": "mask",
        }
        
        # API 요청
        response = requests.post(self.host, headers=headers, files=files, data=payload)
        
        if response.status_code == 200:
            result_image = Image.open(io.BytesIO(response.content))
            
            # 결과 시각화
            plt.figure(figsize=(15, 5))
            plt.subplot(1, 3, 1)
            plt.imshow(original_image)
            plt.title("Original")
            plt.axis("off")
            
            plt.subplot(1, 3, 2)
            plt.imshow(mask_image, cmap='gray')
            plt.title("Mask")
            plt.axis("off")
            
            plt.subplot(1, 3, 3)
            plt.imshow(result_image)
            plt.title("Result")
            plt.axis("off")
            
            plt.show()
            
            return result_image
        else:
            raise Exception(f"API request failed with status {response.status_code}: {response.text}")

# 사용 예시
def apply_vline_sdxl(image_path, api_key):
    editor = VLineInpaintEditorSDXL(api_key)
    result = editor.process_image(
        image_path=image_path,
        prompt="professional portrait photo with perfect v-line jawline, sharp chin, same person",
    )
    return result

# 테스트 실행
api_key = ""
image_path = "face.jpg"
result_image = apply_vline_sdxl(image_path, api_key)
