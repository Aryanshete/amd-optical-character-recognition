import os
import sys
import time
from typing import Tuple, Optional
from PIL import Image
import torch

STRICT_OCR_PROMPT = """Read all text visible in this image.
Return ONLY the characters that should be transcribed.
Do not describe the image.
Do not add explanations or labels.
Do not invent characters.

For license plates:
- Return the registration characters.
- Drop state names/slogans printed around the number.
- For Chinese plates, keep the province character and registration letter.

For signs:
- Return all printed words and numbers.
- Read multiple lines from top to bottom.
- Join lines with spaces.

Output only the transcription."""


class VLMEngine:
    _instance: Optional["VLMEngine"] = None

    def __init__(self, model_name_or_path: Optional[str] = None):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        default_model = "Qwen/Qwen2.5-VL-7B-Instruct"
        if os.path.exists("/models") and len(os.listdir("/models")) > 0:
            default_model = "/models"
        elif os.path.exists("./models") and len(os.listdir("./models")) > 0:
            default_model = "./models"
            
        self.model_path = model_name_or_path or os.getenv("OCR_MODEL_PATH", default_model)
        self.model = None
        self.processor = None
        self.loaded = False
        self._load_model()

    def _load_model(self):
        start_time = time.time()
        print(f"[VLM Engine] Initializing model from: {self.model_path} on {self.device}")
        
        try:
            from transformers import Qwen2_5_VLForConditionalGeneration, AutoProcessor
            
            if self.device == "cuda":
                torch_dtype = torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16
            else:
                torch_dtype = torch.float32

            print("[VLM Engine] Loading processor...")
            self.processor = AutoProcessor.from_pretrained(self.model_path, trust_remote_code=True)

            print(f"[VLM Engine] Loading model weights with dtype={torch_dtype}...")
            if self.device == "cuda":
                self.model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
                    self.model_path,
                    torch_dtype=torch_dtype,
                    device_map="auto",
                    trust_remote_code=True
                )
            else:
                self.model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
                    self.model_path,
                    torch_dtype=torch_dtype,
                    trust_remote_code=True
                ).to(self.device)

            self.model.eval()
            self.loaded = True
            elapsed = time.time() - start_time
            print(f"[VLM Engine] Model loaded in {elapsed:.2f}s.")
            
        except Exception as e:
            print(f"[VLM Engine] Note: Could not load HuggingFace VLM weights ({e}).", file=sys.stderr)
            print("[VLM Engine] Falling back to lightweight heuristic/OCR inference engine.", file=sys.stderr)
            self.loaded = False

    def predict(self, image: Image.Image) -> Tuple[str, float]:
        if not self.loaded:
            from ocr.fallback_engine import run_fallback_ocr
            return run_fallback_ocr(image)

        try:
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "image", "image": image},
                        {"type": "text", "text": STRICT_OCR_PROMPT}
                    ]
                }
            ]

            try:
                from qwen_vl_utils import process_vision_info
                text_prompt = self.processor.apply_chat_template(
                    messages, tokenize=False, add_generation_prompt=True
                )
                image_inputs, video_inputs = process_vision_info(messages)
                inputs = self.processor(
                    text=[text_prompt],
                    images=image_inputs,
                    videos=video_inputs,
                    padding=True,
                    return_tensors="pt"
                )
            except Exception:
                text_prompt = self.processor.apply_chat_template(
                    messages, tokenize=False, add_generation_prompt=True
                )
                inputs = self.processor(
                    text=[text_prompt],
                    images=[image],
                    return_tensors="pt"
                )

            inputs = inputs.to(self.device)

            with torch.no_grad():
                generated_ids = self.model.generate(
                    **inputs,
                    max_new_tokens=128,
                    do_sample=False,
                    temperature=None,
                    top_p=None
                )

            generated_ids_trimmed = [
                out_ids[len(in_ids):] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
            ]
            output_text = self.processor.batch_decode(
                generated_ids_trimmed,
                skip_special_tokens=True,
                clean_up_tokenization_spaces=False
            )[0]

            return output_text.strip(), 0.95

        except Exception as e:
            print(f"[VLM Engine] Error during VLM generation: {e}", file=sys.stderr)
            from ocr.fallback_engine import run_fallback_ocr
            return run_fallback_ocr(image)


def get_vlm_engine(model_name_or_path: Optional[str] = None) -> VLMEngine:
    if VLMEngine._instance is None:
        VLMEngine._instance = VLMEngine(model_name_or_path)
    return VLMEngine._instance
